from typing import Any

from zai import ZhipuAiClient

from src.config import Config
from src.model import AssetData


class AssetAnalyzer:
    SEARCH_QUERY_ASSET_LIMIT = 8
    SEARCH_QUERY_KEYWORDS = ("市场分析", "财经新闻", "市场走势", "投资策略")

    def __init__(self, config: Config):
        self.config = config
        self.client = None

        if config.zai_api_key:
            try:
                self.client = ZhipuAiClient(api_key=config.zai_api_key)
            except Exception as exc:
                print(f"初始化 ZhipuAiClient 失败: {exc}")

    def _format_data_for_analysis(self, data: list[AssetData]) -> str:
        lines = []
        for item in data:
            if item.error:
                lines.append(
                    f"- {item.name}({item.symbol}): 数据获取失败 - {item.error}"
                )
            else:
                change_str = ""
                if item.change is not None and item.change_percent is not None:
                    change_str = f", 涨跌: {item.change:+.2f} ({item.change_percent:+.2f}%)"

                price_str = (
                    f"{item.current_price:.2f}"
                    if item.current_price is not None
                    else "N/A"
                )
                lines.append(
                    f"- {item.name}({item.symbol}): 当前价格 {price_str}{change_str}"
                )

        return "\n".join(lines)

    def _generate_search_query(self, data: list[AssetData]) -> str:
        unique_asset_names: list[str] = []
        seen: set[str] = set()

        for asset in data:
            if asset.error:
                continue
            clean_name = asset.name.strip()
            if not clean_name or clean_name in seen:
                continue
            seen.add(clean_name)
            unique_asset_names.append(clean_name)
            if len(unique_asset_names) >= self.SEARCH_QUERY_ASSET_LIMIT:
                break

        return " ".join(unique_asset_names + list(self.SEARCH_QUERY_KEYWORDS))

    def analyze_with_ai(self, data: list[AssetData]) -> str:
        if not self.client:
            return "AI分析不可用：未配置API密钥或zai-sdk未安装"

        data_summary = self._format_data_for_analysis(data)
        search_query = self._generate_search_query(data)
        prompt = self.config.analysis_prompt.format(
            data_summary=data_summary,
            search_query=search_query
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=[{"role": "user", "content": prompt}],
                tools=[
                    {
                        "type": "web_search",
                        "web_search": {
                            "enable": True,
                            "search_query": search_query,
                            "search_result": True,
                        }
                    }
                ],
            )
            
            message = response.choices[0].message
            return message.content or "AI分析返回空内容"
        except Exception as e:
            return f"AI分析失败: {str(e)}"

    def _group_assets_by_change(
        self, data: list[AssetData]
    ) -> tuple[list[AssetData], list[AssetData], list[AssetData], list[AssetData]]:
        error_assets = [a for a in data if a.error]
        valid_assets = [a for a in data if not a.error and a.change_percent is not None]
        up_assets = [a for a in valid_assets if a.change_percent > 0]
        down_assets = [a for a in valid_assets if a.change_percent < 0]
        flat_assets = [a for a in valid_assets if a.change_percent == 0]
        return up_assets, down_assets, flat_assets, error_assets

    def _append_assets_section(
        self,
        lines: list[str],
        title: str,
        assets: list[AssetData],
        *,
        reverse: bool = False,
        prefix_plus: bool = False,
    ) -> None:
        if not assets:
            return
        lines.append(title)
        for item in sorted(assets, key=lambda a: a.change_percent or 0, reverse=reverse):
            lines.append(f"- {item.name}: {'+' if prefix_plus else ''}{item.change_percent:.2f}%")
        lines.append("")

    def analyze_basic(self, data: list[AssetData]) -> str:
        lines = ["## 基础分析\n"]

        up_assets, down_assets, flat_assets, error_assets = self._group_assets_by_change(
            data
        )

        lines.append(f"### 涨跌统计")
        lines.append(f"- 上涨资产: {len(up_assets)} 个")
        lines.append(f"- 下跌资产: {len(down_assets)} 个")
        lines.append(f"- 持平资产: {len(flat_assets)} 个")
        lines.append(f"- 获取失败: {len(error_assets)} 个\n")

        self._append_assets_section(
            lines, "### 上涨资产", up_assets, reverse=True, prefix_plus=True
        )
        self._append_assets_section(lines, "### 下跌资产", down_assets)

        return "\n".join(lines)

    def analyze(self, data: list[AssetData], use_ai: bool = False) -> dict[str, Any]:
        result = {
            "basic_analysis": self.analyze_basic(data),
            "ai_analysis": None,
        }

        if use_ai and self.client:
            result["ai_analysis"] = self.analyze_with_ai(data)

        return result

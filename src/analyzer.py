from typing import Any

from zai import ZhipuAiClient

from src.config import Config
from src.data_fetcher import AssetData


class AssetAnalyzer:
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

    def analyze_with_ai(self, data: list[AssetData]) -> str:
        if not self.client:
            return "AI分析不可用：未配置API密钥或zai-sdk未安装"

        data_summary = self._format_data_for_analysis(data)
        prompt = self.config.analysis_prompt.format(data_summary=data_summary)

        try:
            response = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI分析失败: {str(e)}"

    def analyze_basic(self, data: list[AssetData]) -> str:
        lines = ["## 基础分析\n"]

        up_assets = [
            d for d in data if d.change_percent is not None and d.change_percent > 0
        ]
        down_assets = [
            d for d in data if d.change_percent is not None and d.change_percent < 0
        ]
        flat_assets = [
            d for d in data if d.change_percent is not None and d.change_percent == 0
        ]
        error_assets = [d for d in data if d.error]

        lines.append(f"### 涨跌统计")
        lines.append(f"- 上涨资产: {len(up_assets)} 个")
        lines.append(f"- 下跌资产: {len(down_assets)} 个")
        lines.append(f"- 持平资产: {len(flat_assets)} 个")
        lines.append(f"- 获取失败: {len(error_assets)} 个\n")

        if up_assets:
            lines.append("### 上涨资产")
            up_assets.sort(key=lambda x: x.change_percent or 0, reverse=True)
            for item in up_assets:
                lines.append(
                    f"- {item.name}: +{item.change_percent:.2f}%"
                )
            lines.append("")

        if down_assets:
            lines.append("### 下跌资产")
            down_assets.sort(key=lambda x: x.change_percent or 0)
            for item in down_assets:
                lines.append(
                    f"- {item.name}: {item.change_percent:.2f}%"
                )
            lines.append("")

        return "\n".join(lines)

    def analyze(self, data: list[AssetData], use_ai: bool = False) -> dict[str, Any]:
        result = {
            "basic_analysis": self.analyze_basic(data),
            "ai_analysis": None,
        }

        if use_ai and self.client:
            result["ai_analysis"] = self.analyze_with_ai(data)

        return result

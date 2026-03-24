from datetime import datetime
from pathlib import Path


CATEGORY_NAMES = {
    "us_stocks": "美股",
    "precious_metals": "贵金属",
    "crypto": "数字货币",
    "cn_stocks": "A股",
    "forex": "汇率",
    "commodities": "大宗商品",
    "bonds": "债券",
}


def _render_overview(data_list: list) -> list[str]:
    lines: list[str] = []
    current_category = None

    for item in data_list:
        if item.category != current_category:
            current_category = item.category
            display_name = CATEGORY_NAMES.get(current_category, current_category)
            lines.append(f"### {display_name}")
            lines.append("")

        if item.error:
            lines.append(f"- **{item.name}** ({item.symbol}): 数据获取失败")
            continue

        price_str = f"{item.current_price:.2f}" if item.current_price is not None else "N/A"
        change_str = ""
        if item.change is not None and item.change_percent is not None:
            change_str = f" | 涨跌: {item.change:+.2f} ({item.change_percent:+.2f}%)"
        lines.append(f"- **{item.name}** ({item.symbol}): {price_str}{change_str}")

    return lines


def render_markdown_report(data_list: list, analysis_result: dict, use_ai: bool = False) -> str:
    lines = [
        "# 资产分析报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 数据概览",
        "",
    ]

    lines.extend(_render_overview(data_list))
    lines.append("")
    lines.append(analysis_result.get("basic_analysis", ""))

    if use_ai and analysis_result.get("ai_analysis"):
        lines.append("")
        lines.append("## AI 分析")
        lines.append("")
        lines.append(analysis_result["ai_analysis"])

    return "\n".join(lines)


def write_report(content: str, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def generate_report(
    data_list: list,
    analysis_result: dict,
    output_dir: str | Path,
    use_ai: bool = False,
) -> Path:
    content = render_markdown_report(
        data_list=data_list, analysis_result=analysis_result, use_ai=use_ai
    )
    return write_report(content=content, output_dir=output_dir)

from datetime import datetime
from pathlib import Path


def generate_report(
    data_list: list,
    analysis_result: dict,
    output_dir: Path,
    use_ai: bool = False,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now()
    filename = f"analysis_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    output_path = output_dir / filename
    
    lines = [
        f"# 资产分析报告",
        f"",
        f"**生成时间**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        "## 数据概览",
        "",
    ]
    
    current_category = None
    for item in data_list:
        if item.category != current_category:
            current_category = item.category
            category_names = {
                "us_stocks": "美股",
                "precious_metals": "贵金属",
                "crypto": "数字货币",
                "cn_stocks": "A股",
                "forex": "汇率",
                "commodities": "大宗商品",
                "bonds": "债券",
            }
            lines.append(f"### {category_names.get(current_category, current_category)}")
            lines.append("")
        
        if item.error:
            lines.append(f"- **{item.name}** ({item.symbol}): 数据获取失败")
        else:
            price_str = f"{item.current_price:.2f}" if item.current_price else "N/A"
            change_str = ""
            if item.change is not None and item.change_percent is not None:
                change_str = f" | 涨跌: {item.change:+.2f} ({item.change_percent:+.2f}%)"
            lines.append(f"- **{item.name}** ({item.symbol}): {price_str}{change_str}")
    
    lines.append("")
    lines.append(analysis_result.get("basic_analysis", ""))
    
    if use_ai and analysis_result.get("ai_analysis"):
        lines.append("")
        lines.append("## AI 分析")
        lines.append("")
        lines.append(analysis_result["ai_analysis"])
    
    content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path

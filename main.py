import argparse
from pathlib import Path

from src.analyzer import AssetAnalyzer
from src.config import Config
from src.data_fetcher import AssetDataFetcher
from src.model import AssetData
from src.reporter import generate_report
from src.utils import log_step


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="资产数据分析工具")
    parser.add_argument(
        "-a", "--use-ai",
        action="store_true",
        help="使用AI分析（需要配置ZAI_API_KEY）",
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="配置文件路径（默认使用config.yaml）",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出目录路径（默认使用output/）",
    )
    return parser.parse_args()


def summarize_fetch_result(data_list: list[AssetData]) -> tuple[int, int]:
    success_count = sum(1 for d in data_list if not d.error)
    error_count = sum(1 for d in data_list if d.error)
    return success_count, error_count


def run_pipeline(args: argparse.Namespace) -> str:
    log_step("开始资产数据分析...")

    config = Config(config_path=args.config)
    use_ai = args.use_ai or config.use_ai

    log_step("加载配置完成")
    log_step(f"AI分析: {'启用' if use_ai else '禁用'}")

    fetcher = AssetDataFetcher()
    log_step("开始拉取资产数据...")

    assets = config.all_assets
    data_list = fetcher.fetch_all(assets)

    success_count, error_count = summarize_fetch_result(data_list)
    log_step(f"数据拉取完成: 成功 {success_count}, 失败 {error_count}")

    analyzer = AssetAnalyzer(config=config)
    log_step("开始分析数据...")

    analysis_result = analyzer.analyze(data_list, use_ai=use_ai)

    output_dir = Path(args.output) if args.output else config.output_dir
    report_path = generate_report(
        data_list=data_list,
        analysis_result=analysis_result,
        category_names=config.category_names,
        output_dir=output_dir,
        use_ai=use_ai,
    )

    log_step(f"分析完成！报告已保存至: {report_path}")

    return str(report_path)


def main() -> str:
    args = parse_args()
    return run_pipeline(args)


if __name__ == "__main__":
    main()

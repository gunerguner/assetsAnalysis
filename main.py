import argparse
from datetime import datetime

from src.analyzer import AssetAnalyzer
from src.config import Config
from src.data_fetcher import AssetDataFetcher
from src.utils import generate_report


def main():
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
    
    args = parser.parse_args()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始资产数据分析...")
    
    config = Config(config_path=args.config)
    
    use_ai = args.use_ai or config.use_ai
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 加载配置完成")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AI分析: {'启用' if use_ai else '禁用'}")
    
    fetcher = AssetDataFetcher()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始拉取资产数据...")
    
    assets = config.all_assets
    data_list = fetcher.fetch_all(assets)
    
    success_count = sum(1 for d in data_list if not d.error)
    error_count = sum(1 for d in data_list if d.error)
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据拉取完成: "
        f"成功 {success_count}, 失败 {error_count}"
    )
    
    analyzer = AssetAnalyzer(config=config)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始分析数据...")
    
    analysis_result = analyzer.analyze(data_list, use_ai=use_ai)
    
    output_dir = args.output if args.output else config.output_dir
    report_path = generate_report(
        data_list=data_list,
        analysis_result=analysis_result,
        output_dir=output_dir,
        use_ai=use_ai,
    )
    
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 分析完成！"
        f"报告已保存至: {report_path}"
    )
    
    return str(report_path)


if __name__ == "__main__":
    main()

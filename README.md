# 资产数据分析工具

一个自动化资产数据分析工具，支持美股、A股、贵金属、加密货币、外汇、大宗商品和债券等多种资产类别的数据获取与分析。

## 功能特性

- 📊 **多资产类别支持**
  - 美股指数：道琼斯、标普500、纳斯达克
  - A股指数：上证指数、沪深300、创业板
  - 贵金属：黄金、白银
  - 加密货币：比特币、以太坊
  - 外汇：美元指数、美元/人民币
  - 大宗商品：WTI原油
  - 债券：美债10年

- 🤖 **AI智能分析**（可选）
  - 集成智谱AI进行深度分析
  - 自动生成市场洞察和投资建议

- 📝 **自动报告生成**
  - Markdown格式报告
  - 包含价格、涨跌幅等关键指标

- ⏰ **自动化运行**
  - GitHub Actions每周五美股收盘后自动执行
  - 支持手动触发

## 安装

### 前置要求

- Python 3.12+

### 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 1. 配置资产列表

编辑 `config.yaml` 文件，自定义需要分析的资产：

```yaml
assets:
  us_stocks:
    - symbol: "^DJI"
      name: "道琼斯"
  crypto:
    - symbol: "BTC-USD"
      name: "比特币"
```

### 2. 配置AI分析（可选）

复制 `.env.example` 为 `.env` 并填入API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
ZAI_API_KEY=your_api_key_here
AI_MODEL=your_model_here
```

## 使用方法

### 基础使用

```bash
python main.py
```

### 启用AI分析

```bash
python main.py -a
```

### 指定输出目录

```bash
python main.py -o /path/to/output
```

### 指定配置文件

```bash
python main.py -c /path/to/config.yaml
```

### 完整示例

```bash
python main.py -a -o ./reports -c ./my_config.yaml
```

## 命令行参数

| 参数 | 简写 | 说明 |
|------|------|------|
| `--use-ai` | `-a` | 启用AI分析（需要配置ZAI_API_KEY） |
| `--config` | `-c` | 指定配置文件路径（默认使用config.yaml） |
| `--output` | `-o` | 指定输出目录路径（默认使用output/） |

## GitHub Actions 自动化

项目配置了GitHub Actions工作流，每周五美股收盘后（UTC 22:30）自动运行分析，并将报告提交到 `data` 分支。

### 手动触发工作流

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Daily Asset Analysis" 工作流
3. 点击 "Run workflow"
4. 选择是否启用AI分析

### 工作流配置

工作流配置文件：`.github/workflows/daily_analysis.yml`

- 执行时间：每周五 UTC 22:30
- 报告存储：`data/YYYY/MM/YYYY-MM-DD.md`
- 分支：data

## 项目结构

```
assetsAnalysis/
├── .github/
│   └── workflows/
│       └── daily_analysis.yml    # GitHub Actions配置
├── src/
│   ├── __init__.py
│   ├── analyzer.py               # 分析器
│   ├── config.py                 # 配置管理
│   ├── data_fetcher.py           # 数据获取
│   └── utils.py                  # 工具函数
├── output/                       # 默认输出目录
├── .env.example                  # 环境变量示例
├── .gitignore
├── config.yaml                   # 资产配置
├── main.py                       # 主程序入口
├── prompts.yaml                  # AI提示词配置
└── requirements.txt              # Python依赖
```

## 依赖项

- `yfinance>=0.2.0` - 金融数据获取
- `pyyaml>=6.0` - YAML配置解析
- `python-dotenv>=1.0.0` - 环境变量管理
- `zai-sdk>=0.1.0` - 智谱AI SDK

## 输出示例

分析报告会生成Markdown格式的文件，包含：

- 各资产当前价格
- 涨跌幅统计
- AI分析结果（如果启用）
- 市场趋势总结

## 注意事项

1. 数据来源于Yahoo Finance，可能存在延迟或错误
2. AI分析功能需要有效的API密钥
3. 建议在美股交易时间后运行以获取最新数据
4. GitHub Actions运行时间可能因网络情况有所波动

## 许可证

MIT License

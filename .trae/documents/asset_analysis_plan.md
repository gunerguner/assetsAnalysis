# 资产分析项目实施计划

## 项目概述

开发一个 Python 项目，用于拉取多种资产的实时数据，并可选使用 AI 分析涨跌情况及背后原因。

## 项目结构

```
assetsAnalysis/
├── .env                    # 环境变量配置（API密钥等）
├── .env.example            # 环境变量示例
├── config.yaml             # 资产配置文件
├── requirements.txt        # Python依赖
├── main.py                 # 主入口文件
├── src/
│   ├── __init__.py
│   ├── config.py           # 配置加载模块
│   ├── data_fetcher.py     # 数据拉取模块
│   ├── analyzer.py         # AI分析模块
│   └── utils.py            # 工具函数
├── output/                 # 输出目录
│   └── .gitkeep
└── .github/
    └── workflows/
        └── daily_analysis.yml  # GitHub Action工作流
```

## 实施步骤

### 第一步：项目初始化

1. 创建 Python 虚拟环境 (.venv)
2. 创建 requirements.txt，包含依赖：

   * yfinance（数据拉取）

   * pyyaml（配置文件解析）

   * python-dotenv（环境变量加载）

   * zai-sdk（AI分析，可选）

   * pandas（数据处理）
3. 创建基础目录结构

### 第二步：配置模块 (src/config.py)

1. 创建 config.yaml 配置文件，定义资产列表：

   * 美股：^DJI（道琼斯）、^GSPC（标普500）、^IXIC（纳斯达克）

   * 黄金白银：GC=F（黄金）、SI=F（白银）

   * 数字货币：BTC-USD、ETH-USD

   * A股：000001.SS（上证）、000300.SS（沪深300）、399006.SZ（创业板）

   * 汇率：DX-Y.NYB（美元指数）、CNY=X（美元/人民币）

   * 原油：CL=F（WTI原油）

   * 债券：^TNX（美债10年）
2. 创建 .env 和 .env.example 文件
3. 实现 Config 类加载配置

### 第三步：数据拉取模块 (src/data\_fetcher.py)

1. 实现 AssetDataFetcher 类
2. 使用 yfinance 拉取实时数据
3. 计算涨跌幅、涨跌额等指标
4. 支持批量拉取和单个拉取
5. 错误处理和重试机制

### 第四步：AI分析模块 (src/analyzer.py)

1. 实现 AssetAnalyzer 类
2. 集成 zai-sdk（可选，通过参数控制）
3. 分析资产涨跌情况
4. 生成涨跌原因分析报告
5. 支持不使用 AI 时的基础分析

### 第五步：主入口 (main.py)

1. 解析命令行参数
2. 加载配置
3. 拉取数据
4. 执行分析（可选AI）
5. 生成报告并保存到 output/ 目录

### 第六步：GitHub Action 配置

1. 创建 .github/workflows/daily\_analysis.yml
2. 配置定时任务：美股收盘后执行（北京时间凌晨5点，即美东时间下午4点后）
3. 执行数据拉取和分析
4. 将结果提交到 analysis-results 分支

### 第七步：测试验证

1. 本地测试数据拉取功能
2. 测试 AI 分析功能
3. 验证 GitHub Action 工作流

## 配置说明

### config.yaml 示例

```yaml
assets:
  us_stocks:
    - symbol: "^DJI"
      name: "道琼斯"
    - symbol: "^GSPC"
      name: "标普500"
    - symbol: "^IXIC"
      name: "纳斯达克"
  precious_metals:
    - symbol: "GC=F"
      name: "黄金"
    - symbol: "SI=F"
      name: "白银"
  crypto:
    - symbol: "BTC-USD"
      name: "比特币"
    - symbol: "ETH-USD"
      name: "以太坊"
  cn_stocks:
    - symbol: "000001.SS"
      name: "上证指数"
    - symbol: "000300.SS"
      name: "沪深300"
    - symbol: "399006.SZ"
      name: "创业板"
  forex:
    - symbol: "DX-Y.NYB"
      name: "美元指数"
    - symbol: "CNY=X"
      name: "美元/人民币"
  commodities:
    - symbol: "CL=F"
      name: "WTI原油"
  bonds:
    - symbol: "^TNX"
      name: "美债10年"

analysis:
  use_ai: false  # 是否使用AI分析
  output_format: "markdown"  # 输出格式
```

### .env 示例

```
ZAI_API_KEY=your_api_key_here
```

## 输出格式

生成的报告将保存为 Markdown 格式，包含：

* 数据拉取时间

* 各资产实时价格

* 涨跌幅/涨跌额

* AI分析结果（如果启用）


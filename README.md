# Graphrager

Graphrager 是一个基于网页内容自动生成知识图谱的工具，它能够从给定的 URL 中提取实体和关系，并以可视化的方式展示知识网络。

## 功能特点

- 🌐 支持从任意 URL 提取知识图谱
- 🔍 智能识别页面类型和结构
- 🤖 集成本地大模型进行内容理解
- 📊 交互式知识图谱可视化
- 💬 基于知识图谱的智能对话

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- Ollama（用于本地大模型部署）

### 安装步骤

1. 克隆项目
```bash
git clone [your-repository-url]
cd Graphrager
```

2. 安装后端依赖
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

### 运行应用

1. 启动后端服务
```bash
python backend/app.py
```

2. 在浏览器中访问
```
http://localhost:5000
```

## 项目结构

```
Graphrager/
├── backend/             # 后端代码
│   ├── app.py          # Flask 应用主文件
│   └── modules/        # 功能模块
├── frontend/           # 前端代码
├── docs/              # 项目文档
└── tests/             # 测试代码
```

## API 文档

详细的 API 文档请参考 [API.md](docs/API.md)

## 开发指南

开发相关信息请参考：
- [技术选型说明](docs/技术选型说明.md)
- [实现步骤说明](docs/实现步骤说明文档.md)
- [开发过程记录](docs/开发过程记录.md)
- [开发环境配置](docs/开发环境配置.md)

## 许可证

[MIT License](LICENSE)

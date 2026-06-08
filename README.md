# AI Developer Copilot 🤖

面向开发者的智能助手，提供知识库问答、代码分析、报错诊断、学习笔记生成等功能。

## 功能特性

### 1. 💬 智能聊天
- 基于 Agent 的智能对话
- 多轮对话记忆
- 自动选择工具

### 2. 📚 智能知识库
- 支持 PDF/Word/Markdown/Text 格式
- 多知识库管理
- 引用来源显示
- 向量搜索

### 3. 🔍 代码仓库分析
- 支持 ZIP 项目上传
- GitHub 仓库克隆分析
- 自动识别技术栈
- 生成项目架构图
- README 智能解读

### 4. 🚨 报错诊断助手
- 自动检测报错类型（Python/Java/前端）
- 分析原因并提供解决方案
- 生成修复代码

### 5. 📝 学习笔记生成
- 从教程自动生成学习笔记
- 生成面试题和答案
- 知识体系总结
- 学习路线规划

### 6. 📋 对话记忆系统
- 多会话管理
- 历史会话保存
- 上下文理解

## 技术栈

- **框架**: LangChain, LangGraph
- **向量存储**: FAISS, ChromaDB
- **大模型**: DeepSeek
- **前端**: Streamlit
- **文档加载**: PyPDF, python-docx
- **其他**: GitPython

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_EMBEDDING_MODEL=text-embedding-v3
```

### 3. 运行应用

```bash
streamlit run app.py
```

## 项目结构

```
ai-developer-copilot/
├── modules/
│   ├── __init__.py
│   ├── knowledge_base.py      # 知识库模块
│   ├── code_analyzer.py       # 代码分析模块
│   ├── error_diagnosis.py     # 报错诊断模块
│   ├── note_generator.py      # 学习笔记模块
│   ├── conversation_memory.py # 对话记忆模块
│   └── agent_system.py        # Agent系统
├── knowledge_bases/          # 知识库数据
├── conversation_history/     # 对话历史
├── temp_uploads/             # 临时文件
├── app.py                    # 主界面
├── pyproject.toml            # 依赖配置
└── README.md                 # 项目说明
```

## 使用说明

### 知识库使用

1. 点击"创建知识库"新建一个知识库
2. 选择知识库后，上传文档
3. 在"知识库问答"中提问

### 代码分析使用

1. 选择"上传ZIP项目"或"GitHub仓库"
2. 上传文件或输入仓库URL
3. 点击"分析项目"获取结果

### 报错诊断使用

1. 粘贴报错信息
2. 可选地提供相关代码
3. 点击"诊断报错"获取解决方案

### 学习笔记生成

1. 上传教程文件
2. 点击"生成学习资料"
3. 查看并导出笔记

## 升级说明

本项目是从原 RAG 知识库问答系统升级而来：
- 保留原有知识库功能
- 新增 5 大核心模块
- 集成 LangGraph Agent
- 使用 FAISS 优化向量存储

## 开发计划

- [ ] 支持更多文档格式
- [ ] 代码对比功能
- [ ] 更多 Agent 工具
- [ ] 数据库持久化
- [ ] 用户权限管理

## 许可证

MIT License

# Ollama 安装和配置指南

## 1. 安装 Ollama

1. 访问 [Ollama 官方网站](https://ollama.ai/download) 下载 Windows 版本的安装包
2. 运行安装程序，按照提示完成安装

## 2. 下载模型

我们可以使用以下命令下载模型：

```bash
# 下载 Mistral 模型（推荐，平衡性能和资源消耗）
ollama pull mistral

# 或者其他可选模型
# ollama pull llama2    # Meta的LLaMA2模型
# ollama pull codellama # 专注于代码的LLaMA变体
# ollama pull gemma     # Google的Gemma模型
```

## 3. 验证安装

安装完成后，可以通过以下步骤验证：

1. 打开命令行终端
2. 运行基本测试：
```bash
ollama run mistral "Hello, how are you?"
```

## 4. API 调用示例

Ollama 提供了 REST API，我们可以通过以下方式调用：

```python
import requests

def query_ollama(prompt, model="mistral"):
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               "model": model,
                               "prompt": prompt
                           })
    return response.json()

# 测试调用
result = query_ollama("分析这个网页的类型")
print(result)
```

## 5. 系统要求

- 最低 8GB RAM（推荐 16GB 或更多）
- 支持 AVX2 指令集的 CPU
- 至少 5GB 可用磁盘空间（因模型大小而异）

## 6. 注意事项

1. 首次下载模型可能需要较长时间，取决于网络状况和模型大小
2. 确保系统防火墙不会阻止 Ollama 的网络访问
3. API 默认在本地 11434 端口运行

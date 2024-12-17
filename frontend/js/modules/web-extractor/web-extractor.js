// 网页数据提取模块
export class WebExtractor {
    constructor() {
        this.statusElement = document.getElementById('extraction-status');
        this.contentPreviewElement = document.getElementById('content-preview');
        this.promptPreviewElement = document.getElementById('prompt-preview');
        
        // 默认提示词模板
        this.defaultPrompt = `我将给你一段文本内容，请你帮我：
1. 识别出文本中的重要实体（人物、组织、地点、概念等）
2. 分析这些实体之间的关系
3. 用JSON格式返回，格式如下：
{
    "nodes": [
        {"id": "实体1", "label": "实体1", "type": "实体类型"},
        {"id": "实体2", "label": "实体2", "type": "实体类型"}
    ],
    "edges": [
        {"from": "实体1", "to": "实体2", "label": "关系描述"}
    ]
}

以下是需要分析的文本内容：`;
    }

    // 验证URL格式
    validateUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    // 显示提取状态
    updateStatus(message, isError = false, isLoading = false) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
            this.statusElement.className = 'status ' + 
                (isError ? 'status-error' : isLoading ? 'status-loading' : 'status-success');
        }
    }

    // 显示内容预览
    showContentPreview(content) {
        if (this.contentPreviewElement) {
            this.contentPreviewElement.textContent = content;
        }
        
        // 同时更新提示词预览
        this.updatePromptPreview(content);
    }

    // 更新提示词预览
    updatePromptPreview(content) {
        if (this.promptPreviewElement) {
            const promptPreview = this.defaultPrompt + '\n"""\n' + content + '\n"""';
            this.promptPreviewElement.textContent = promptPreview;
        }
    }

    // 提取网页内容
    async extractContent(url) {
        try {
            if (!this.validateUrl(url)) {
                throw new Error('无效的URL格式');
            }

            this.updateStatus('正在提取内容...', false, true);
            console.log('发送请求到后端:', url);

            const response = await fetch('http://localhost:5000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            console.log('收到响应:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('响应错误:', errorData);
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('响应数据:', data);

            if (!data || !data.content) {
                console.error('响应数据无效:', data);
                throw new Error('服务器返回的数据无效');
            }

            // 显示提取的内容预览和提示词预览
            this.showContentPreview(data.content);
            this.updateStatus('内容提取成功');

            return data;

        } catch (error) {
            console.error('提取内容失败:', error);
            this.updateStatus(error.message, true);
            throw error;
        }
    }
}

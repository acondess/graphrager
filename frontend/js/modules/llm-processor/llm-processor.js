// 大模型提示词处理模块
export class LLMProcessor {
    constructor() {
        this.processingStatusElement = document.getElementById('processing-status');
        this.promptInputElement = document.getElementById('prompt-input');
        this.promptPreviewElement = document.getElementById('prompt-preview');
    }

    // 更新处理状态
    updateStatus(message, isError = false, isLoading = false) {
        if (this.processingStatusElement) {
            this.processingStatusElement.textContent = message;
            this.processingStatusElement.className = 'status ' + 
                (isError ? 'status-error' : isLoading ? 'status-loading' : 'status-success');
        }
    }

    // 获取提示词
    getPrompt() {
        // 首先尝试获取用户自定义提示词
        const customPrompt = this.promptInputElement ? this.promptInputElement.value.trim() : '';
        
        // 如果没有自定义提示词，则使用预览中的默认提示词
        if (!customPrompt && this.promptPreviewElement) {
            return this.promptPreviewElement.textContent;
        }
        
        return customPrompt;
    }

    // 获取用户自定义提示词
    getCustomPrompt() {
        return this.promptInputElement ? this.promptInputElement.value : '';
    }

    // 处理提取的文本
    async processContent(content) {
        try {
            this.updateStatus('正在处理内容...', false, true);
            console.log('开始处理内容，长度:', content.length); // 添加调试日志

            const prompt = this.getPrompt();
            console.log('使用提示词:', prompt); // 添加调试日志
            
            const response = await fetch('http://localhost:5000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    prompt
                })
            });

            console.log('收到响应:', response.status); // 添加调试日志

            if (!response.ok) {
                const errorData = await response.json();
                console.error('响应错误:', errorData); // 添加错误日志
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('响应数据:', data); // 添加调试日志

            if (!data || !data.data) {
                console.error('响应数据无效:', data); // 添加错误日志
                throw new Error('服务器返回的数据无效');
            }

            this.updateStatus('内容处理成功');
            return data;

        } catch (error) {
            console.error('处理内容失败:', error); // 添加错误日志
            this.updateStatus(error.message, true);
            throw error;
        }
    }

    // 显示处理日志
    showProcessingLogs(logs) {
        const logsContainer = document.getElementById('processing-logs');
        if (logsContainer && logs) {
            logsContainer.innerHTML = logs.map(log => `
                <div class="log-entry ${log.level.toLowerCase()}">
                    <span class="timestamp">${new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
                    <span class="message">${log.message}</span>
                </div>
            `).join('');
            logsContainer.classList.add('show');
        }
    }
}

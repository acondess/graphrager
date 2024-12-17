let currentNetwork = null;
let currentGraphData = null;

// 显示处理状态
function showStatus(message, type = 'processing') {
    const status = document.getElementById('processing-status');
    if (status) {
        status.textContent = message;
        status.className = type;
    }
}

// 显示加载状态
function showLoading(show) {
    const status = document.getElementById('processing-status');
    if (status) {
        status.textContent = show ? '处理中...' : '';
    }
}

// 显示错误信息
function showError(message) {
    const status = document.getElementById('processing-status');
    if (status) {
        status.innerHTML = message ? `<span style="color: red">${message}</span>` : '';
    }
}

// 初始化模型选择器
async function initializeModelSelector() {
    showStatus('正在加载模型列表...');
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        const selector = document.getElementById('model-selector');
        selector.innerHTML = '';
        
        if (data.models && data.models.length > 0) {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name;
                selector.appendChild(option);
            });
            showStatus('模型列表加载完成', 'success');
        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = '无可用模型';
            selector.appendChild(option);
            showStatus('未找到可用模型', 'error');
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        showStatus('加载模型列表失败', 'error');
    }
}

// 设置按钮状态
function setButtonState(buttonId, enabled) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = !enabled;
    }
}

// 初始化图谱
function initializeGraph(container, data) {
    try {
        // 清空之前的图谱
        container.innerHTML = '';
        
        const graphData = {
            nodes: new vis.DataSet(data.nodes),
            edges: new vis.DataSet(data.edges)
        };
        
        const options = {
            nodes: {
                shape: 'dot',
                size: 20,
                font: {
                    size: 14,
                    color: '#333'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                shadow: true,
                font: {
                    size: 12,
                    align: 'middle'
                },
                arrows: 'to',
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: true,
                barnesHut: {
                    gravitationalConstant: -80000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            }
        };

        currentNetwork = new vis.Network(container, graphData, options);
    } catch (error) {
        console.error('Failed to initialize graph:', error);
        showError('初始化图谱失败');
    }
}

// 提取网页内容
document.getElementById('extract-btn').addEventListener('click', async () => {
    const url = document.getElementById('url-input').value.trim();
    
    if (!url) {
        showError('请输入URL');
        return;
    }
    
    showStatus('正在提取网页内容...');
    setButtonState('extract-btn', false);
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        });
        
        const data = await response.json();
        showStatus('内容提取成功', 'success');
        
        if (data.error) {
            showStatus('内容提取失败: ' + data.error, 'error');
            return;
        }
        
        // 显示提取的内容
        document.getElementById('extracted-content').value = data.content;
        
        // 如果提示词为空，设置默认提示词
        if (!document.getElementById('prompt-input').value.trim()) {
            document.getElementById('prompt-input').value = defaultPrompt;
        }
        
        // 构建完整的提示词和内容
        const fullPrompt = document.getElementById('prompt-input').value.replace('{text}', data.content);
        document.getElementById('content-input').value = fullPrompt;
        
    } catch (error) {
        showStatus('内容提取失败: ' + error.message, 'error');
        console.error('Extraction failed:', error);
    } finally {
        setButtonState('extract-btn', true);
    }
});

// 生成结构化内容
document.getElementById('structure-btn').addEventListener('click', async () => {
    const content = document.getElementById('content-input').value.trim();
    const prompt = document.getElementById('prompt-input').value.trim();
    const model = document.getElementById('model-selector').value;
    
    if (!content) {
        showError('请输入要处理的内容');
        return;
    }
    
    if (!model) {
        showError('请选择一个模型');
        return;
    }
    
    showStatus('正在生成结构化内容...');
    setButtonState('structure-btn', false);
    
    try {
        const response = await fetch('/api/structure', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                prompt: prompt,
                model: model
            }),
        });
        
        const data = await response.json();
        showStatus('结构化内容生成成功', 'success');
        
        if (data.error) {
            showStatus('结构化内容生成失败: ' + data.error, 'error');
            return;
        }
        
        // 显示生成的结构化内容和原始输出
        document.getElementById('structured-content').value = data.raw_output;
        
        try {
            // 尝试解析JSON并填充到图谱输入框
            const jsonData = JSON.parse(data.raw_output);
            document.getElementById('graph-input').value = JSON.stringify(jsonData, null, 2);
        } catch (error) {
            console.warn('Raw output is not valid JSON:', error);
            document.getElementById('graph-input').value = data.raw_output;
        }
        
    } catch (error) {
        showStatus('结构化内容生成失败: ' + error.message, 'error');
        console.error('Structure generation failed:', error);
    } finally {
        setButtonState('structure-btn', true);
    }
});

// 全局变量和配置
const API_BASE = '/api'; // API基础路径
let selectedModel = '';
const defaultPrompt = `你是一个专业的知识图谱生成助手。请分析以下文本内容，提取关键实体和它们之间的关系，并生成一个知识图谱的JSON数据结构。

要求：
1. 仔细分析文本中的关键概念、人物、事件等实体
2. 识别这些实体之间的关系
3. 将实体和关系组织成图结构
4. 返回严格的JSON格式数据，包含nodes和edges两个数组
5. 每个node必须包含id、label和type字段
6. 每个edge必须包含source、target和label字段
7. 确保source和target的值与节点的id对应
8. 不要生成任何JSON之外的文本

文本内容：
{text}

请直接返回JSON数据，示例格式：
{
    "nodes": [
        {"id": "1", "label": "实体1", "type": "person"},
        {"id": "2", "label": "实体2", "type": "concept"}
    ],
    "edges": [
        {"source": "1", "target": "2", "label": "关系描述"}
    ]
}`;

// 生成图谱
document.getElementById('generate-btn').addEventListener('click', () => {
    const jsonStr = document.getElementById('graph-input').value.trim();
    
    if (!jsonStr) {
        showError('请输入JSON数据');
        return;
    }
    
    setButtonState('generate-btn', false);
    try {
        const graphData = JSON.parse(jsonStr);
        if (!graphData.nodes || !graphData.edges) {
            showStatus('无效的图谱数据格式', 'error');
            return;
        }
        
        // 初始化图谱
        initializeGraph(document.getElementById('graph-container'), graphData);
        showStatus('图谱生成成功', 'success');
        
    } catch (error) {
        showStatus('图谱生成失败: ' + error.message, 'error');
        console.error('Graph generation failed:', error);
    } finally {
        setButtonState('generate-btn', true);
    }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeModelSelector();
    
    // 如果提示词为空，设置默认提示词
    if (!document.getElementById('prompt-input').value.trim()) {
        document.getElementById('prompt-input').value = defaultPrompt;
    }
    
    // 构建完整的提示词和内容
    const fullPrompt = document.getElementById('prompt-input').value.replace('{text}', document.getElementById('content-input').value);
    document.getElementById('content-input').value = fullPrompt;
});

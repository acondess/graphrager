let currentNetwork = null;

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (message) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        errorElement.style.display = 'none';
    }
}

function showNodeDetails(params) {
    if (params.nodes && params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = currentNetwork.body.data.nodes.get(nodeId);
        
        const detailsElement = document.getElementById('node-details');
        const contentElement = document.getElementById('node-details-content');
        
        contentElement.innerHTML = `
            <p><strong>ID:</strong> ${node.id}</p>
            <p><strong>Type:</strong> ${node.type || 'N/A'}</p>
            <p><strong>Name:</strong> ${node.label}</p>
            <p><strong>Description:</strong> ${node.description || 'N/A'}</p>
        `;
        
        detailsElement.style.display = 'block';
    }
}

function initializeGraph(container, data, options) {
    // 清空之前的图谱
    container.innerHTML = '';
    
    // 创建新的图谱实例
    currentNetwork = new vis.Network(container, data, options);
    
    // 添加节点点击事件
    currentNetwork.on('click', showNodeDetails);
}

// 缩放控制
document.getElementById('zoom-in').addEventListener('click', () => {
    if (currentNetwork) {
        currentNetwork.moveTo({
            scale: currentNetwork.getScale() * 1.2
        });
    }
});

document.getElementById('zoom-out').addEventListener('click', () => {
    if (currentNetwork) {
        currentNetwork.moveTo({
            scale: currentNetwork.getScale() * 0.8
        });
    }
});

document.getElementById('zoom-fit').addEventListener('click', () => {
    if (currentNetwork) {
        currentNetwork.fit();
    }
});

// 清除按钮
document.getElementById('clear-btn').addEventListener('click', () => {
    document.getElementById('url-input').value = '';
    document.getElementById('graph-visualization').innerHTML = '';
    document.getElementById('graph-details').innerHTML = '';
    document.getElementById('node-details').style.display = 'none';
    showError(null);
    currentNetwork = null;
});

// 生成图谱
document.getElementById('generate-btn').addEventListener('click', function() {
    const url = document.getElementById('url-input').value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    showLoading(true);
    showError(null);
    
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        if (!data.graph_data || !data.graph_data.entities || !data.graph_data.entities.length) {
            showError('No entities found on the page');
            return;
        }
        
        // 准备 vis.js 数据
        const nodes = new vis.DataSet(
            data.graph_data.entities.map(entity => ({
                id: entity.id,
                label: entity.name,
                type: entity.type,
                description: entity.description,
                color: getNodeColor(entity.type)
            }))
        );

        const edges = new vis.DataSet(
            data.graph_data.relations.map((rel, index) => ({
                id: `e${index}`,
                from: rel.source,
                to: rel.target,
                label: rel.type,
                title: rel.description || rel.type,
                arrows: 'to',
                color: { color: '#999' }
            }))
        );

        const networkData = { nodes, edges };
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

        // 初始化图谱
        initializeGraph(document.getElementById('graph-visualization'), networkData, options);
        
        // 显示详细信息
        const graphDetails = document.getElementById('graph-details');
        graphDetails.innerHTML = `
            <h3>Graph Details</h3>
            <ul>
                <li>Page Type: ${data.page_type.type}</li>
                <li>Confidence: ${(data.page_type.confidence * 100).toFixed(1)}%</li>
                <li>Features: ${data.page_type.features.join(', ')}</li>
                <li>Total Entities: ${data.graph_data.entities.length}</li>
                <li>Total Relations: ${data.graph_data.relations.length}</li>
                <li>Processing Time: ${data.processing_time.toFixed(2)} seconds</li>
            </ul>
            <h3>Entity Types:</h3>
            <ul>
                ${Array.from(new Set(data.graph_data.entities.map(e => e.type))).map(type => `
                    <li>
                        <span style="color: ${getNodeColor(type)}">●</span>
                        ${type}: ${data.graph_data.entities.filter(e => e.type === type).length} entities
                    </li>
                `).join('')}
            </ul>
        `;
        
        // 显示日志
        displayLogs(data.logs);
    })
    .catch(error => {
        showLoading(false);
        showError('Failed to generate knowledge graph: ' + error.message);
        console.error('Error:', error);
    });
});

// 根据实体类型返回颜色
function getNodeColor(type) {
    const colors = {
        'concept': '#4CAF50',
        'category': '#2196F3',
        'person': '#9C27B0',
        'org': '#F44336',
        'default': '#607D8B'
    };
    return colors[type] || colors.default;
}

function displayPrompts(logs) {
    // 创建或获取提示词容器
    const promptsContainer = document.getElementById('prompts-container');
    if (!promptsContainer) {
        const container = document.createElement('div');
        container.id = 'prompts-container';
        container.style.maxHeight = '400px';
        container.style.overflow = 'auto';
        container.style.marginTop = '20px';
        container.style.padding = '10px';
        container.style.backgroundColor = '#f8f9fa';
        container.style.border = '1px solid #dee2e6';
        container.style.borderRadius = '4px';
        container.style.fontFamily = 'monospace';
        document.body.appendChild(container);
    }

    const promptsDiv = document.getElementById('prompts-container');
    promptsDiv.innerHTML = '<h3>LLM Prompts:</h3>';

    if (logs && logs.length > 0) {
        const promptsList = document.createElement('div');
        
        // 过滤并显示提示词相关的日志
        logs.forEach(log => {
            if (log.message.includes('Prompt sent to LLM:') || 
                log.message.includes('System prompt:')) {
                const promptDiv = document.createElement('div');
                promptDiv.style.marginBottom = '15px';
                
                // 分割消息以获取提示词内容
                const parts = log.message.split('\n');
                const title = parts[0];
                const content = parts.slice(2, -2).join('\n');
                
                // 创建标题
                const titleElem = document.createElement('div');
                titleElem.style.fontWeight = 'bold';
                titleElem.style.marginBottom = '5px';
                titleElem.style.color = '#0066cc';
                titleElem.textContent = title;
                
                // 创建内容
                const contentElem = document.createElement('pre');
                contentElem.style.whiteSpace = 'pre-wrap';
                contentElem.style.wordWrap = 'break-word';
                contentElem.style.backgroundColor = '#ffffff';
                contentElem.style.padding = '10px';
                contentElem.style.border = '1px solid #e9ecef';
                contentElem.style.borderRadius = '4px';
                contentElem.style.fontSize = '14px';
                contentElem.textContent = content;
                
                promptDiv.appendChild(titleElem);
                promptDiv.appendChild(contentElem);
                promptsList.appendChild(promptDiv);
            }
        });
        
        promptsDiv.appendChild(promptsList);
    } else {
        promptsDiv.innerHTML += '<p>No prompts available.</p>';
    }
}

function displayLogs(logs) {
    const logsContainer = document.getElementById('logs-container');
    if (!logsContainer) {
        const container = document.createElement('div');
        container.id = 'logs-container';
        container.style.maxHeight = '500px';  
        container.style.overflow = 'auto';
        container.style.marginTop = '20px';
        container.style.padding = '10px';
        container.style.backgroundColor = '#f8f9fa';
        container.style.border = '1px solid #dee2e6';
        container.style.borderRadius = '4px';
        container.style.fontFamily = 'monospace';
        document.body.appendChild(container);
    }
    
    const logsDiv = document.getElementById('logs-container');
    logsDiv.innerHTML = '<h3>处理步骤和日志:</h3>';
    
    if (logs && logs.length > 0) {
        const logsList = document.createElement('ul');
        logsList.style.listStyle = 'none';
        logsList.style.padding = '0';
        
        logs.forEach(log => {
            const logItem = document.createElement('li');
            const timestamp = new Date(log.timestamp * 1000).toLocaleTimeString();
            
            if (log.level === 'STEP') {
                logItem.innerHTML = `
                    <div class="step-container" style="margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #007bff; border-radius: 4px;">
                        <div style="font-weight: bold; color: #007bff;">${timestamp}</div>
                        <pre style="margin: 5px 0; white-space: pre-wrap; word-wrap: break-word;">${log.message}</pre>
                    </div>
                `;
            } else {
                logItem.innerHTML = `
                    <div style="margin: 5px 0;">
                        <span style="color: ${getLogLevelColor(log.level)}">[${log.level}]</span>
                        <span style="color: #666;">${timestamp}:</span>
                        <span>${log.message}</span>
                    </div>
                `;
            }
            
            logsList.appendChild(logItem);
        });
        
        logsDiv.appendChild(logsList);
    } else {
        logsDiv.innerHTML += '<p>暂无日志信息</p>';
    }
}

function getLogLevelColor(level) {
    switch (level.toUpperCase()) {
        case 'ERROR': return '#dc3545';
        case 'WARNING': return '#ffc107';
        case 'INFO': return '#17a2b8';
        case 'STEP': return '#007bff';
        default: return '#6c757d';
    }
}

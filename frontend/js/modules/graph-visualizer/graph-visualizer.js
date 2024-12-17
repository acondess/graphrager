// 知识图谱可视化模块
export class GraphVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.network = null;
        this.data = null;
        this.options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 12,
                    face: 'Arial'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                font: {
                    size: 12,
                    align: 'middle'
                },
                arrows: {
                    to: { enabled: true, scaleFactor: 1 }
                }
            },
            physics: {
                stabilization: false,
                barnesHut: {
                    gravitationalConstant: -80000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true
            }
        };
    }

    // 初始化图谱
    initialize() {
        if (!this.container) {
            console.error('Graph container not found');
            return;
        }

        // 创建控制按钮
        this.createControls();
    }

    // 创建图谱控制按钮
    createControls() {
        const controls = document.createElement('div');
        controls.className = 'graph-controls';
        
        controls.innerHTML = `
            <button onclick="graphVisualizer.zoomIn()">+</button>
            <button onclick="graphVisualizer.zoomOut()">-</button>
            <button onclick="graphVisualizer.fitGraph()">Fit</button>
            <button onclick="graphVisualizer.exportGraph()">Export</button>
        `;

        this.container.parentNode.insertBefore(controls, this.container);
    }

    // 渲染图谱
    renderGraph(graphData) {
        this.data = graphData;

        // 创建数据集
        const nodes = new vis.DataSet(graphData.nodes);
        const edges = new vis.DataSet(graphData.edges);

        // 创建网络图
        this.network = new vis.Network(this.container, {
            nodes: nodes,
            edges: edges
        }, this.options);

        // 添加事件监听
        this.addEventListeners();
    }

    // 添加事件监听器
    addEventListeners() {
        if (!this.network) return;

        // 节点点击事件
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                this.showNodeDetails(nodeId);
            }
        });

        // 稳定状态事件
        this.network.on('stabilized', () => {
            console.log('Graph stabilized');
        });
    }

    // 显示节点详情
    showNodeDetails(nodeId) {
        const node = this.data.nodes.find(n => n.id === nodeId);
        if (!node) return;

        const detailsContainer = document.getElementById('node-details');
        if (detailsContainer) {
            detailsContainer.innerHTML = `
                <h3>Node Details</h3>
                <p><strong>ID:</strong> ${node.id}</p>
                <p><strong>Label:</strong> ${node.label}</p>
                ${node.properties ? `
                    <h4>Properties:</h4>
                    <ul>
                        ${Object.entries(node.properties).map(([key, value]) => `
                            <li><strong>${key}:</strong> ${value}</li>
                        `).join('')}
                    </ul>
                ` : ''}
            `;
            detailsContainer.style.display = 'block';
        }
    }

    // 缩放控制
    zoomIn() {
        if (this.network) {
            const scale = this.network.getScale() * 1.2;
            this.network.moveTo({ scale: scale });
        }
    }

    zoomOut() {
        if (this.network) {
            const scale = this.network.getScale() / 1.2;
            this.network.moveTo({ scale: scale });
        }
    }

    fitGraph() {
        if (this.network) {
            this.network.fit();
        }
    }

    // 导出图谱
    async exportGraph() {
        try {
            const response = await fetch('http://localhost:5000/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: this.data,
                    format: 'json'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // 创建下载链接
            const blob = new Blob([result.data], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'knowledge-graph.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export graph: ' + error.message);
        }
    }
}

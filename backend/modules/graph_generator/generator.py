import json
from typing import Dict, List
import logging

class GraphGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def format_graph_data(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """格式化图谱数据为前端可用格式"""
        try:
            # 确保节点ID唯一
            unique_nodes = {}
            for node in nodes:
                if node['id'] not in unique_nodes:
                    unique_nodes[node['id']] = {
                        'id': node['id'],
                        'label': node.get('label', node['id']),
                        'group': node.get('group', 'default')
                    }

            # 处理边
            formatted_edges = []
            for i, edge in enumerate(edges):
                if edge['source'] in unique_nodes and edge['target'] in unique_nodes:
                    formatted_edges.append({
                        'id': f'e{i}',  # 添加唯一ID
                        'from': edge['source'],
                        'to': edge['target'],
                        'label': edge.get('type', edge.get('label', '')),  # 优先使用type字段
                        'arrows': 'to',
                        'color': {'color': '#999'}  # 添加边的颜色
                    })

            return {
                'nodes': list(unique_nodes.values()),
                'edges': formatted_edges
            }
        except Exception as e:
            self.logger.error(f"Data formatting failed: {str(e)}")
            return {'nodes': [], 'edges': []}

    def apply_layout(self, graph_data: Dict) -> Dict:
        """应用图谱布局算法"""
        # 这里可以添加自定义布局算法
        # 目前返回原始数据，实际布局将在前端处理
        return graph_data

    def generate_graph(self, data: Dict) -> Dict:
        """生成最终的图谱数据"""
        try:
            # 格式化数据
            formatted_data = self.format_graph_data(
                data.get('nodes', []),
                data.get('edges', [])
            )
            
            # 应用布局
            graph_with_layout = self.apply_layout(formatted_data)
            
            return {
                'data': graph_with_layout,
                'status': 'success'
            }
        except Exception as e:
            self.logger.error(f"Graph generation failed: {str(e)}")
            return {
                'data': {'nodes': [], 'edges': []},
                'status': 'error',
                'error': str(e)
            }

    def export_graph(self, graph_data: Dict, format: str = 'json') -> Dict:
        """导出图谱数据"""
        try:
            if format == 'json':
                return {
                    'data': json.dumps(graph_data, ensure_ascii=False, indent=2),
                    'format': 'json',
                    'status': 'success'
                }
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            return {
                'data': None,
                'status': 'error',
                'error': str(e)
            }

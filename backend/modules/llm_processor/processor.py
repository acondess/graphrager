import requests
import json
import logging
from typing import List, Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, host: str = "http://localhost:11434"):
        """初始化LLM处理器"""
        self.host = host
        self.default_model = "llama3:latest"  # 使用已安装的模型
        
    def get_models(self) -> List[Dict[str, Any]]:
        """获取可用的模型列表"""
        try:
            response = requests.get(f"{self.host}/api/tags")
            response.raise_for_status()
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type.lower():
                logger.error(f"Unexpected content type: {content_type}")
                logger.error(f"Response text: {response.text[:200]}")  # 只记录前200个字符
                raise ValueError(f"服务器返回了非JSON响应: {content_type}")
            
            # 解析响应
            data = response.json()
            if not isinstance(data, list):
                raise ValueError("Invalid response format from Ollama API")
                
            # 提取模型信息
            models = []
            for model in data:
                if isinstance(model, dict) and 'name' in model:
                    models.append({
                        'name': model['name'],
                        'modified_at': model.get('modified_at', ''),
                        'size': model.get('size', 0)
                    })
            
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch models: {str(e)}")
            raise Exception(f"无法连接到Ollama服务: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
            raise Exception(f"获取模型列表失败: {str(e)}")
            
    def process(self, model: str, prompt: str, content: str) -> str:
        """处理内容并生成结构化输出"""
        try:
            # 准备请求数据
            system_prompt = "你是一个专业的知识图谱生成助手。请严格按照要求生成JSON格式的输出。"
            full_prompt = f"{system_prompt}\n\n{prompt.replace('{text}', content)}"
            
            data = {
                "model": model or self.default_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            logger.info(f"Sending request to Ollama API with model: {model or self.default_model}")
            
            # 发送请求到Ollama，不设置超时
            response = requests.post(
                f"{self.host}/api/generate",  # 使用 generate API 端点
                json=data
            )
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            logger.info(f"Response content type: {content_type}")
            logger.info(f"Response status code: {response.status_code}")
            
            if 'application/json' not in content_type.lower():
                logger.error(f"Unexpected content type: {content_type}")
                logger.error(f"Response text: {response.text[:200]}")  # 只记录前200个字符
                raise ValueError(f"服务器返回了非JSON响应: {content_type}")
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if 'response' not in result:
                logger.error(f"Invalid response format: {json.dumps(result, indent=2)}")
                raise ValueError("Ollama API返回了无效的响应格式")
                
            # 尝试解析生成的内容为JSON
            generated_text = result['response'].strip()
            logger.info(f"Generated text: {generated_text[:200]}...")  # 只记录前200个字符
            return generated_text
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API请求失败: {str(e)}")
            raise Exception(f"无法连接到Ollama服务: {str(e)}")
        except Exception as e:
            logger.error(f"处理内容时发生错误: {str(e)}")
            raise Exception(str(e))
            
    def is_service_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except:
            return False

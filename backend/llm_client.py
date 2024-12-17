import requests
from typing import Dict, Any, Optional
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
from functools import lru_cache
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = "llama3:latest", host: str = "localhost", port: int = 11434):
        self.model = model
        self.base_url = f"http://{host}:{port}/api"
        logger.info(f"Initialized OllamaClient with model: {model}")
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_cache_key(self, prompt: str, system: str = None) -> str:
        """生成缓存键"""
        content = f"{prompt}:{system if system else ''}"
        return hashlib.md5(content.encode()).hexdigest()

    @lru_cache(maxsize=1000)
    def _cached_generate(self, cache_key: str, prompt: str, system: str = None) -> Dict[str, Any]:
        """带缓存的生成函数"""
        url = f"{self.base_url}/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        try:
            logger.info(f"Cache miss for key: {cache_key[:8]}...")
            start_time = time.time()
            
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            processing_time = time.time() - start_time
            logger.info(f"Generation completed in {processing_time:.2f} seconds")
            
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("Request to Ollama API timed out")
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def generate(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """生成响应"""
        try:
            cache_key = self._get_cache_key(prompt, system)
            
            # 记录提示词
            logger.info("Prompt sent to LLM:\n" + "-"*50 + "\n" + prompt + "\n" + "-"*50)
            if system:
                logger.info("System prompt:\n" + "-"*50 + "\n" + system + "\n" + "-"*50)
            
            return self._cached_generate(cache_key, prompt, system)
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}")
            return {"response": "", "error": str(e)}

    def _get_page_type_prompt(self, content):
        return f"""分析以下网页内容的类型。内容类型包括:
- news: 新闻文章，包含具体新闻事件、时间、人物等信息
- news_list: 新闻列表页面，包含多个新闻标题和链接
- unknown: 无法确定类型的页面

请仅返回以上类型之一，不要包含其他内容。

网页内容:
{content}
"""

    def _get_entities_prompt(self, content, page_type):
        example_json = '''{
    "entities": [
        {
            "id": "p1",
            "type": "person",
            "name": "拜登",
            "description": "美国总统"
        },
        {
            "id": "o1",
            "type": "org",
            "name": "白宫",
            "description": "美国政府行政机构"
        },
        {
            "id": "l1",
            "type": "location",
            "name": "华盛顿",
            "description": "美国首都"
        },
        {
            "id": "e1",
            "type": "event",
            "name": "记者会",
            "description": "关于外交政策的新闻发布会"
        },
        {
            "id": "t1",
            "type": "time",
            "name": "2024-12-17",
            "description": "事件发生时间"
        }
    ],
    "relationships": [
        {
            "source": "p1",
            "target": "e1",
            "type": "participates_in"
        },
        {
            "source": "e1",
            "target": "l1",
            "type": "located_in"
        },
        {
            "source": "e1",
            "target": "t1",
            "type": "happens_at"
        },
        {
            "source": "p1",
            "target": "o1",
            "type": "affiliated_with"
        }
    ]
}'''
        
        return f"""你是一个专业的新闻分析AI。请仔细分析以下新闻内容，提取所有重要实体和它们之间的关系。注意：
1. 必须严格按照JSON格式返回
2. 确保提取所有关键实体（人物、组织、地点、事件、时间等）
3. 确保建立实体之间有意义的关系
4. ID必须唯一，使用p1、o1、l1、e1、t1等前缀区分不同类型

实体类型定义：
1. person (p前缀): 人物，如政治人物、企业家、专家等
2. org (o前缀): 组织机构，如政府、公司、组织等
3. location (l前缀): 地点，如国家、城市、地区等
4. event (e前缀): 事件，如会议、事故、战争等
5. time (t前缀): 时间点或时间段，使用ISO格式(YYYY-MM-DD)
6. topic (tp前缀): 主题或议题，如政策、倡议等

关系类型定义：
1. participates_in: 参与关系（人物/组织参与事件）
2. located_in: 位置关系（事件/组织发生或位于某地）
3. happens_at: 时间关系（事件发生于某时间）
4. affiliated_with: 隶属关系（人物属于某组织）
5. supports: 支持关系（人物/组织支持某议题/立场）
6. opposes: 反对关系（人物/组织反对某议题/立场）
7. relates_to: 相关关系（实体之间的其他关系）

请按照以下示例格式返回JSON（注意：这只是示例，你需要根据实际新闻内容提取实体和关系）：

{example_json}

新闻内容：
{content}"""

    def analyze_page_type(self, content: str) -> Dict[str, Any]:
        """分析页面类型"""
        prompt = self._get_page_type_prompt(content)
        response = self.generate(prompt)
        try:
            result = response.get("response", "")
            return {"type": result.strip()}
        except Exception as e:
            return {
                "type": "unknown",
                "error": str(e)
            }

    def extract_entities_relations(self, content: str, page_type: str) -> Dict[str, Any]:
        """从内容中提取实体和关系"""
        prompt = self._get_entities_prompt(content, page_type)
        response = self.generate(prompt)
        try:
            result = response.get("response", "")
            print("LLM Response:", result)  # 添加调试输出
            parsed_result = json.loads(result)
            
            # 验证结果格式
            if not isinstance(parsed_result, dict):
                raise ValueError("Response is not a dictionary")
            
            if "entities" not in parsed_result or "relationships" not in parsed_result:
                raise ValueError("Missing required keys: entities or relationships")
            
            # 验证实体ID的唯一性
            entity_ids = [e.get("id") for e in parsed_result.get("entities", [])]
            if len(entity_ids) != len(set(entity_ids)):
                raise ValueError("Duplicate entity IDs found")
            
            # 验证关系引用的实体是否存在
            valid_ids = set(entity_ids)
            valid_relationships = []
            for rel in parsed_result.get("relationships", []):
                if rel.get("source") in valid_ids and rel.get("target") in valid_ids:
                    valid_relationships.append(rel)
            
            return {
                "entities": parsed_result.get("entities", []),
                "relationships": valid_relationships
            }
            
        except Exception as e:
            print(f"Error parsing response: {str(e)}")  # 添加错误调试输出
            return {
                "entities": [],
                "relationships": [],
                "error": f"Failed to parse response: {str(e)}"
            }

# 测试代码
if __name__ == "__main__":
    client = OllamaClient()
    test_content = """
    <html>
        <body>
            <h1>测试页面</h1>
            <p>这是一个测试内容...</p>
        </body>
    </html>
    """
    
    # 测试连接和模型响应
    result = client.generate("你好，测试连接。")
    print("Connection test:", result)

    # 测试页面类型分析
    page_type_result = client.analyze_page_type(test_content)
    print("Page type analysis:", page_type_result)

    # 测试实体和关系提取
    entities_relations_result = client.extract_entities_relations(test_content, page_type_result["type"])
    print("Entities and relationships extraction:", entities_relations_result)

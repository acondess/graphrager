import requests
import json
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_session():
    """创建带有自定义headers的会话"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    retry_strategy = Retry(
        total=3,  # 最大重试次数
        backoff_factor=1,  # 重试间隔
        status_forcelist=[500, 502, 503, 504]  # 需要重试的状态码
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def test_analyze_endpoint():
    """测试 /analyze 端点"""
    url = "http://localhost:5000/analyze"
    test_url = "https://www.zaobao.com.sg/realtime/world/story20241216-5601903"  # 测试新闻链接
    
    session = create_session()
    
    try:
        logger.info(f"Testing URL: {test_url}")
        start_time = time.time()
        
        # 发送请求
        response = session.post(
            url,
            json={"url": test_url},
            timeout=120  # 2分钟超时
        )
        
        # 检查响应状态码
        if response.status_code != 200:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return
        
        # 解析响应
        try:
            result = response.json()
            logger.info("Response received successfully")
            logger.info(f"Processing time: {time.time() - start_time:.2f} seconds")
            logger.info(f"Page type: {result.get('page_type', {}).get('type', 'unknown')}")
            logger.info(f"Status: {result.get('status', 'unknown')}")
            
            # 打印完整响应（用于调试）
            logger.debug(f"Full response: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {120} seconds")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.exception(e)
    finally:
        session.close()

if __name__ == "__main__":
    test_analyze_endpoint()

import requests
import logging

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_direct_access():
    url = "https://www.zaobao.com.sg/realtime/world/story20241216-5601903"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Content Length: {len(response.text)}")
        logger.info(f"Content Type: {response.headers.get('content-type')}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing URL: {e}")

if __name__ == "__main__":
    test_direct_access()

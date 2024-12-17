import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
from urllib.parse import urlparse

class WebExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def validate_url(self, url: str) -> bool:
        """验证URL格式是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            self.logger.error(f"URL validation failed: {str(e)}")
            return False

    def fetch_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """获取网页内容，带重试机制"""
        if not self.validate_url(url):
            raise ValueError("Invalid URL format")

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise

    def clean_html(self, html_content: str) -> str:
        """清洗HTML内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本和样式
        for element in soup.find_all(['script', 'style', 'iframe', 'nav', 'footer']):
            element.decompose()
        
        # 提取正文内容
        content_selectors = [
            'article', '.article', '#article',
            '.content', '#content', 'main',
            '.post-content', '#post-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            if selector.startswith('.'):
                element = soup.find(class_=selector[1:])
            elif selector.startswith('#'):
                element = soup.find(id=selector[1:])
            else:
                element = soup.find(selector)
            
            if element:
                main_content = element
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        return ' '.join(p.text.strip() for p in main_content.find_all('p') if p.text.strip())

    def extract(self, url: str) -> Dict[str, str]:
        """主要提取方法"""
        try:
            html_content = self.fetch_content(url)
            cleaned_text = self.clean_html(html_content)
            
            return {
                'url': url,
                'content': cleaned_text,
                'status': 'success'
            }
        except Exception as e:
            self.logger.error(f"Extraction failed: {str(e)}")
            return {
                'url': url,
                'content': '',
                'status': 'error',
                'error': str(e)
            }

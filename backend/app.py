from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import time
import requests
import json
import traceback
from bs4 import BeautifulSoup

from modules.web_extractor.extractor import WebExtractor
from modules.llm_processor.processor import LLMProcessor
from modules.graph_generator.generator import GraphGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# 初始化模块
web_extractor = WebExtractor()
llm_processor = LLMProcessor()
graph_generator = GraphGenerator()

class LogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = {
            'level': record.levelname,
            'message': record.getMessage(),
            'timestamp': time.time()
        }
        self.logs.append(log_entry)

    def get_logs(self):
        return self.logs

    def clear(self):
        self.logs = []

# 创建全局日志处理器
log_handler = LogHandler()
logger.addHandler(log_handler)

def error_response(message, status_code=400):
    return jsonify({"error": str(message)}), status_code

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用的Ollama模型列表"""
    try:
        # 首先尝试从Ollama API获取模型列表
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models_data = response.json()
            # 确保返回的数据格式正确
            if 'models' in models_data:
                return jsonify(models_data)
            else:
                # 如果返回的数据格式不正确，构造正确的格式
                models = [{'name': model['name']} for model in models_data.get('models', [])]
                return jsonify({'models': models})
        else:
            logger.warning(f"Failed to fetch models from Ollama API: {response.status_code}")
            # 如果无法从API获取，返回默认模型列表
            default_models = [
                {'name': 'llama2'},
                {'name': 'mistral'}
            ]
            return jsonify({'models': default_models})
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to Ollama API, using default models")
        # 连接失败时返回默认模型列表
        default_models = [
            {'name': 'llama2'},
            {'name': 'mistral'}
        ]
        return jsonify({'models': default_models})
    except Exception as e:
        return error_response(f"获取模型列表失败: {str(e)}")

def extract_content(url):
    """从URL中提取文本内容"""
    try:
        # 添加用户代理头，避免被拒绝访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP响应状态
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise ValueError(f"不支持的内容类型: {content_type}")
        
        # 使用Beautiful Soup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 提取所有文本内容
        text = soup.get_text()
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求URL失败: {str(e)}")
        raise ValueError(f"无法访问URL: {str(e)}")
    except Exception as e:
        logger.error(f"提取内容时出错: {str(e)}")
        raise ValueError(f"提取内容失败: {str(e)}")

@app.route('/api/extract', methods=['POST'])
def extract():
    """提取网页内容"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return error_response("Missing URL parameter")

        url = data['url']
        # 调用提取器并获取结果
        result = extract_content(url)
        
        # 检查提取状态
        if not result:
            return error_response("No content extracted")
            
        return jsonify({'content': result})
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"内容提取失败: {str(e)}")

@app.route('/api/structure', methods=['POST'])
def structure():
    """生成结构化内容"""
    try:
        data = request.get_json()
        if not data:
            return error_response("Missing request data")
            
        required_fields = ['model', 'prompt', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return error_response(f"Missing required fields: {', '.join(missing_fields)}")

        content = data.get('content')
        prompt = data.get('prompt')
        model = data.get('model')

        if not content:
            return error_response('Content is required')
        if not model:
            return error_response('Model is required')

        logger.info(f"Processing content with model: {model}")
        logger.debug(f"Content length: {len(content)}")
        logger.debug(f"Prompt length: {len(prompt) if prompt else 0}")
        
        # 确保Ollama服务正在运行
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code != 200:
                return error_response("Ollama service is not responding properly")
        except requests.exceptions.ConnectionError:
            return error_response("Could not connect to Ollama service. Please ensure it is running.")
            
        # 处理内容
        result = llm_processor.process(model, prompt, content)
        
        # 记录生成结果
        logger.info(f"Generated content from LLM")
        
        # 返回原始结果，不进行JSON解析
        return jsonify({'result': result, 'raw_output': result})
        
    except Exception as e:
        logger.error(f"Structure generation error: {str(e)}")
        traceback.print_exc()  # 打印详细错误信息到控制台
        return error_response(f"结构化处理失败: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

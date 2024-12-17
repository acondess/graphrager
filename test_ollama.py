import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3:latest",
        "prompt": "你好，这是一个测试。请用一句话回复。",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 50
        }
    }
    
    try:
        logger.info("Testing Ollama API directly...")
        logger.info(f"Sending request to: {url}")
        logger.info(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Response from Ollama:")
        logger.info(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error(f"Error testing Ollama: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    test_ollama()

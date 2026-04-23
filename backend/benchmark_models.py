import json
import urllib.request
import time

HOST = "http://localhost:11434/api/generate"
MODELS = ["qwen2.5-coder:1.5b", "phi3:mini", "llama3.2:1b"]

PROMPT = """Analyze INFY at CMP 1450.
Task: Act as a Senior Market Strategist.
1. Provide a 'market_narrative' consisting of 1 paragraph.
2. Provide 'pros' and 'cons' (1 point each).
3. Provide 'target_1' and 'stop_loss'.

Expected JSON ONLY:
{
    "market_narrative": "Paragraph 1...",
    "pros": ["Point 1"],
    "cons": ["Point 1"],
    "target_1": 1500.0, "stop_loss": 1400.0
}"""

def test_model(model):
    payload = {
        "model": model,
        "prompt": PROMPT,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 300}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(HOST, data=data, headers={'Content-Type': 'application/json'})
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                return model, -1, f"Error: {resp.status}"
            
            result = json.loads(resp.read().decode("utf-8"))
            end_time = time.time()
            
            response_text = result.get("response", "")
            
            # Check if valid JSON
            is_valid = False
            try:
                cleaned = response_text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].split("```")[0].strip()
                    
                json_start = cleaned.find('{')
                json_end = cleaned.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json.loads(cleaned[json_start:json_end])
                    is_valid = True
            except Exception as e:
                pass
            
            return model, round(end_time - start_time, 2), "Valid JSON" if is_valid else f"Invalid JSON: {response_text[:50]}"
    except Exception as e:
        return model, -1, str(e)

def main():
    print(f"{'Model':<20} | {'Time (s)':<10} | {'Result'}")
    print("-" * 50)
    for model in MODELS:
        m, t, res = test_model(model)
        print(f"{m:<20} | {t:<10} | {res}")

if __name__ == "__main__":
    main()

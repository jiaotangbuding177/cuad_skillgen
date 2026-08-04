import os
import openai

# ≤‚ ‘ ECNU  «∑Ò÷ß≥÷ response_format
client = openai.OpenAI(
    api_key=os.environ.get("ECNU_API_KEY"),
    base_url="https://chat.ecnu.edu.cn/open/api/v1"
)

try:
    response = client.chat.completions.create(
        model="ecnu-plus",
        messages=[{"role": "user", "content": "Return a JSON object with key 'test' and value 123"}],
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    print(f"Success: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

path = r'D:\cuad-skillgenbench\scripts\common\llm_client.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = '                self.usage.record(usage_dict["prompt_tokens"], usage_dict["completion_tokens"])\n                return text, usage_dict'
new = '                if text is None:\n                    raise ValueError("LLM returned None response")\n\n                self.usage.record(usage_dict["prompt_tokens"], usage_dict["completion_tokens"])\n                return text, usage_dict'

assert old in content, 'target code not found'
content = content.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK - Added None response check')

path = r'D:\cuad-skillgenbench\scripts\common\llm_client.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                elif self._provider == "ecnu":
                    kwargs = {
                        "model": self.model,
                        "max_tokens": max_tok,
                        "temperature": temp,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    }
                    if response_format == "json":
                        kwargs["response_format"] = {"type": "json_object"}
                    response = client.chat.completions.create(**kwargs)'''

new = '''                elif self._provider == "ecnu":
                    kwargs = {
                        "model": self.model,
                        "max_tokens": max_tok,
                        "temperature": temp,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    }
                    response = client.chat.completions.create(**kwargs)'''

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK')
else:
    print('ERROR: Target code not found')

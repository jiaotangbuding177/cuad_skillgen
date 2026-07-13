"""
LLM client wrapper for CUAD-SkillGen baselines.

Provides unified interface for LLM API calls with:
- Retry logic
- Token counting
- Usage logging
- Support for multiple providers (Claude, OpenAI)
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple


class LLMUsage:
    """Track LLM API usage."""

    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.calls = 0
        self.errors = 0

    def record(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.calls += 1

    def record_error(self):
        self.errors += 1

    def to_dict(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "calls": self.calls,
            "errors": self.errors,
        }

    def __repr__(self):
        return f"LLMUsage(calls={self.calls}, tokens={self.total_tokens}, errors={self.errors})"


class LLMClient:
    """Unified LLM client with retry and logging."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.usage = LLMUsage()
        self._client = None

    def _get_client(self):
        """Lazy-initialize the API client."""
        if self._client is None:
            if self.model.startswith("claude") or self.model.startswith("anthropic"):
                try:
                    import anthropic
                    api_key = os.environ.get("ANTHROPIC_API_KEY")
                    if not api_key:
                        raise ValueError("ANTHROPIC_API_KEY not set")
                    self._client = anthropic.Anthropic(api_key=api_key)
                    self._provider = "anthropic"
                except ImportError:
                    raise ImportError("anthropic package not installed. Run: pip install anthropic")
            elif self.model.startswith("gpt") or self.model.startswith("o1") or self.model.startswith("o3"):
                try:
                    import openai
                    api_key = os.environ.get("OPENAI_API_KEY")
                    if not api_key:
                        raise ValueError("OPENAI_API_KEY not set")
                    self._client = openai.OpenAI(api_key=api_key)
                    self._provider = "openai"
                except ImportError:
                    raise ImportError("openai package not installed. Run: pip install openai")
            else:
                raise ValueError(f"Unsupported model: {self.model}")
        return self._client

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> Tuple[str, dict]:
        """
        Make a single LLM API call.

        Args:
            system_prompt: System message
            user_prompt: User message
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            response_format: "json" for JSON mode (OpenAI only)

        Returns:
            Tuple of (response_text, usage_dict)
        """
        client = self._get_client()
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        last_error = None
        for attempt in range(self.max_retries):
            try:
                if self._provider == "anthropic":
                    response = client.messages.create(
                        model=self.model,
                        max_tokens=max_tok,
                        temperature=temp,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    text = response.content[0].text
                    usage_dict = {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                    }

                elif self._provider == "openai":
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
                    response = client.chat.completions.create(**kwargs)
                    text = response.choices[0].message.content
                    usage_dict = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                self.usage.record(usage_dict["prompt_tokens"], usage_dict["completion_tokens"])
                return text, usage_dict

            except Exception as e:
                last_error = e
                self.usage.record_error()
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"  LLM call failed (attempt {attempt+1}/{self.max_retries}): {e}")
                    print(f"  Retrying in {delay}s...")
                    time.sleep(delay)

        raise RuntimeError(f"LLM call failed after {self.max_retries} attempts: {last_error}")

    def call_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Tuple[dict, dict]:
        """
        Make an LLM call expecting JSON output.

        Returns:
            Tuple of (parsed_json, usage_dict)
        """
        # Add JSON instruction to system prompt
        json_system = system_prompt + "\n\nReturn your response as valid JSON only. Do not include any text outside the JSON."

        text, usage = self.call(json_system, user_prompt, temperature, max_tokens, response_format="json")

        # Parse JSON from response
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_str)
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
                result = json.loads(json_str)
            else:
                raise

        return result, usage

    def get_total_usage(self) -> dict:
        """Get total usage across all calls."""
        return self.usage.to_dict()

    def reset_usage(self):
        """Reset usage counters."""
        self.usage = LLMUsage()


def estimate_tokens(text: str) -> int:
    """Rough token count estimate (1 token ≈ 4 chars for English)."""
    return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars]

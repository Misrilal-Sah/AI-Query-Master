"""
AI Query Master - Multi-LLM Provider with Fallback Chain
Supports: Gemini → Groq → OpenRouter
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LLMProvider:
    """Multi-LLM provider with automatic fallback chain."""

    def __init__(self):
        self.providers = []
        self._init_providers()
        self.last_provider_used = None

    def _init_providers(self):
        """Initialize all available LLM providers in priority order."""

        # Priority 1: Google Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.providers.append({
                "name": "Gemini 2.0 Flash",
                "type": "gemini",
                "api_key": gemini_key,
                "model": "gemini-2.0-flash",
            })
            self.providers.append({
                "name": "Gemini 2.0 Flash Lite",
                "type": "gemini",
                "api_key": gemini_key,
                "model": "gemini-2.0-flash-lite",
            })

        # Priority 2: Groq (Fast & Free)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers.append({
                "name": "Groq Llama 3.1 8B",
                "type": "groq",
                "api_key": groq_key,
                "model": "llama-3.1-8b-instant",
            })

        # Priority 3: OpenRouter (Free models)
        or_key1 = os.getenv("OPENROUTER_KEY_1")
        if or_key1:
            self.providers.append({
                "name": "OpenRouter (Gemma 3 4B)",
                "type": "openrouter",
                "api_key": or_key1,
                "model": "google/gemma-3-4b-it:free",
            })

        or_key2 = os.getenv("OPENROUTER_KEY_2")
        if or_key2:
            self.providers.append({
                "name": "OpenRouter (Llama 3.3 70B)",
                "type": "openrouter",
                "api_key": or_key2,
                "model": "meta-llama/llama-3.3-70b-instruct:free",
            })

        if not self.providers:
            raise ValueError("No LLM API keys configured. Set at least one in .env")

        logger.info(f"Initialized {len(self.providers)} LLM providers: "
                     f"{[p['name'] for p in self.providers]}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response using the fallback chain.
        Returns: {"text": str, "provider": str, "model": str, "success": bool}
        """
        errors = []

        for provider in self.providers:
            try:
                logger.info(f"Trying {provider['name']}...")
                start_time = time.time()

                if provider["type"] == "gemini":
                    text = self._call_gemini(provider, prompt, system_prompt,
                                             temperature, max_tokens, json_mode)
                elif provider["type"] == "groq":
                    text = self._call_groq(provider, prompt, system_prompt,
                                           temperature, max_tokens, json_mode)
                elif provider["type"] == "openrouter":
                    text = self._call_openrouter(provider, prompt, system_prompt,
                                                 temperature, max_tokens, json_mode)
                else:
                    continue

                elapsed = time.time() - start_time
                self.last_provider_used = provider["name"]
                logger.info(f"✓ {provider['name']} responded in {elapsed:.2f}s")

                return {
                    "text": text,
                    "provider": provider["name"],
                    "model": provider["model"],
                    "success": True,
                    "time": round(elapsed, 2),
                }

            except Exception as e:
                error_msg = f"{provider['name']}: {str(e)}"
                logger.warning(f"✗ {error_msg}")
                errors.append(error_msg)
                continue

        # All providers failed
        logger.error(f"All LLM providers failed: {errors}")
        return {
            "text": f"All LLM providers failed. Errors: {'; '.join(errors)}",
            "provider": "none",
            "model": "none",
            "success": False,
            "errors": errors,
        }

    def _call_gemini(self, provider, prompt, system_prompt, temperature, max_tokens, json_mode):
        """Call Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=provider["api_key"])

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name=provider["model"],
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None,
        )

        response = model.generate_content(prompt)

        if response.text:
            return response.text
        raise Exception("Empty response from Gemini")

    def _call_groq(self, provider, prompt, system_prompt, temperature, max_tokens, json_mode):
        """Call Groq API."""
        from groq import Groq

        client = Groq(api_key=provider["api_key"])

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        text = response.choices[0].message.content

        if text:
            return text
        raise Exception("Empty response from Groq")

    def _call_openrouter(self, provider, prompt, system_prompt, temperature, max_tokens, json_mode):
        """Call OpenRouter API (OpenAI-compatible)."""
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=provider["api_key"],
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        text = response.choices[0].message.content

        if text:
            return text
        raise Exception("Empty response from OpenRouter")


# Singleton instance
_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Get or create the singleton LLM provider."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider

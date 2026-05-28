import json
import urllib.request
from .config import TOKEN_PRICES


def _http_post(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _openai_compat(base_url: str, api_key: str, model_id: str, prompt: str) -> tuple[str, int, int]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = _http_post(f"{base_url}/v1/chat/completions", headers, body)
    text = resp["choices"][0]["message"]["content"]
    input_tokens = resp["usage"]["prompt_tokens"]
    output_tokens = resp["usage"]["completion_tokens"]
    return text, input_tokens, output_tokens


def call_anthropic(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": model_id,
        "max_tokens": 8096,
        "messages": [{"role": "user", "content": full_prompt}],
    }
    resp = _http_post("https://api.anthropic.com/v1/messages", headers, body)
    text = resp["content"][0]["text"]
    return text, resp["usage"]["input_tokens"], resp["usage"]["output_tokens"]


def call_openai(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.openai.com", api_key, model_id, full_prompt)


def call_google(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    headers = {"Content-Type": "application/json"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": full_prompt}]}]}
    resp = _http_post(url, headers, body)
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    usage = resp.get("usageMetadata", {})
    return text, usage.get("promptTokenCount", 0), usage.get("candidatesTokenCount", 0)


def call_mistral(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.mistral.ai", api_key, model_id, full_prompt)


def call_deepseek(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.deepseek.com", api_key, model_id, full_prompt)


def call_xai(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.x.ai", api_key, model_id, full_prompt)


def call_cohere(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": full_prompt}],
    }
    resp = _http_post("https://api.cohere.com/v2/chat", headers, body)
    text = resp["message"]["content"][0]["text"]
    usage = resp.get("usage", {}).get("tokens", {})
    return text, usage.get("input_tokens", 0), usage.get("output_tokens", 0)


def call_groq(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.groq.com/openai", api_key, model_id, full_prompt)


def call_perplexity(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.perplexity.ai", api_key, model_id, full_prompt)


def call_kimi(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.moonshot.ai", api_key, model_id, full_prompt)


def call_qwen(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://dashscope.aliyuncs.com/compatible-mode", api_key, model_id, full_prompt)


def call_llama(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.llama.com", api_key, model_id, full_prompt)


def call_siliconflow(api_key: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    return _openai_compat("https://api.siliconflow.cn", api_key, model_id, full_prompt)


def call_ollama(ollama_url: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    headers = {"Content-Type": "application/json"}
    body = {"model": model_id, "messages": [{"role": "user", "content": full_prompt}], "stream": False}
    url = ollama_url.rstrip("/") + "/api/chat"
    resp = _http_post(url, headers, body)
    text = resp["message"]["content"]
    return text, resp.get("prompt_eval_count", 0), resp.get("eval_count", 0)


PROVIDER_CALLERS = {
    "anthropic":    call_anthropic,
    "openai":       call_openai,
    "google":       call_google,
    "mistral":      call_mistral,
    "deepseek":     call_deepseek,
    "xai":          call_xai,
    "cohere":       call_cohere,
    "groq":         call_groq,
    "perplexity":   call_perplexity,
    "kimi":         call_kimi,
    "qwen":         call_qwen,
    "llama":        call_llama,
    "siliconflow":  call_siliconflow,
}


def call_model(config: dict, provider: str, model_id: str, prompt: str, context: str = "") -> tuple[str, int, int]:
    if provider == "ollama":
        return call_ollama(config.get("ollama_url", "http://localhost:11434"), model_id, prompt, context)

    api_key = config["api_keys"].get(provider)
    if not api_key:
        raise ValueError(f"No API key set for '{provider}'. Run: progter {provider} \"your-api-key\"")

    caller = PROVIDER_CALLERS.get(provider)
    if not caller:
        raise ValueError(f"Unknown provider: {provider}")

    return caller(api_key, model_id, prompt, context)

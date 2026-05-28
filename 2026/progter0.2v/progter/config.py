import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".progter" / "config.json"

DEFAULT_CONFIG = {
    "api_keys": {
        "anthropic": None,
        "openai": None,
        "google": None,
        "mistral": None,
        "deepseek": None,
        "xai": None,
        "cohere": None,
        "groq": None,
        "perplexity": None,
        "kimi": None,
        "qwen": None,
        "siliconflow": None,
        "llama": None,
    },
    "ollama_url": "http://localhost:11434",
    "ollama_models": [],
    "folder_path": None,
    "token_usage": {}
}

MODEL_ALIASES = {
    # ── Anthropic ─────────────────────────────────────────────────────────────
    "claude":           "claude-sonnet-4-6",
    "claude_sonnet4_6": "claude-sonnet-4-6",
    "claude_opus4_6":   "claude-opus-4-6",
    "claude_haiku4_5":  "claude-haiku-4-5",

    # ── OpenAI ────────────────────────────────────────────────────────────────
    "chatgpt":          "gpt-4o",
    "gpt4o":            "gpt-4o",
    "gpt4o_mini":       "gpt-4o-mini",
    "o3":               "o3",
    "o3_mini":          "o3-mini",

    # ── Google ────────────────────────────────────────────────────────────────
    "gemini":           "gemini-2.5-pro",
    "gemini_2_5":       "gemini-2.5-pro",
    "gemini_2_5_flash": "gemini-2.5-flash",

    # ── Mistral ───────────────────────────────────────────────────────────────
    "mistral":          "mistral-large-latest",
    "mistral_large3":   "mistral-large-latest",
    "mistral_small4":   "mistral-small-latest",
    "codestral":        "codestral-latest",
    "devstral":         "devstral-latest",
    "magistral":        "magistral-medium-latest",

    # ── DeepSeek ──────────────────────────────────────────────────────────────
    "deepseek":         "deepseek-chat",
    "deepseek_v4":      "deepseek-chat",
    "deepseek_r2":      "deepseek-reasoner",

    # ── xAI ───────────────────────────────────────────────────────────────────
    "grok":             "grok-3",
    "grok_4":           "grok-4",
    "grok_4_1":         "grok-4-1-fast-non-reasoning",

    # ── Cohere ────────────────────────────────────────────────────────────────
    "cohere":           "command-r-plus",
    "command_r":        "command-r-08-2024",
    "command_r_plus":   "command-r-plus-08-2024",

    # ── Groq ──────────────────────────────────────────────────────────────────
    "groq":             "llama-3.3-70b-versatile",
    "groq_llama":       "llama-3.3-70b-versatile",

    # ── Perplexity ────────────────────────────────────────────────────────────
    "perplexity":       "sonar-pro",
    "sonar":            "sonar",
    "sonar_pro":        "sonar-pro",

    # ── Kimi (Moonshot AI) ────────────────────────────────────────────────────
    "kimi":             "kimi-k2.6",
    "kimi_k2":          "kimi-k2",
    "kimi_k2_6":        "kimi-k2.6",
    "kimi_k2_5":        "kimi-k2.5",

    # ── Qwen (Alibaba) ────────────────────────────────────────────────────────
    "qwen":             "qwen-max",
    "qwen_max":         "qwen-max",
    "qwen_plus":        "qwen-plus",
    "qwen_turbo":       "qwen-turbo",
    "qwen_coder":       "qwen-coder-plus",
    "qwen3":            "qwen3-235b-a22b",
    "qwen3_235b":       "qwen3-235b-a22b",

    # ── Meta Llama API ────────────────────────────────────────────────────────
    "llama":            "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "llama4":           "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "llama4_maverick":  "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "llama4_scout":     "Llama-4-Scout-17B-16E-Instruct",
    "llama3_3":         "Llama-3.3-70B-Instruct",
    "llama3_3_8b":      "Llama-3.3-8B-Instruct",

    # ── SiliconFlow ───────────────────────────────────────────────────────────
    # Kimi via SiliconFlow
    "sf_kimi":          "moonshotai/Kimi-K2.6",
    "sf_kimi_k2_5":     "moonshotai/Kimi-K2.5",
    # DeepSeek via SiliconFlow
    "sf_deepseek":      "deepseek-ai/DeepSeek-V3",
    "sf_deepseek_v4":   "Pro/deepseek-ai/DeepSeek-V4-Pro",
    "sf_deepseek_flash":"Pro/deepseek-ai/DeepSeek-V4-Flash",
    "sf_deepseek_r1":   "deepseek-ai/DeepSeek-R1",
    "sf_deepseek_r2":   "deepseek-ai/DeepSeek-R2",
    # Qwen via SiliconFlow
    "sf_qwen3":         "Qwen/Qwen3-235B-A22B",
    "sf_qwen3_30b":     "Qwen/Qwen3-30B-A3B",
    "sf_qwen3_14b":     "Qwen/Qwen3-14B",
    "sf_qwen3_8b":      "Qwen/Qwen3-8B",
    "sf_qwen3_5":       "Qwen/Qwen3.5-397B-A17B",
    "sf_qwen3_5_122b":  "Qwen/Qwen3.5-122B-A10B",
    "sf_qwen3_5_35b":   "Qwen/Qwen3.5-35B-A3B",
    "sf_qwen3_5_27b":   "Qwen/Qwen3.5-27B",
    "sf_qwen3_6":       "Qwen/Qwen3.6-35B-A3B",
    "sf_qwen3_6_27b":   "Qwen/Qwen3.6-27B",
    "sf_qwen_coder":    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "sf_qwen2_5_72b":   "Qwen/Qwen2.5-72B-Instruct",
    # GLM via SiliconFlow
    "sf_glm":           "THUDM/GLM-4.7",
    "sf_glm4_7":        "THUDM/GLM-4.7",
    "sf_glm5":          "THUDM/GLM-5.1",
    "sf_glm4_5":        "THUDM/GLM-4.5-Air",
    "sf_glm4_6":        "THUDM/GLM-4.6",
    # Llama via SiliconFlow
    "sf_llama4":        "meta-llama/Llama-4-Maverick-Instruct",
    "sf_llama4_scout":  "meta-llama/Llama-4-Scout-Instruct",
    "sf_llama3_3":      "meta-llama/Llama-3.3-70B-Instruct",
    # Gemma via SiliconFlow
    "sf_gemma4":        "google/gemma-4-31b-it",
    "sf_gemma4_26b":    "google/gemma-4-26b-it",
    # MiniMax via SiliconFlow
    "sf_minimax":       "MiniMax/MiniMax-M2.5",
    "sf_minimax_m1":    "MiniMax/MiniMax-M1-80k",
    # ByteDance Seed via SiliconFlow
    "sf_seed":          "ByteDance-Seed/Seed-OSS-36B-Instruct",
    # Mistral via SiliconFlow
    "sf_mistral":       "mistralai/Mistral-7B-Instruct-v0.2",
    # Hy3 via SiliconFlow
    "sf_hy3":           "Hy3/Hy3-preview",
    # Step via SiliconFlow
    "sf_step":          "Step-3.5-Flash",
    # Ling via SiliconFlow
    "sf_ling":          "Ling-flash-2.0",
}

PROVIDER_FOR_MODEL = {
    # Anthropic
    "claude-sonnet-4-6":                        "anthropic",
    "claude-opus-4-6":                          "anthropic",
    "claude-haiku-4-5":                         "anthropic",
    # OpenAI
    "gpt-4o":                                   "openai",
    "gpt-4o-mini":                              "openai",
    "o3":                                       "openai",
    "o3-mini":                                  "openai",
    # Google
    "gemini-2.5-pro":                           "google",
    "gemini-2.5-flash":                         "google",
    # Mistral
    "mistral-large-latest":                     "mistral",
    "mistral-small-latest":                     "mistral",
    "codestral-latest":                         "mistral",
    "devstral-latest":                          "mistral",
    "magistral-medium-latest":                  "mistral",
    # DeepSeek
    "deepseek-chat":                            "deepseek",
    "deepseek-reasoner":                        "deepseek",
    # xAI
    "grok-3":                                   "xai",
    "grok-4":                                   "xai",
    "grok-4-1-fast-non-reasoning":              "xai",
    # Cohere
    "command-r-plus":                           "cohere",
    "command-r-plus-08-2024":                   "cohere",
    "command-r-08-2024":                        "cohere",
    # Groq
    "llama-3.3-70b-versatile":                  "groq",
    # Perplexity
    "sonar":                                    "perplexity",
    "sonar-pro":                                "perplexity",
    # Kimi
    "kimi-k2":                                  "kimi",
    "kimi-k2.5":                                "kimi",
    "kimi-k2.6":                                "kimi",
    # Qwen
    "qwen-max":                                 "qwen",
    "qwen-plus":                                "qwen",
    "qwen-turbo":                               "qwen",
    "qwen-coder-plus":                          "qwen",
    "qwen3-235b-a22b":                          "qwen",
    # Meta Llama
    "Llama-4-Maverick-17B-128E-Instruct-FP8":   "llama",
    "Llama-4-Scout-17B-16E-Instruct":           "llama",
    "Llama-3.3-70B-Instruct":                   "llama",
    "Llama-3.3-8B-Instruct":                    "llama",
    # SiliconFlow
    "moonshotai/Kimi-K2.6":                     "siliconflow",
    "moonshotai/Kimi-K2.5":                     "siliconflow",
    "deepseek-ai/DeepSeek-V3":                  "siliconflow",
    "Pro/deepseek-ai/DeepSeek-V4-Pro":          "siliconflow",
    "Pro/deepseek-ai/DeepSeek-V4-Flash":        "siliconflow",
    "deepseek-ai/DeepSeek-R1":                  "siliconflow",
    "deepseek-ai/DeepSeek-R2":                  "siliconflow",
    "Qwen/Qwen3-235B-A22B":                     "siliconflow",
    "Qwen/Qwen3-30B-A3B":                       "siliconflow",
    "Qwen/Qwen3-14B":                           "siliconflow",
    "Qwen/Qwen3-8B":                            "siliconflow",
    "Qwen/Qwen3.5-397B-A17B":                   "siliconflow",
    "Qwen/Qwen3.5-122B-A10B":                   "siliconflow",
    "Qwen/Qwen3.5-35B-A3B":                     "siliconflow",
    "Qwen/Qwen3.5-27B":                         "siliconflow",
    "Qwen/Qwen3.6-35B-A3B":                     "siliconflow",
    "Qwen/Qwen3.6-27B":                         "siliconflow",
    "Qwen/Qwen2.5-Coder-32B-Instruct":          "siliconflow",
    "Qwen/Qwen2.5-72B-Instruct":                "siliconflow",
    "THUDM/GLM-4.7":                            "siliconflow",
    "THUDM/GLM-5.1":                            "siliconflow",
    "THUDM/GLM-4.5-Air":                        "siliconflow",
    "THUDM/GLM-4.6":                            "siliconflow",
    "meta-llama/Llama-4-Maverick-Instruct":     "siliconflow",
    "meta-llama/Llama-4-Scout-Instruct":        "siliconflow",
    "meta-llama/Llama-3.3-70B-Instruct":        "siliconflow",
    "google/gemma-4-31b-it":                    "siliconflow",
    "google/gemma-4-26b-it":                    "siliconflow",
    "MiniMax/MiniMax-M2.5":                     "siliconflow",
    "MiniMax/MiniMax-M1-80k":                   "siliconflow",
    "ByteDance-Seed/Seed-OSS-36B-Instruct":     "siliconflow",
    "mistralai/Mistral-7B-Instruct-v0.2":       "siliconflow",
    "Hy3/Hy3-preview":                          "siliconflow",
    "Step-3.5-Flash":                           "siliconflow",
    "Ling-flash-2.0":                           "siliconflow",
}

TOKEN_PRICES = {
    # Anthropic
    "claude-sonnet-4-6":                        {"input": 3.00,   "output": 15.00},
    "claude-opus-4-6":                          {"input": 15.00,  "output": 75.00},
    "claude-haiku-4-5":                         {"input": 0.80,   "output": 4.00},
    # OpenAI
    "gpt-4o":                                   {"input": 2.50,   "output": 10.00},
    "gpt-4o-mini":                              {"input": 0.15,   "output": 0.60},
    "o3":                                       {"input": 10.00,  "output": 40.00},
    # Google
    "gemini-2.5-pro":                           {"input": 1.25,   "output": 10.00},
    "gemini-2.5-flash":                         {"input": 0.075,  "output": 0.30},
    # Mistral
    "mistral-large-latest":                     {"input": 2.00,   "output": 6.00},
    "mistral-small-latest":                     {"input": 0.10,   "output": 0.30},
    "codestral-latest":                         {"input": 0.30,   "output": 0.90},
    "devstral-latest":                          {"input": 0.10,   "output": 0.30},
    "magistral-medium-latest":                  {"input": 0.50,   "output": 1.50},
    # DeepSeek
    "deepseek-chat":                            {"input": 0.27,   "output": 1.10},
    "deepseek-reasoner":                        {"input": 0.55,   "output": 2.19},
    # xAI
    "grok-3":                                   {"input": 3.00,   "output": 15.00},
    "grok-4":                                   {"input": 3.00,   "output": 15.00},
    # Cohere
    "command-r-plus-08-2024":                   {"input": 2.50,   "output": 10.00},
    "command-r-08-2024":                        {"input": 0.15,   "output": 0.60},
    # Groq
    "llama-3.3-70b-versatile":                  {"input": 0.05,   "output": 0.08},
    # Perplexity
    "sonar":                                    {"input": 1.00,   "output": 1.00},
    "sonar-pro":                                {"input": 3.00,   "output": 15.00},
    # Kimi
    "kimi-k2":                                  {"input": 0.57,   "output": 2.30},
    "kimi-k2.5":                                {"input": 0.50,   "output": 2.80},
    "kimi-k2.6":                                {"input": 0.57,   "output": 2.30},
    # Qwen
    "qwen-max":                                 {"input": 1.60,   "output": 6.40},
    "qwen-plus":                                {"input": 0.40,   "output": 1.20},
    "qwen-turbo":                               {"input": 0.05,   "output": 0.20},
    "qwen-coder-plus":                          {"input": 0.70,   "output": 2.80},
    "qwen3-235b-a22b":                          {"input": 0.50,   "output": 2.00},
    # Meta Llama
    "Llama-4-Maverick-17B-128E-Instruct-FP8":   {"input": 0.27,   "output": 0.85},
    "Llama-4-Scout-17B-16E-Instruct":           {"input": 0.18,   "output": 0.59},
    "Llama-3.3-70B-Instruct":                   {"input": 0.20,   "output": 0.60},
    "Llama-3.3-8B-Instruct":                    {"input": 0.05,   "output": 0.10},
    # SiliconFlow
    "moonshotai/Kimi-K2.6":                     {"input": 0.57,   "output": 2.30},
    "moonshotai/Kimi-K2.5":                     {"input": 0.50,   "output": 2.80},
    "Pro/deepseek-ai/DeepSeek-V4-Pro":          {"input": 0.145,  "output": 3.48},
    "Pro/deepseek-ai/DeepSeek-V4-Flash":        {"input": 0.028,  "output": 0.28},
    "deepseek-ai/DeepSeek-V3":                  {"input": 0.27,   "output": 1.10},
    "deepseek-ai/DeepSeek-R1":                  {"input": 0.55,   "output": 2.19},
    "deepseek-ai/DeepSeek-R2":                  {"input": 0.55,   "output": 2.19},
    "Qwen/Qwen3-235B-A22B":                     {"input": 0.50,   "output": 2.00},
    "Qwen/Qwen3-30B-A3B":                       {"input": 0.10,   "output": 0.30},
    "Qwen/Qwen3-14B":                           {"input": 0.07,   "output": 0.14},
    "Qwen/Qwen3-8B":                            {"input": 0.05,   "output": 0.10},
    "Qwen/Qwen3.5-397B-A17B":                   {"input": 0.80,   "output": 2.40},
    "Qwen/Qwen3.5-122B-A10B":                   {"input": 0.40,   "output": 1.20},
    "Qwen/Qwen3.5-35B-A3B":                     {"input": 0.10,   "output": 0.30},
    "Qwen/Qwen3.5-27B":                         {"input": 0.10,   "output": 0.30},
    "Qwen/Qwen3.6-35B-A3B":                     {"input": 0.10,   "output": 0.30},
    "Qwen/Qwen3.6-27B":                         {"input": 0.10,   "output": 0.30},
    "Qwen/Qwen2.5-Coder-32B-Instruct":          {"input": 0.07,   "output": 0.14},
    "Qwen/Qwen2.5-72B-Instruct":                {"input": 0.13,   "output": 0.40},
    "THUDM/GLM-4.7":                            {"input": 0.50,   "output": 1.90},
    "THUDM/GLM-5.1":                            {"input": 0.70,   "output": 2.50},
    "THUDM/GLM-4.5-Air":                        {"input": 0.10,   "output": 0.30},
    "THUDM/GLM-4.6":                            {"input": 0.50,   "output": 1.90},
    "meta-llama/Llama-4-Maverick-Instruct":     {"input": 0.27,   "output": 0.85},
    "meta-llama/Llama-4-Scout-Instruct":        {"input": 0.18,   "output": 0.59},
    "meta-llama/Llama-3.3-70B-Instruct":        {"input": 0.05,   "output": 0.08},
    "google/gemma-4-31b-it":                    {"input": 0.10,   "output": 0.30},
    "google/gemma-4-26b-it":                    {"input": 0.08,   "output": 0.20},
    "MiniMax/MiniMax-M2.5":                     {"input": 0.40,   "output": 1.60},
    "MiniMax/MiniMax-M1-80k":                   {"input": 0.40,   "output": 1.60},
    "ByteDance-Seed/Seed-OSS-36B-Instruct":     {"input": 0.10,   "output": 0.30},
    "mistralai/Mistral-7B-Instruct-v0.2":       {"input": 0.04,   "output": 0.04},
    "Hy3/Hy3-preview":                          {"input": 0.06,   "output": 0.06},
    "Step-3.5-Flash":                           {"input": 0.15,   "output": 0.50},
    "Ling-flash-2.0":                           {"input": 0.10,   "output": 0.30},
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    config = DEFAULT_CONFIG.copy()
    config.update(data)
    return config


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def resolve_model(alias: str) -> tuple[str, str]:
    alias_lower = alias.lower().replace("-", "_").replace(".", "_")

    for key, model_id in MODEL_ALIASES.items():
        if key.lower().replace("-", "_").replace(".", "_") == alias_lower:
            provider = PROVIDER_FOR_MODEL.get(model_id, "unknown")
            return model_id, provider

    if alias in PROVIDER_FOR_MODEL:
        return alias, PROVIDER_FOR_MODEL[alias]

    if alias.startswith("ollama_"):
        model_name = alias[len("ollama_"):]
        return model_name, "ollama"

    return alias, "unknown"


def record_usage(config: dict, model_id: str, input_tokens: int, output_tokens: int):
    usage = config.setdefault("token_usage", {})
    entry = usage.setdefault(model_id, {"input_tokens": 0, "output_tokens": 0})
    entry["input_tokens"] += input_tokens
    entry["output_tokens"] += output_tokens

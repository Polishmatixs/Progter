#!/usr/bin/env python3
import sys
import argparse

from .config import (
    load_config, save_config, resolve_model,
    record_usage, TOKEN_PRICES, MODEL_ALIASES
)
from .providers import call_model
from .files import build_generation_prompt, parse_ai_response, write_files


# ─── Helpers ──────────────────────────────────────────────────────────────────

def print_ok(msg: str):
    print(f"[OK] {msg}")

def print_err(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def print_info(msg: str):
    print(f"[INFO] {msg}")


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_set_api(provider: str, api_key: str):
    config = load_config()
    config["api_keys"][provider] = api_key
    save_config(config)
    print_ok(f"API key for '{provider}' saved.")


def cmd_folderpath(path: str):
    import os
    resolved = os.path.expanduser(path)
    config = load_config()
    config["folder_path"] = resolved
    save_config(config)
    print_ok(f"Project folder set to: {resolved}")


def cmd_ollama_url(url: str):
    config = load_config()
    config["ollama_url"] = url
    save_config(config)
    print_ok(f"Ollama URL set to: {url}")


def cmd_ollama_add(model_name: str):
    config = load_config()
    models = config.setdefault("ollama_models", [])
    if model_name not in models:
        models.append(model_name)
        save_config(config)
        print_ok(f"Ollama model '{model_name}' registered.")
    else:
        print_info(f"Ollama model '{model_name}' already registered.")


def cmd_generate(model_alias: str, prompt: str):
    config = load_config()

    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set. Run: folderpath \"/your/path\"")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)

    if provider == "unknown":
        print_err(f"Unknown model or alias: '{model_alias}'")
        print_info("Run 'progter help' to see available models.")
        sys.exit(1)

    print_info(f"Using {provider} / {model_id}")
    print_info(f"Project folder: {folder_path}")
    print_info("Sending request...")

    full_prompt = build_generation_prompt(prompt, folder_path)

    try:
        response, input_tokens, output_tokens = call_model(
            config, provider, model_id, full_prompt
        )
    except ValueError as e:
        print_err(str(e))
        sys.exit(1)
    except Exception as e:
        print_err(f"API call failed: {e}")
        sys.exit(1)

    record_usage(config, model_id, input_tokens, output_tokens)
    save_config(config)

    operations = parse_ai_response(response, folder_path)

    if not operations:
        print("\n--- AI Response ---")
        print(response)
        print("-------------------")
        print_info("No file operations detected in response.")
        return

    written = write_files(operations, folder_path)
    for f in written:
        print_ok(f"Written: {f}")

    print_info(f"Tokens used: {input_tokens} in / {output_tokens} out")


def cmd_hmmtpc():
    config = load_config()
    usage = config.get("token_usage", {})

    if not usage:
        print("No token usage recorded yet.")
        return

    total_cost = 0.0
    rows = []

    for model_id, tokens in usage.items():
        inp = tokens.get("input_tokens", 0)
        out = tokens.get("output_tokens", 0)

        prices = TOKEN_PRICES.get(model_id)
        if prices:
            cost = (inp * prices["input"] + out * prices["output"]) / 1_000_000
            cost_str = f"${cost:.4f}"
        else:
            cost = 0.0
            cost_str = "$0.0000 (local/unknown)"

        total_cost += cost
        rows.append((model_id, inp, out, cost_str))

    folder = config.get("folder_path", "unknown")
    print(f"\nProject cost report: {folder}")
    print("-" * 60)
    print(f"{'Model':<35} {'In tokens':>10} {'Out tokens':>10}  {'Cost':>10}")
    print("-" * 60)

    for model_id, inp, out, cost_str in rows:
        print(f"{model_id:<35} {inp:>10,} {out:>10,}  {cost_str:>10}")

    print("-" * 60)
    print(f"{'TOTAL':<55}  ${total_cost:.4f}")
    print()


def cmd_help():
    print("""
Progter - AI-powered terminal code assistant

SETUP
  <provider> "<api_key>"        Set API key for a provider
    Providers: anthropic, openai, google, mistral, deepseek, xai, cohere, groq, perplexity

  folderpath "<path>"           Set the project folder

  ollama "<url>"                Set Ollama server URL (default: http://localhost:11434)
  ollama_add <model>            Register a local Ollama model

GENERATE
  <model> "<prompt>"            Generate or edit code using the specified model
    Examples:
      claude_sonnet4.6 "create main.py with a FastAPI app"
      chatgpt "add authentication to main.py"
      gemini_2.5 "write tests for all functions"
      mistral_large3 "refactor the database module"
      deepseek_r2 "optimize the sorting algorithm"
      grok_4 "add error handling"
      codestral "improve the code style"
      groq_llama "add docstrings to all functions"
      ollama_llama3 "create a README.md"

AVAILABLE MODELS
  Anthropic:   claude_sonnet4.6, claude_opus4.6, claude_haiku4.5
  OpenAI:      chatgpt, gpt4o, gpt4o_mini, o3
  Google:      gemini, gemini_2.5, gemini_2.5_flash
  Mistral:     mistral, mistral_large3, mistral_small4, codestral, devstral, magistral
  DeepSeek:    deepseek, deepseek_v4, deepseek_r2
  xAI:         grok, grok_4, grok_4.1
  Cohere:      cohere, command_r, command_r_plus
  Groq:        groq, groq_llama
  Perplexity:  perplexity, sonar, sonar_pro
  Ollama:      ollama_<model_name>

OTHER
  hmmtpc                        Show total cost of the project in $
  help                          Show this help message
""")


# ─── Entry point ──────────────────────────────────────────────────────────────

PROVIDERS = {
    "anthropic", "openai", "google", "mistral",
    "deepseek", "xai", "cohere", "groq", "perplexity",
    "kimi", "qwen", "llama", "siliconflow",
}


def main():
    args = sys.argv[1:]

    if not args:
        cmd_help()
        return

    command = args[0].lower()

    # help
    if command == "help":
        cmd_help()

    # hmmtpc
    elif command == "hmmtpc":
        cmd_hmmtpc()

    # folderpath "<path>"
    elif command == "folderpath":
        if len(args) < 2:
            print_err("Usage: folderpath \"/your/path\"")
            sys.exit(1)
        cmd_folderpath(args[1])

    # ollama "<url>" or ollama_add <model>
    elif command == "ollama":
        if len(args) < 2:
            print_err("Usage: ollama \"http://localhost:11434\"")
            sys.exit(1)
        cmd_ollama_url(args[1])

    elif command == "ollama_add":
        if len(args) < 2:
            print_err("Usage: ollama_add <model_name>")
            sys.exit(1)
        cmd_ollama_add(args[1])

    # <provider> "<api_key>"
    elif command in PROVIDERS:
        if len(args) < 2:
            print_err(f"Usage: {command} \"your-api-key\"")
            sys.exit(1)
        cmd_set_api(command, args[1])

    # <model_alias> "<prompt>"
    elif len(args) >= 2:
        model_alias = args[0]
        prompt = args[1]
        cmd_generate(model_alias, prompt)

    else:
        print_err(f"Unknown command: {command}")
        print_info("Run 'progter help' to see available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()

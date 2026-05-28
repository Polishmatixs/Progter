#!/usr/bin/env python3
import sys
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path

from .config import (
    load_config, save_config, resolve_model,
    record_usage, TOKEN_PRICES, MODEL_ALIASES
)
from .providers import call_model
from .files import (
    build_generation_prompt, parse_ai_response, write_files,
    get_project_files, build_context
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

DEMO_MODE = False

def print_ok(msg: str):
    if DEMO_MODE:
        import time
        for ch in f"[OK] {msg}":
            print(ch, end="", flush=True)
            time.sleep(0.03)
        print()
    else:
        print(f"[OK] {msg}")

def print_err(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def print_info(msg: str):
    if DEMO_MODE:
        import time
        for ch in f"[INFO] {msg}":
            print(ch, end="", flush=True)
            time.sleep(0.02)
        print()
    else:
        print(f"[INFO] {msg}")

def print_header(msg: str):
    print(f"\n=== {msg} ===")


# ─── Backup / Undo ────────────────────────────────────────────────────────────

def backup_project(folder_path: str) -> str:
    backup_dir = Path.home() / ".progter" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / timestamp
    shutil.copytree(folder_path, backup_path, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".git", "node_modules"
    ))
    backups = sorted(backup_dir.iterdir())
    if len(backups) > 10:
        shutil.rmtree(backups[0])
    return str(backup_path)


def cmd_undo():
    backup_dir = Path.home() / ".progter" / "backups"
    if not backup_dir.exists():
        print_err("No backups found.")
        return

    backups = sorted(backup_dir.iterdir())
    if not backups:
        print_err("No backups found.")
        return

    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        return

    latest = backups[-1]
    print_info(f"Restoring from backup: {latest.name}")
    if Path(folder_path).exists():
        shutil.rmtree(folder_path)
    shutil.copytree(latest, folder_path)
    print_ok(f"Restored to state from {latest.name}")


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_set_api(provider: str, api_key: str):
    config = load_config()
    config["api_keys"][provider] = api_key
    save_config(config)
    print_ok(f"API key for '{provider}' saved.")


def cmd_folderpath(path: str):
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


def cmd_rules(rule: str = None):
    config = load_config()
    rules = config.setdefault("rules", [])

    if rule is None:
        if not rules:
            print("No rules set.")
        else:
            print("Active rules:")
            for i, r in enumerate(rules, 1):
                print(f"  {i}. {r}")
        return

    if rule.startswith("remove "):
        try:
            idx = int(rule.split()[1]) - 1
            removed = rules.pop(idx)
            save_config(config)
            print_ok(f"Removed rule: {removed}")
        except (ValueError, IndexError):
            print_err("Usage: progter rules remove <number>")
        return

    rules.append(rule)
    save_config(config)
    print_ok(f"Rule added: {rule}")


def cmd_status():
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        return

    files = get_project_files(folder_path)
    if not files:
        print(f"Project folder is empty: {folder_path}")
        return

    total_size = 0
    total_lines = 0
    print(f"\nProject: {folder_path}")
    print("-" * 55)
    print(f"{'File':<40} {'Lines':>6} {'Size':>8}")
    print("-" * 55)

    for filename, content in sorted(files.items()):
        lines = content.count("\n") + 1
        size = len(content.encode("utf-8"))
        total_size += size
        total_lines += lines
        size_str = f"{size:,}B" if size < 1024 else f"{size//1024}KB"
        print(f"{filename:<40} {lines:>6} {size_str:>8}")

    print("-" * 55)
    total_str = f"{total_size:,}B" if total_size < 1024 else f"{total_size//1024}KB"
    print(f"{'TOTAL':<40} {total_lines:>6} {total_str:>8}")
    print()


def cmd_generate(model_alias: str, prompt: str, plan_mode: bool = False):
    global DEMO_MODE
    config = load_config()

    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set. Run: progter folderpath \"your/path\"")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)
    if provider == "unknown":
        print_err(f"Unknown model or alias: '{model_alias}'")
        print_info("Run 'progter help' to see available models.")
        sys.exit(1)

    rules = config.get("rules", [])

    print_info(f"Using {provider} / {model_id}")
    print_info(f"Project folder: {folder_path}")

    if plan_mode:
        plan_prompt = (
            f"Before making any changes, describe in plain English exactly what files you will create "
            f"or modify and what changes you will make. Do NOT write any code yet. "
            f"User request: {prompt}"
        )
        context = build_context(folder_path)
        full_plan_prompt = f"{context}\n\n{plan_prompt}" if context else plan_prompt
        print_info("Generating plan...")
        try:
            plan_response, _, _ = call_model(config, provider, model_id, full_plan_prompt)
        except Exception as e:
            print_err(f"API call failed: {e}")
            sys.exit(1)
        print("\n--- Plan ---")
        print(plan_response)
        print("------------")
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm != "y":
            print_info("Cancelled.")
            return

    backup_path = backup_project(folder_path)
    print_info(f"Backup saved: {Path(backup_path).name}")
    print_info("Sending request...")

    full_prompt = build_generation_prompt(prompt, folder_path, rules)

    try:
        response, input_tokens, output_tokens = call_model(config, provider, model_id, full_prompt)
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


def cmd_multiprompt(model_aliases: list[str], prompt: str):
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        sys.exit(1)

    rules = config.get("rules", [])
    results = {}
    errors = {}
    lock = threading.Lock()

    def run_model(alias: str):
        model_id, provider = resolve_model(alias)
        if provider == "unknown":
            with lock:
                errors[alias] = f"Unknown model: {alias}"
            return

        short = alias.replace("_", "").replace(".", "")
        mp_prompt = (
            f"{prompt}\n\nIMPORTANT: Name all output files with _{short} suffix before the extension. "
            f"For example: main_{short}.py instead of main.py"
        )
        full_prompt = build_generation_prompt(mp_prompt, folder_path, rules)

        try:
            response, input_tokens, output_tokens = call_model(config, provider, model_id, full_prompt)
            operations = parse_ai_response(response, folder_path)
            written = write_files(operations, folder_path)
            with lock:
                results[alias] = (written, input_tokens, output_tokens)
                record_usage(config, model_id, input_tokens, output_tokens)
        except Exception as e:
            with lock:
                errors[alias] = str(e)

    print_header(f"Multiprompt: {len(model_aliases)} models")
    print_info(f"Prompt: {prompt}")
    print_info("Running all models in parallel...")
    print()

    threads = [threading.Thread(target=run_model, args=(alias,)) for alias in model_aliases]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    save_config(config)

    for alias in model_aliases:
        if alias in results:
            written, inp, out = results[alias]
            print_ok(f"{alias}: {', '.join(written)} ({inp} in / {out} out tokens)")
        elif alias in errors:
            print_err(f"{alias}: {errors[alias]}")


def cmd_chat(model_alias: str):
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)
    if provider == "unknown":
        print_err(f"Unknown model: {model_alias}")
        sys.exit(1)

    context = build_context(folder_path)
    print_info(f"Chat mode with {model_id}. Type 'exit' to quit.")
    print_info("AI has full context of your project.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("exit", "quit", "q"):
            break
        if not user_input:
            continue

        full_prompt = f"{context}\n\nUser question (do NOT generate files, just answer): {user_input}"
        try:
            response, input_tokens, output_tokens = call_model(config, provider, model_id, full_prompt)
            print(f"\nAI: {response}\n")
            record_usage(config, model_id, input_tokens, output_tokens)
            save_config(config)
        except Exception as e:
            print_err(f"API call failed: {e}")


def cmd_explain(model_alias: str, filepath: str):
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        sys.exit(1)

    target = Path(folder_path) / filepath
    if not target.exists():
        print_err(f"File not found: {filepath}")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)
    if provider == "unknown":
        print_err(f"Unknown model: {model_alias}")
        sys.exit(1)

    content = target.read_text(encoding="utf-8", errors="replace")
    prompt = (
        f"Explain this file clearly and concisely. Describe what it does, "
        f"what each function/class does, and any important details.\n\n"
        f"File: {filepath}\n\n{content}"
    )

    print_info(f"Explaining {filepath} using {model_id}...")
    try:
        response, input_tokens, output_tokens = call_model(config, provider, model_id, prompt)
        print(f"\n{response}\n")
        record_usage(config, model_id, input_tokens, output_tokens)
        save_config(config)
    except Exception as e:
        print_err(f"API call failed: {e}")


def cmd_fix(model_alias: str, filepath: str = None):
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)
    if provider == "unknown":
        print_err(f"Unknown model: {model_alias}")
        sys.exit(1)

    if filepath:
        target = Path(folder_path) / filepath
        if not target.exists():
            print_err(f"File not found: {filepath}")
            sys.exit(1)
        content = target.read_text(encoding="utf-8", errors="replace")
        prompt = f"Find and fix all bugs, errors, and issues in this file. Return the fixed file.\n\nFile: {filepath}\n\n{content}"
    else:
        prompt = "Find and fix all bugs, errors, and issues in the project."

    backup_project(folder_path)
    full_prompt = build_generation_prompt(prompt, folder_path, config.get("rules", []))

    print_info(f"Fixing using {model_id}...")
    try:
        response, input_tokens, output_tokens = call_model(config, provider, model_id, full_prompt)
        operations = parse_ai_response(response, folder_path)
        if operations:
            written = write_files(operations, folder_path)
            for f in written:
                print_ok(f"Fixed: {f}")
        else:
            print("\n--- AI Response ---")
            print(response)
            print("-------------------")
        record_usage(config, model_id, input_tokens, output_tokens)
        save_config(config)
    except Exception as e:
        print_err(f"API call failed: {e}")


def cmd_translate(model_alias: str, filepath: str, target_lang: str):
    config = load_config()
    folder_path = config.get("folder_path")
    if not folder_path:
        print_err("No project folder set.")
        sys.exit(1)

    model_id, provider = resolve_model(model_alias)
    if provider == "unknown":
        print_err(f"Unknown model: {model_alias}")
        sys.exit(1)

    target = Path(folder_path) / filepath
    if not target.exists():
        print_err(f"File not found: {filepath}")
        sys.exit(1)

    content = target.read_text(encoding="utf-8", errors="replace")
    ext_map = {
        "python": ".py", "javascript": ".js", "typescript": ".ts",
        "java": ".java", "go": ".go", "rust": ".rs", "cpp": ".cpp",
        "c": ".c", "ruby": ".rb", "php": ".php", "kotlin": ".kt",
    }
    new_ext = ext_map.get(target_lang.lower(), f".{target_lang.lower()}")
    new_name = target.stem + new_ext

    prompt = (
        f"Translate this code from its current language to {target_lang}. "
        f"Keep the same logic and functionality. Output as FILE: {new_name}\n\n"
        f"Original file ({filepath}):\n{content}"
    )

    backup_project(folder_path)
    print_info(f"Translating {filepath} to {target_lang}...")
    try:
        response, input_tokens, output_tokens = call_model(config, provider, model_id, prompt)
        operations = parse_ai_response(response, folder_path)
        if operations:
            written = write_files(operations, folder_path)
            for f in written:
                print_ok(f"Created: {f}")
        else:
            print(response)
        record_usage(config, model_id, input_tokens, output_tokens)
        save_config(config)
    except Exception as e:
        print_err(f"API call failed: {e}")


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
            cost_str = f"${cost:.6f}"
        else:
            cost = 0.0
            cost_str = "$0.000000 (local)"
        total_cost += cost
        rows.append((model_id, inp, out, cost_str))

    folder = config.get("folder_path", "unknown")
    print(f"\nProject cost report: {folder}")
    print("-" * 65)
    print(f"{'Model':<35} {'In tokens':>10} {'Out tokens':>10}  {'Cost':>12}")
    print("-" * 65)
    for model_id, inp, out, cost_str in rows:
        print(f"{model_id:<35} {inp:>10,} {out:>10,}  {cost_str:>12}")
    print("-" * 65)
    print(f"{'TOTAL':<57}  ${total_cost:.6f}")
    print()


def cmd_demo():
    global DEMO_MODE
    DEMO_MODE = not DEMO_MODE
    state = "ON" if DEMO_MODE else "OFF"
    print_ok(f"Demo mode {state} — output is now {'slow and dramatic' if DEMO_MODE else 'normal speed'}.")


def cmd_help():
    print("""
Progter v0.2 - AI-powered terminal code assistant

SETUP
  <provider> "<api_key>"              Set API key for a provider
    Providers: anthropic, openai, google, mistral, deepseek,
               xai, cohere, groq, perplexity, kimi, qwen, llama, siliconflow

  folderpath "<path>"                 Set the project folder
  ollama "<url>"                      Set Ollama server URL
  ollama_add <model>                  Register a local Ollama model

GENERATE
  <model> "<prompt>"                  Generate or modify files
  plan <model> "<prompt>"             Plan mode: AI explains before executing
  multiprompt <m1> <m2> ... "<prompt>"  Run multiple AIs on same prompt

LIFEHACKS
  chat <model>                        Chat with AI about your project
  explain <model> <file>              AI explains a file
  fix <model> [file]                  AI fixes bugs in file or whole project
  translate <model> <file> <lang>     Rewrite file in another language

PROJECT
  status                              Show project files, sizes, line counts
  undo                                Restore project to previous state
  rules "<rule>"                      Add a rule for all AI prompts
  rules                               List current rules
  rules "remove <number>"             Remove a rule

OTHER
  hmmtpc                              Show project cost in $ (6 decimal places)
  demo                                Toggle demo mode (for YouTube recordings)
  help                                Show this help message
""")


# ─── Entry point ──────────────────────────────────────────────────────────────

PROVIDERS = {
    "anthropic", "openai", "google", "mistral",
    "deepseek", "xai", "cohere", "groq", "perplexity",
    "kimi", "qwen", "llama", "siliconflow",
}


def main():
    global DEMO_MODE
    args = sys.argv[1:]

    if not args:
        cmd_help()
        return

    command = args[0].lower()

    if command == "help":
        cmd_help()

    elif command == "hmmtpc":
        cmd_hmmtpc()

    elif command == "status":
        cmd_status()

    elif command == "undo":
        cmd_undo()

    elif command == "demo":
        cmd_demo()

    elif command == "folderpath":
        if len(args) < 2:
            print_err("Usage: progter folderpath \"your/path\"")
            sys.exit(1)
        cmd_folderpath(args[1])

    elif command == "ollama":
        if len(args) < 2:
            print_err("Usage: progter ollama \"http://localhost:11434\"")
            sys.exit(1)
        cmd_ollama_url(args[1])

    elif command == "ollama_add":
        if len(args) < 2:
            print_err("Usage: progter ollama_add <model_name>")
            sys.exit(1)
        cmd_ollama_add(args[1])

    elif command == "rules":
        rule = args[1] if len(args) >= 2 else None
        cmd_rules(rule)

    elif command == "plan":
        if len(args) < 3:
            print_err("Usage: progter plan <model> \"prompt\"")
            sys.exit(1)
        cmd_generate(args[1], args[2], plan_mode=True)

    elif command == "multiprompt":
        if len(args) < 3:
            print_err("Usage: progter multiprompt <model1> <model2> ... \"prompt\"")
            sys.exit(1)
        prompt = args[-1]
        models = args[1:-1]
        cmd_multiprompt(models, prompt)

    elif command == "chat":
        if len(args) < 2:
            print_err("Usage: progter chat <model>")
            sys.exit(1)
        cmd_chat(args[1])

    elif command == "explain":
        if len(args) < 3:
            print_err("Usage: progter explain <model> <file>")
            sys.exit(1)
        cmd_explain(args[1], args[2])

    elif command == "fix":
        if len(args) < 2:
            print_err("Usage: progter fix <model> [file]")
            sys.exit(1)
        filepath = args[2] if len(args) >= 3 else None
        cmd_fix(args[1], filepath)

    elif command == "translate":
        if len(args) < 4:
            print_err("Usage: progter translate <model> <file> <language>")
            sys.exit(1)
        cmd_translate(args[1], args[2], args[3])

    elif command in PROVIDERS:
        if len(args) < 2:
            print_err(f"Usage: progter {command} \"your-api-key\"")
            sys.exit(1)
        cmd_set_api(command, args[1])

    elif len(args) >= 2:
        cmd_generate(args[0], args[1])

    else:
        print_err(f"Unknown command: {command}")
        print_info("Run 'progter help' to see available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()

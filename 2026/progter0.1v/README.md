# Progter

AI-powered terminal code assistant. Inspired by Cursor, built for people who live in the terminal.

## Installation

```bash
git clone https://github.com/you/progter
cd progter
pip install -e . --break-system-packages
```

## Quick Start

```bash
# 1. Set your API keys (only the ones you want to use)
progter anthropic "sk-ant-..."
progter openai "sk-..."
progter google "AIza..."
progter mistral "..."
progter deepseek "..."
progter xai "..."
progter cohere "..."
progter groq "..."
progter perplexity "..."

# 2. Set project folder
progter folderpath "/home/user/myproject"

# 3. Generate code
progter claude_sonnet4.6 "create main.py with a FastAPI REST API"
progter chatgpt "add JWT authentication to main.py"
progter gemini_2.5 "write unit tests for all endpoints"
progter codestral "refactor and improve code style"

# Ollama (local models, no API key needed)
progter ollama "http://localhost:11434"
progter ollama_add llama3
progter ollama_llama3 "add docstrings to all functions"

# Check project cost
progter hmmtpc

# Help
progter help
```

## How it works

1. When you run a generation command, Progter reads all files in your project folder
2. It sends the full project context to the AI along with your prompt
3. The AI returns modified or new files
4. Progter writes those files to disk — modifying existing ones, never duplicating

This means you can use different AI models on the same project freely. Claude writes the base, GPT-4o adds auth, Codestral cleans up style — all editing the same files without conflicts.

## Supported Models

| Alias | Model | Provider |
|---|---|---|
| claude_sonnet4.6 | claude-sonnet-4-6 | Anthropic |
| claude_opus4.6 | claude-opus-4-6 | Anthropic |
| claude_haiku4.5 | claude-haiku-4-5 | Anthropic |
| chatgpt / gpt4o | gpt-4o | OpenAI |
| gpt4o_mini | gpt-4o-mini | OpenAI |
| o3 | o3 | OpenAI |
| gemini / gemini_2.5 | gemini-2.5-pro | Google |
| gemini_2.5_flash | gemini-2.5-flash | Google |
| mistral / mistral_large3 | mistral-large-latest | Mistral |
| mistral_small4 | mistral-small-latest | Mistral |
| codestral | codestral-latest | Mistral |
| devstral | devstral-latest | Mistral |
| magistral | magistral-medium-latest | Mistral |
| deepseek / deepseek_v4 | deepseek-chat | DeepSeek |
| deepseek_r2 | deepseek-reasoner | DeepSeek |
| grok / grok_4 | grok-4 | xAI |
| cohere / command_r_plus | command-r-plus | Cohere |
| groq / groq_llama | llama-3.3-70b-versatile | Groq |
| perplexity / sonar_pro | sonar-pro | Perplexity |
| ollama_<name> | any local model | Ollama |

## Config location

Config is stored at `~/.progter/config.json`

# Progter

AI-powered terminal code assistant. Inspired by Cursor, built for people who live in the terminal.

> Free. The only limit is your API budget.

## Installation

```bash
git clone https://github.com/you/progter
cd progter
pip install -e .
```

On Linux:
```bash
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
progter groq "..."
progter kimi "..."
progter qwen "..."
progter llama "..."
progter siliconflow "..."

# 2. Set project folder
progter folderpath "C:/Users/you/myproject"

# 3. Generate code
progter claude_sonnet4_6 "create main.py with a FastAPI REST API"
progter chatgpt "add JWT authentication to main.py"
progter gemini_2_5 "write unit tests for all endpoints"
progter codestral "refactor and improve code style"
```

## Commands

### Generate
```bash
progter <model> "<prompt>"                        # generate or modify files
progter plan <model> "<prompt>"                   # AI explains what it will do before executing
progter multiprompt <m1> <m2> <m3> "<prompt>"    # run multiple AIs on the same prompt
```

### Lifehacks
```bash
progter chat <model>                    # chat with AI about your project
progter explain <model> <file>          # AI explains what a file does
progter fix <model> [file]              # AI finds and fixes bugs
progter translate <model> <file> <lang> # rewrite file in another language
```

### Project
```bash
progter status                          # show all files with sizes and line counts
progter undo                            # restore project to previous state
progter rules "<rule>"                  # add a rule applied to every AI prompt
progter rules                           # list current rules
progter rules "remove <number>"         # remove a rule
```

### Setup
```bash
progter folderpath "<path>"             # set project folder
progter ollama "<url>"                  # set Ollama server URL
progter ollama_add <model>              # register a local Ollama model
```

### Other
```bash
progter hmmtpc                          # show total project cost in $
progter demo                            # toggle demo mode (for YouTube recordings)
progter help                            # show help
```

## How it works

1. You run a generation command
2. Progter reads all files in your project folder
3. It sends the full project context to the AI along with your prompt
4. The AI returns modified or new files
5. Progter writes those files to disk — modifying existing ones, never duplicating

This means you can use different AI models on the same project freely. Claude writes the base, GPT-4o adds auth, Codestral cleans up style — all editing the same files without conflicts.

## Supported Models

### Anthropic
| Alias | Model |
|---|---|
| claude / claude_sonnet4_6 | claude-sonnet-4-6 |
| claude_opus4_6 | claude-opus-4-6 |
| claude_haiku4_5 | claude-haiku-4-5 |

### OpenAI
| Alias | Model |
|---|---|
| chatgpt / gpt4o | gpt-4o |
| gpt4o_mini | gpt-4o-mini |
| o3 | o3 |

### Google
| Alias | Model |
|---|---|
| gemini / gemini_2_5 | gemini-2.5-pro |
| gemini_2_5_flash | gemini-2.5-flash |

### Mistral
| Alias | Model |
|---|---|
| mistral / mistral_large3 | mistral-large-latest |
| mistral_small4 | mistral-small-latest |
| codestral | codestral-latest |
| devstral | devstral-latest |
| magistral | magistral-medium-latest |

### DeepSeek
| Alias | Model |
|---|---|
| deepseek / deepseek_v4 | deepseek-chat |
| deepseek_r2 | deepseek-reasoner |

### xAI
| Alias | Model |
|---|---|
| grok / grok_4 | grok-4 |
| grok_4_1 | grok-4-1-fast-non-reasoning |

### Kimi (Moonshot AI)
| Alias | Model |
|---|---|
| kimi / kimi_k2_6 | kimi-k2.6 |
| kimi_k2_5 | kimi-k2.5 |

### Qwen (Alibaba)
| Alias | Model |
|---|---|
| qwen / qwen_max | qwen-max |
| qwen_plus | qwen-plus |
| qwen_turbo | qwen-turbo |
| qwen_coder | qwen-coder-plus |
| qwen3 | qwen3-235b-a22b |

### Meta Llama
| Alias | Model |
|---|---|
| llama / llama4 | Llama-4-Maverick |
| llama4_scout | Llama-4-Scout |
| llama3_3 | Llama-3.3-70B |

### SiliconFlow (one key, 30+ models)
| Alias | Model |
|---|---|
| sf_kimi | moonshotai/Kimi-K2.6 |
| sf_deepseek_v4 | DeepSeek-V4-Pro |
| sf_deepseek_flash | DeepSeek-V4-Flash |
| sf_qwen3 | Qwen3-235B-A22B |
| sf_qwen_coder | Qwen2.5-Coder-32B |
| sf_glm5 | GLM-5.1 |
| sf_glm4_6 | GLM-4.6 |
| sf_llama4 | Llama-4-Maverick |
| sf_gemma4 | gemma-4-31b |
| sf_minimax | MiniMax-M2.5 |
| + more | run `progter help` |

### Groq
| Alias | Model |
|---|---|
| groq / groq_llama | llama-3.3-70b-versatile |

### Perplexity
| Alias | Model |
|---|---|
| perplexity / sonar_pro | sonar-pro |
| sonar | sonar |

### Ollama (local, free)
```bash
ollama pull llama3
progter ollama_add llama3
progter ollama_llama3 "create main.py"
```

## Config

Stored at `~/.progter/config.json` (Windows: `C:\Users\you\.progter\config.json`)

API keys are stored locally on your machine only.

## Contributing

Pull requests are welcome. For major changes please open an issue first.

Things that would be great to add:
- IDE integration (inline suggestions in Neovim/VS Code)
- Streaming output (see AI response as it types)
- `progter diff` — show what AI changed before writing
- Support for more providers

## License

MIT

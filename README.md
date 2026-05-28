Progter
AI-powered terminal code assistant. Inspired by Cursor, built for people who live in the terminal.

Free. The only limit is your API budget.

Installation
bashgit clone https://github.com/Polishmatixs/progter
cd progter
pip install -e .
On Linux:
bashpip install -e . --break-system-packages
Quick Start
bash# 1. Set your API keys (only the ones you want to use)
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
Commands
Generate
bashprogter <model> "<prompt>"                        # generate or modify files
progter plan <model> "<prompt>"                   # AI explains what it will do before executing
progter multiprompt <m1> <m2> <m3> "<prompt>"    # run multiple AIs on the same prompt
Lifehacks
bashprogter chat <model>                    # chat with AI about your project
progter explain <model> <file>          # AI explains what a file does
progter fix <model> [file]              # AI finds and fixes bugs
progter translate <model> <file> <lang> # rewrite file in another language
Project
bashprogter status                          # show all files with sizes and line counts
progter undo                            # restore project to previous state
progter rules "<rule>"                  # add a rule applied to every AI prompt
progter rules                           # list current rules
progter rules "remove <number>"         # remove a rule
Setup
bashprogter folderpath "<path>"             # set project folder
progter ollama "<url>"                  # set Ollama server URL
progter ollama_add <model>              # register a local Ollama model
Other
bashprogter hmmtpc                          # show total project cost in $
progter demo                            # toggle demo mode (for YouTube recordings)
progter help                            # show help
How it works

You run a generation command
Progter reads all files in your project folder
It sends the full project context to the AI along with your prompt
The AI returns modified or new files
Progter writes those files to disk — modifying existing ones, never duplicating

This means you can use different AI models on the same project freely. Claude writes the base, GPT-4o adds auth, Codestral cleans up style — all editing the same files without conflicts.
Supported Models
Anthropic
AliasModelclaude / claude_sonnet4_6claude-sonnet-4-6claude_opus4_6claude-opus-4-6claude_haiku4_5claude-haiku-4-5
OpenAI
AliasModelchatgpt / gpt4ogpt-4ogpt4o_minigpt-4o-minio3o3
Google
AliasModelgemini / gemini_2_5gemini-2.5-progemini_2_5_flashgemini-2.5-flash
Mistral
AliasModelmistral / mistral_large3mistral-large-latestmistral_small4mistral-small-latestcodestralcodestral-latestdevstraldevstral-latestmagistralmagistral-medium-latest
DeepSeek
AliasModeldeepseek / deepseek_v4deepseek-chatdeepseek_r2deepseek-reasoner
xAI
AliasModelgrok / grok_4grok-4grok_4_1grok-4-1-fast-non-reasoning
Kimi (Moonshot AI)
AliasModelkimi / kimi_k2_6kimi-k2.6kimi_k2_5kimi-k2.5
Qwen (Alibaba)
AliasModelqwen / qwen_maxqwen-maxqwen_plusqwen-plusqwen_turboqwen-turboqwen_coderqwen-coder-plusqwen3qwen3-235b-a22b
Meta Llama
AliasModelllama / llama4Llama-4-Maverickllama4_scoutLlama-4-Scoutllama3_3Llama-3.3-70B
SiliconFlow (one key, 30+ models)
AliasModelsf_kimimoonshotai/Kimi-K2.6sf_deepseek_v4DeepSeek-V4-Prosf_deepseek_flashDeepSeek-V4-Flashsf_qwen3Qwen3-235B-A22Bsf_qwen_coderQwen2.5-Coder-32Bsf_glm5GLM-5.1sf_glm4_6GLM-4.6sf_llama4Llama-4-Mavericksf_gemma4gemma-4-31bsf_minimaxMiniMax-M2.5+ morerun progter help
Groq
AliasModelgroq / groq_llamallama-3.3-70b-versatile
Perplexity
AliasModelperplexity / sonar_prosonar-prosonarsonar
Ollama (local, free)
bashollama pull llama3
progter ollama_add llama3
progter ollama_llama3 "create main.py"
Config
Stored at ~/.progter/config.json (Windows: C:\Users\you\.progter\config.json)
API keys are stored locally on your machine only.
Contributing
Pull requests are welcome. For major changes please open an issue first.
Things that would be great to add:

IDE integration (inline suggestions in Neovim/VS Code)
Streaming output (see AI response as it types)
progter diff — show what AI changed before writing
Support for more providers

License
MIT

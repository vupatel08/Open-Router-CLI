<div align="center">

# 🤖 OrChat

<img src="https://github.com/user-attachments/assets/df20dccc-8971-414e-9281-74260f05bf44" width="800" alt="OrChat Interface"/>

[![PyPI version](https://img.shields.io/pypi/v/orchat?color=86efac&style=for-the-badge&logo=pypi&logoColor=black)](https://badge.fury.io/py/orchat)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge&logo=opensource&logoColor=white)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-10b981?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Downloads](https://img.shields.io/pypi/dm/orchat?color=1f2937&style=for-the-badge&logo=download&logoColor=white)](https://pepy.tech/project/orchat)
[![GitHub Stars](https://img.shields.io/github/stars/oop7/OrChat?color=86efac&style=for-the-badge&logo=github&logoColor=black)](https://github.com/oop7/OrChat/stargazers)

[🚀 Installation](#installation) • [✨ Features](#features) • [💬 Chat Commands](#chat-commands) • [📁 File Attachment](#file-attachment) • [🧠 Thinking Mode](#thinking-mode) • [⚙️ Configuration](#configuration) • [🔍 Troubleshooting](#troubleshooting) • [🤝 Contributing](#contributing)

A powerful CLI for chatting with AI models through OpenRouter with streaming responses, token tracking, and extensive customization options.

</div>


<a id="features"></a>
## ✨ Features

- **Universal Model Access**: Connect to any AI model available on OpenRouter
- **Interactive Chat**: Enjoy a smooth conversation experience with real-time streaming responses
- **Rich Markdown Rendering**: View formatted text, code blocks, tables and more directly in your terminal
- **Performance Analytics**: Track token usage and response times for cost efficiency
- **Multimodal Support**: Share images and various file types with compatible AI models
- **Smart Thinking Mode**: See the AI's reasoning process with compatible models
- **Enhanced File Processing**: Improved file attachment with better error handling and path support
- **Multiple Export Formats**: Save conversations as Markdown, HTML, JSON, TXT, or PDF
- **Smart Context Management**: Automatically manages conversation history to stay within token limits
- **Customizable Themes**: Choose from different visual themes for your terminal
- **File Attachment Support**: Share files of various types with the AI for analysis

<a id="installation"></a>
## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install orchat
```
```bash
# Run the application
orchat
```

### From Source

```bash
git clone https://github.com/oop7/OrChat.git
pip install -r requirements.txt
python main.py
```

## 📋 Prerequisites

- Python 3.7 or higher
- An OpenRouter API key (get one at [OpenRouter.ai](https://openrouter.ai))
- Required packages: requests, tiktoken, rich, dotenv, colorama

## 🏁 Getting Started

1. Install OrChat using one of the methods above
2. Run the setup wizard
   - if you follow from source PyPI:
     ```bash
     orchat --setup
     ```
   - if you follow from source method:
     ```bash
     python main.py --setup
     ```
3. Enter your OpenRouter API key when prompted
4. Select your preferred AI model and configure settings
5. Start chatting!

## 🪛 Add-Ons

### FZF fuzzy search (Enhanced Model Selection)

1. Install fzf and pyfzf

   - Install pyfzf
     ```bash
     pip install pyfzf
     ```
   - Fzf can be downloaded from https://github.com/junegunn/fzf?tab=readme-ov-file#installation

2. Ensure fzf is in your path
3. From now on, the model selection will use fzf for powerful fuzzy search and filtering capabilities!

<a id="configuration"></a>
## ⚙️ Configuration

OrChat can be configured in multiple ways:

1. **Setup Wizard**: Run `python main.py --setup` for interactive configuration
2. **Config File**: Edit the `config.ini` file in the application directory
3. **Environment Variables**: Create a `.env` file with your configuration
4. **System Environment Variables**: Set environment variables directly in your system (recommended for security)

**Enhanced Environment Support**: OrChat now supports system/user environment variables, removing the strict requirement for `.env` files.

Example `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
```

Example `config.ini` structure:

```ini
[API]
OPENROUTER_API_KEY = your_api_key_here

[SETTINGS]
MODEL = anthropic/claude-3-opus
TEMPERATURE = 0.7
SYSTEM_INSTRUCTIONS = You are a helpful AI assistant.
THEME = default
MAX_TOKENS = 8000
AUTOSAVE_INTERVAL = 300
STREAMING = True
THINKING_MODE = False
```

## 🖥️ Command-Line Options

- `--setup`: Run the setup wizard
- `--model MODEL`: Specify the model to use (e.g., `--model "anthropic/claude-3-opus"`)
- `--task {creative,coding,analysis,chat}`: Optimize for a specific task type
- `--image PATH`: Analyze an image file

<a id="chat-commands"></a>
## 💬 Chat Commands

| Command                   | Description                                           |
| ------------------------- | ----------------------------------------------------- |
| `/help`                   | Show available commands                               |
| `/exit`                   | Exit the chat                                         |
| `/quit`                   | Exit the chat                                         |
| `/new`                    | Start a new conversation                              |
| `/clear`                  | Clear conversation history                            |
| `/cls` or `/clear-screen` | Clear the terminal screen                             |
| `/save [format]`          | Save conversation (formats: md, html, json, txt, pdf) |
| `/model`                  | Change the AI model                                   |
| `/temperature <0.0-2.0>`  | Adjust temperature setting                            |
| `/system`                 | View or change system instructions                    |
| `/tokens`                 | Show token usage statistics                           |
| `/speed`                  | Show response time statistics                         |
| `/theme <theme>`          | Change the color theme (default, dark, light, hacker) |
| `/thinking`               | Show last AI thinking process                         |
| `/thinking-mode`          | Toggle thinking mode on/off                           |
| `/attach` or `/upload`    | Share a file with the AI (can be used anywhere in your message) |
| `/about`                  | Show information about OrChat                         |
| `/update`                 | Check for updates                                     |
| `/settings`               | View current settings                                 |

<a id="file-attachment"></a>
## 📁 File Attachment

Share files with the AI for analysis using the enhanced attachment system:

```
/attach path/to/your/file.ext
/upload path/to/your/file.ext
```

**Enhanced Features:**
- **Flexible Command Usage**: `/upload` and `/attach` can be used anywhere in your message, not just at the beginning
- **Quoted Path Support**: Handles file paths with spaces using quotes (`/attach "C:\path with spaces\file.txt"`)
- **Better Error Handling**: Improved error messages and usage examples
- **File Preview**: Shows file metadata and preview before processing
- **Security Validation**: Built-in file size and type validation (10MB limit)

Supported file types:

- **Images**: JPG, PNG, GIF, WEBP, BMP (displayed visually with multimodal models)
- **Code Files**: Python, JavaScript, Java, C++, TypeScript, Swift, etc. (with syntax highlighting)
- **Text Documents**: TXT, MD, CSV (full content displayed)
- **Data Files**: JSON, XML (displayed with formatting)
- **Web Files**: HTML, CSS (formatted display)
- **Archives**: ZIP, TAR, GZ, RAR (basic metadata support)

<a id="thinking-mode"></a>
## 🧠 Thinking Mode

OrChat can display the AI's reasoning process with enhanced thinking mode:

```
/thinking-mode       # Toggle thinking mode on/off
/thinking            # Show the most recent thinking process
```

**Enhanced Features:**
- **Improved Detection**: Better extraction of thinking content from model responses
- **Model Compatibility**: Automatic handling of models that don't support thinking mode
- **Visual Indicators**: Clear status indicators showing if thinking mode is enabled
- **Flexible Setup**: Option to enable/disable during model selection

This feature allows you to see how the AI approached your question before giving its final answer. Note that thinking mode works best with models that explicitly support `<thinking>` tags.

## 🎨 Themes

Change the visual appearance with the `/theme` command:

- **default**: Blue user, green assistant
- **dark**: Cyan user, magenta assistant
- **light**: Blue user, green assistant with lighter colors
- **hacker**: Matrix-inspired green text on black

## 📊 Token Management

OrChat intelligently manages conversation context to keep within token limits:

- Automatically trims old messages when approaching limits
- Displays token usage statistics after each response
- Allows manual clearing of context with `/clear`

## 🔄 Updates

Check for updates with the `/update` command to see if a newer version is available.

## 🆕 Recent Improvements

**Latest enhancements include:**

- **Enhanced Model Compatibility**: Improved handling of models that don't support system messages (like some Gemma variants)
- **Better Command Parsing**: `/upload` and `/attach` commands can now be used anywhere in your message
- **Improved Code Quality**: Code refinements based on pylint recommendations for better performance
- **Enhanced Environment Support**: Better handling of system environment variables
- **FZF Integration**: Powerful fuzzy search for model selection when fzf is installed
- **Streamlined User Experience**: Added `quit` as alias for `exit` and improved error messages
- **Better File Handling**: Enhanced path handling with support for quoted paths and spaces

<a id="troubleshooting"></a>
## 🔍 Troubleshooting

- **API Key Issues**: Ensure your OpenRouter API key is correctly set in config.ini, .env file, or system environment variables
- **File Path Problems**: When using `/attach` or `/upload`, use quotes for paths with spaces and ensure correct path format for your OS
- **Model Compatibility**: Some features like thinking mode only work with specific models
- **Command Usage**: Remember that `/upload` and `/attach` can be used anywhere in your message for flexibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<a id="contributing"></a>
## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for providing unified API access to AI models
- [Rich](https://github.com/Textualize/rich) for the beautiful terminal interface

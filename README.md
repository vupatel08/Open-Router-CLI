# OrChat

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/oop7/OrChat/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

A powerful CLI for chatting with AI models through OpenRouter.

![OrChat Demo](path/to/demo.gif)

## Features

- **Universal Model Access**: Connect to any AI model available on OpenRouter
- **Interactive Chat**: Enjoy a smooth conversation experience with real-time streaming responses
- **Performance Analytics**: Track token usage and response times
- **Multimodal Support**: Share images and various file types with AI models
- **Extensible Plugin System**: Easily extend functionality with custom plugins
- **Multiple Export Formats**: Save conversations as Markdown, HTML, JSON, TXT, or PDF
- **Smart Context Management**: Automatically manages conversation history to stay within token limits
- **Customizable Themes**: Choose from different visual themes for your terminal

## Installation

### From PyPI (Recommended)

```bash
pip install orchat
```

### From Source

```bash
git clone https://github.com/oop7/OrChat.git
cd orchat
pip install -r requirements.txt
python main.py
```

## Prerequisites

- Python 3.7 or higher
- An OpenRouter API key (get one at [OpenRouter.ai](https://openrouter.ai))

## Getting Started

1. Install OrChat using one of the methods above
2. Run the setup wizard:
   ```bash
   orchat --setup
   ```
3. Enter your OpenRouter API key when prompted
4. Select your preferred AI model and configure settings
5. Start chatting!

## Command-Line Options

- `--setup`: Run the setup wizard
- `--model MODEL`: Specify the model to use
- `--task {creative,coding,analysis,chat}`: Optimize for a specific task type
- `--image PATH`: Analyze an image file

## Chat Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/exit` | Exit the chat |
| `/new` | Start a new conversation |
| `/clear` | Clear conversation history |
| `/save` | Save conversation to file |
| `/model` | Change the AI model |
| `/temperature` | Adjust temperature setting |
| `/system` | View or change system instructions |
| `/tokens` | Show token usage statistics |
| `/speed` | Show response time statistics |
| `/theme` | Change the color theme |
| `/thinking` | Show last AI thinking process |
| `/attach` or `/upload` | Share a file with the AI |
| `/about` | Show information about OrChat |
| `/update` | Check for updates |

## Configuration

OrChat stores configuration in a `config.ini` file in the application directory. You can also use environment variables by creating a `.env` file with:

# OpenRouter CLI

A powerful CLI for chatting with AI models through OpenRouter with streaming responses, token tracking, and extensive customization options.

## Features

<details>
<summary><strong>Core Features</strong></summary>

- **Universal Model Access**: Connect to any AI model available on OpenRouter with dynamic model retrieval
- **Interactive Chat**: Enjoy a smooth conversation experience with real-time streaming responses
- **Rich Markdown Rendering**: View formatted text, code blocks, tables and more directly in your terminal
- **Performance Analytics**: Track token usage, response times, and total cost for efficiency monitoring
- **Command Auto-completion**: Enhanced user experience with intelligent command suggestions and prompt history navigation
- **Prompt History Navigation**: Use ↑/↓ arrow keys to navigate through previous prompts and Ctrl+R for history search
- **Pricing Display**: Real-time pricing information displayed during active chat sessions

</details>

<details>
<summary><strong>File & Media Support</strong></summary>

- **Multimodal Support**: Share images and various file types with compatible AI models
- **Enhanced File Processing**: Improved file attachment with better error handling and path support
- **File Attachment Support**: Share files of various types with the AI for analysis

</details>

<details>
<summary><strong>Advanced Features</strong></summary>

- **Smart Thinking Mode**: See the AI's reasoning process with compatible models
- **Multiple Export Formats**: Save conversations as Markdown, HTML, JSON, TXT, or PDF
- **Smart Context Management**: Automatically manages conversation history to stay within token limits
- **Customizable Themes**: Choose from different visual themes for your terminal

</details>

<details>
<summary><strong>Interactive Input Features</strong></summary>

- **Command History Navigation**: Press ↑/↓ arrow keys to cycle through previous prompts and commands
- **History Search**: Use Ctrl+R to search through your prompt history with keywords
- **Automatic Command Completion**: Start typing "/" and command suggestions appear instantly - no Tab key needed!
- **Auto-Suggest from History**: Previous commands and prompts appear as grey suggestions as you type
- **Intelligent Command Detection**: Commands work anywhere in your message with `/attach` and `/upload`

**How Auto-Completion Works:**
- Type `/` → All available commands appear automatically
- Type `/c` → Filters to commands starting with 'c' (clear, cls, clear-screen, etc.)
- Type `/temp` → Shows `/temperature` command
- Type `/think` → Shows `/thinking` and `/thinking-mode` commands
- No Tab key required - completions appear as you type!

</details>

## Installation

<summary><strong>Installation Methods</strong></summary>

### From Source

```bash
git clone https://github.com/oop7/OrChat.git
pip install -r requirements.txt
python main.py
```

</details>

</details>

<details>
<summary><strong>Prerequisites</strong></summary>

- Python 3.7 or higher
- An OpenRouter API key (get one at [OpenRouter.ai](https://openrouter.ai))
- Required packages: in `requirements.txt`

</details>

<details>
<summary><strong>Getting Started</strong></summary>

1. Install OpenRouter CLI using the method above
2. Run the setup wizard
   ```bash
   python main.py --setup
   ```
3. Enter your OpenRouter API key when prompted
4. Select your preferred AI model and configure settings
5. Start chatting!

</details>

<details>
<summary><strong>Add-Ons</strong></summary>

### FZF fuzzy search (Enhanced Model Selection)

1. Install fzf and pyfzf

   - Install pyfzf
     ```bash
     pip install pyfzf
     ```
   - Fzf can be downloaded from https://github.com/junegunn/fzf?tab=readme-ov-file#installation

2. Ensure fzf is in your path
3. From now on, the model selection will use fzf for powerful fuzzy search and filtering capabilities!

**Note**: If fzf is not installed, OpenRouter CLI will automatically fall back to standard model selection.

</details>

## Configuration

<details>
<summary><strong>Configuration Methods</strong></summary>

OpenRouter CLI can be configured in multiple ways:

1. **Setup Wizard**: Run `python main.py --setup` for interactive configuration
2. **Config File**: Edit the `config.ini` file in the application directory
3. **Environment Variables**: Create a `.env` file with your configuration
4. **System Environment Variables**: Set environment variables directly in your system (recommended for security)

**Enhanced Environment Support**: OpenRouter CLI now supports system/user environment variables, removing the strict requirement for `.env` files.

</details>

<details>
<summary><strong>Configuration Examples</strong></summary>

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

</details>

<details>
<summary><strong>Command-Line Options</strong></summary>

- `--setup`: Run the setup wizard
- `--model MODEL`: Specify the model to use (e.g., `--model "anthropic/claude-3-opus"`)
- `--task {creative,coding,analysis,chat}`: Optimize for a specific task type
- `--image PATH`: Analyze an image file

</details>

## Chat Commands

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
| `/about`                  | Show information about OpenRouter CLI                         |
| `/update`                 | Check for updates                                     |
| `/settings`               | View current settings                                 |

## File Attachment

<details>
<summary><strong>Basic Usage</strong></summary>

Share files with the AI for analysis using the enhanced attachment system:

```
/attach path/to/your/file.ext
/upload path/to/your/file.ext
```

</details>

<details>
<summary><strong>Enhanced Features</strong></summary>

- **Flexible Command Usage**: `/upload` and `/attach` can be used anywhere in your message, not just at the beginning
- **Quoted Path Support**: Handles file paths with spaces using quotes (`/attach "C:\path with spaces\file.txt"`)
- **Better Error Handling**: Improved error messages and usage examples
- **File Preview**: Shows file metadata and preview before processing
- **Security Validation**: Built-in file size and type validation (10MB limit)

</details>

<details>
<summary><strong>Supported File Types</strong></summary>

- **Images**: JPG, PNG, GIF, WEBP, BMP (displayed visually with multimodal models)
- **Code Files**: Python, JavaScript, Java, C++, TypeScript, Swift, etc. (with syntax highlighting)
- **Text Documents**: TXT, MD, CSV (full content displayed)
- **Data Files**: JSON, XML (displayed with formatting)
- **Web Files**: HTML, CSS (formatted display)
- **Archives**: ZIP, TAR, GZ, RAR (basic metadata support)

</details>

## Thinking Mode

<details>
<summary><strong>Basic Usage</strong></summary>

OpenRouter CLI can display the AI's reasoning process with enhanced thinking mode:

```
/thinking-mode       # Toggle thinking mode on/off
/thinking            # Show the most recent thinking process
```

This feature allows you to see how the AI approached your question before giving its final answer. **Auto Thinking Mode** automatically enables this feature when you select models with reasoning support.

</details>

<details>
<summary><strong>Enhanced Features</strong></summary>

- **Improved Detection**: Better extraction of thinking content from model responses
- **Model Compatibility**: Automatic handling of models that don't support thinking mode
- **Visual Indicators**: Clear status indicators showing if thinking mode is enabled
- **Flexible Setup**: Option to enable/disable during model selection

</details>

## Themes

<details>
<summary><strong>Available Themes</strong></summary>

Change the visual appearance with the `/theme` command:

- **default**: Blue user, green assistant
- **dark**: Cyan user, magenta assistant
- **light**: Blue user, green assistant with lighter colors
- **hacker**: Matrix-inspired green text on black

</details>

## Token Management

<details>
<summary><strong>Smart Context Management</strong></summary>

OpenRouter CLI intelligently manages conversation context to keep within token limits:

- Automatically trims old messages when approaching limits
- Displays comprehensive token usage statistics including total tokens and cost tracking
- Shows real-time pricing information during active sessions
- Displays total cost tracking across conversations
- Allows manual clearing of context with `/clear`

</details>

## Updates

<details>
<summary><strong>Version Management</strong></summary>

Check for updates with the `/update` command to see if a newer version is available.

</details>

## Troubleshooting

<details>
<summary><strong>Common Issues & Solutions</strong></summary>

- **API Key Issues**: Ensure your OpenRouter API key is correctly set in config.ini, .env file, or system environment variables. OpenRouter CLI will prompt for re-entry if an incorrect key is detected
- **Insufficient Account Credit**: If you receive a 402 error, check your OpenRouter account balance and add funds as needed
- **File Path Problems**: When using `/attach` or `/upload`, use quotes for paths with spaces and ensure correct path format for your OS
- **Model Compatibility**: Some features like thinking mode only work with specific models
- **Command Usage**: Remember that `/upload` and `/attach` can be used anywhere in your message for flexibility

</details>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

<details>
<summary><strong>Special Thanks</strong></summary>

- [OpenRouter](https://openrouter.ai/) for providing unified API access to AI models
- [Rich](https://github.com/Textualize/rich) for the beautiful terminal interface
- All contributors and users who provide feedback and help improve OpenRouter CLI

</details>

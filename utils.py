import os
import platform

def clear_terminal():
    """Clear the terminal screen based on the operating system."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def format_time_delta(delta_seconds):
    """Format time delta in a human-readable format."""
    if delta_seconds < 60:
        return f"{delta_seconds:.1f}s"
    elif delta_seconds < 3600:
        minutes = delta_seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = delta_seconds / 3600
        return f"{hours:.1f}h"

def format_file_size(size_bytes):
    """Format file size in a human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def count_tokens(text, model_name="cl100k_base"):
    """Counts the number of tokens in a given text string using tiktoken."""
    try:
        import tiktoken
        # tiktoken.encoding_for_model will raise a KeyError if the model is not found.
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default encoding for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        # If tiktoken is not available, estimate tokens (rough approximation)
        return len(text.split()) * 1.3  # Rough estimate: 1.3 tokens per word

    tokens = encoding.encode(text)
    return len(tokens)





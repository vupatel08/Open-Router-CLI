import tiktoken

def count_tokens(text, model_name="cl100k_base"):
    """Counts the number of tokens in a given text string using tiktoken."""
    try:
        # tiktoken.encoding_for_model will raise a KeyError if the model is not found.
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default encoding for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    return len(tokens)

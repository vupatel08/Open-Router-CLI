import os
import base64
import getpass
from cryptography.fernet import Fernet
from rich.console import Console

# Initialize Rich console
console = Console()

def generate_key():
    """Generate a key for encryption"""
    return Fernet.generate_key()

def encrypt_api_key(api_key, key):
    """Encrypt API key using Fernet symmetric encryption"""
    f = Fernet(key)
    encrypted_key = f.encrypt(api_key.encode())
    return encrypted_key

def decrypt_api_key(encrypted_key, key):
    """Decrypt API key using Fernet symmetric encryption"""
    try:
        f = Fernet(key)
        decrypted_key = f.decrypt(encrypted_key)
        return decrypted_key.decode()
    except Exception:
        return None

def get_or_create_master_key():
    """Get or create master encryption key"""
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.key')
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = generate_key()
        # Set restrictive file permissions (Windows compatible)
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Set file permissions to be readable only by owner (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(key_file, 0o600)
        
        return key

def validate_api_key_format(api_key):
    """Validate API key format"""
    if not api_key or len(api_key) < 20:
        return False
    
    # OpenRouter keys typically start with 'sk-or-'
    if not api_key.startswith('sk-or-'):
        console.print("[yellow]Warning: API key doesn't match expected OpenRouter format[/yellow]")
    
    return True

def secure_input_api_key():
    """Securely input API key without echoing to console"""
    try:
        api_key = getpass.getpass("Enter your OpenRouter API key (input hidden): ")
        if not validate_api_key_format(api_key):
            console.print("[red]Invalid API key format[/red]")
            return None
        return api_key
    except KeyboardInterrupt:
        console.print("\n[yellow]API key input cancelled[/yellow]")
        return None

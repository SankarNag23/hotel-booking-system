import os
import json
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_key():
    """Generate a secure encryption key"""
    return Fernet.generate_key()

def encrypt_value(key: bytes, value: str) -> str:
    """Encrypt a value using Fernet encryption"""
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(key: bytes, encrypted_value: str) -> str:
    """Decrypt a value using Fernet encryption"""
    f = Fernet(key)
    return f.decrypt(encrypted_value.encode()).decode()

def setup_google_places_api():
    """Set up Google Places API key with encryption"""
    logger.info("Setting up Google Places API key...")
    
    # Check if .env file exists
    env_path = Path('.env')
    key_path = Path('.key')
    
    # Generate encryption key if it doesn't exist
    if not key_path.exists():
        key = generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
    else:
        with open(key_path, 'rb') as f:
            key = f.read()
    
    if not env_path.exists():
        logger.info("Creating .env file...")
        env_path.touch()
    
    # Read existing .env file
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    if v.startswith('ENC['):
                        v = decrypt_value(key, v[4:-1])
                    env_vars[k] = v
    
    # Get API key from user with validation
    while True:
        api_key = input("Enter your Google Places API key: ").strip()
        if not api_key:
            logger.error("API key cannot be empty")
            continue
        if not api_key.startswith('AIza'):
            logger.warning("Warning: Google API keys typically start with 'AIza'. Please verify your key.")
            if input("Continue anyway? (y/n): ").lower() != 'y':
                continue
        break
    
    # Encrypt and store API key
    encrypted_key = encrypt_value(key, api_key)
    env_vars['GOOGLE_PLACES_API_KEY'] = f"ENC[{encrypted_key}]"
    
    # Set secure permissions for .env file
    with open(env_path, 'w') as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
    try:
        os.chmod(env_path, 0o600)  # Read/write for owner only
        os.chmod(key_path, 0o600)  # Read/write for owner only
    except Exception as e:
        logger.warning(f"Could not set file permissions: {str(e)}")
    
    logger.info("Google Places API key has been securely stored")
    return True

def setup_render_config():
    """Update render.yaml with encrypted API key reference"""
    logger.info("Updating render.yaml configuration...")
    
    render_path = Path('render.yaml')
    if not render_path.exists():
        logger.error("render.yaml not found")
        return False
    
    try:
        with open(render_path, 'r') as f:
            config = f.read()
        
        # Update config to use environment variable
        config = config.replace(
            'value: AIzaSyDxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxX',
            'value: ${GOOGLE_PLACES_API_KEY}'
        )
        
        with open(render_path, 'w') as f:
            f.write(config)
        
        logger.info("render.yaml has been updated to use environment variable")
        return True
    except Exception as e:
        logger.error(f"Error updating render.yaml: {str(e)}")
        return False

def validate_environment():
    """Validate all required environment variables and their format"""
    required_vars = {
        'GOOGLE_PLACES_API_KEY': r'^(ENC\[.+\]|AIza.+)$',
        'API_KEY': r'^[A-Za-z0-9-_=]+$',
        'DEBUG': r'^(True|False)$'
    }
    
    missing = []
    invalid = []
    
    for var, pattern in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif not re.match(pattern, value):
            invalid.append(var)
    
    if missing or invalid:
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
        if invalid:
            logger.error(f"Invalid format for environment variables: {', '.join(invalid)}")
        return False
    return True

def main():
    """Main setup function with enhanced security"""
    logger.info("Starting secure API key setup...")
    
    # Validate current environment
    if not validate_environment():
        logger.warning("Environment validation failed, proceeding with setup...")
    
    # Set up Google Places API
    if setup_google_places_api():
        # Update render.yaml
        if setup_render_config():
            logger.info("\nSetup completed successfully!")
            logger.info("Security notes:")
            logger.info("1. Keep your .env and .key files secure and never commit them")
            logger.info("2. Ensure proper file permissions are set")
            logger.info("3. Regularly rotate your API keys")
            logger.info("\nNext steps:")
            logger.info("1. Commit the changes to your repository (excluding .env and .key)")
            logger.info("2. Set up environment variables in your deployment platform")
            logger.info("3. Run test_hotel_search.py to validate the implementation")
        else:
            logger.error("Failed to update render.yaml")
    else:
        logger.error("Failed to set up Google Places API key")

if __name__ == "__main__":
    main() 
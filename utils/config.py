import os
import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "generator": {
        "default_length": 16,
        "default_count": 1,
        "use_uppercase": True,
        "use_lowercase": True,
        "use_digits": True,
        "use_symbols": True
    },
    "output": {
        "json_output": False,
        "color_output": True
    },
    "security": {
        "check_hibp": False,
        "hibp_timeout": 5,
        "cache_enabled": True,
        "cache_expiration_days": 30
    },
    "logging": {
        "level": "INFO",
        "console_output": False,
        "file_output": True
    },
    "performance": {
        "batch_processing_threads": 4
    }
}

def GetConfigPath():
    """Get the path to the config file"""
    # Use user's home directory
    home = Path.home()
    config_dir = home / ".passaudit"
    config_file = config_dir / "config.json"
    return config_dir, config_file

def LoadConfig():
    """Load configuration from file or return defaults"""
    config_dir, config_file = GetConfigPath()

    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Merge with defaults (in case new options are added)
                config = DEFAULT_CONFIG.copy()
                for section in user_config:
                    if section in config:
                        config[section].update(user_config[section])
                    else:
                        config[section] = user_config[section]
                return config
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()

def SaveConfig(config):
    """Save configuration to file"""
    config_dir, config_file = GetConfigPath()

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def InitializeConfig():
    """Create default config file if it doesn't exist"""
    config_dir, config_file = GetConfigPath()

    if not config_file.exists():
        print(f"Creating default configuration at {config_file}")
        config_dir.mkdir(parents=True, exist_ok=True)
        return SaveConfig(DEFAULT_CONFIG)
    return True

def ShowConfig():
    """Display current configuration"""
    config = LoadConfig()
    config_dir, config_file = GetConfigPath()

    print(f"Configuration file: {config_file}")
    print("\nCurrent settings:")
    print(json.dumps(config, indent=2))

def UpdateConfigValue(section, key, value):
    """Update a specific configuration value"""
    config = LoadConfig()

    if section not in config:
        config[section] = {}

    # Convert string values to appropriate types
    if isinstance(value, str):
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)

    config[section][key] = value

    if SaveConfig(config):
        print(f"Updated {section}.{key} = {value}")
        return True
    return False

def ResetConfig():
    """Reset configuration to defaults"""
    if SaveConfig(DEFAULT_CONFIG):
        print("Configuration reset to defaults")
        return True
    return False

"""
Example usage of the ConfigurationService class.

This file demonstrates how to use the ConfigurationService for
accessing and modifying application settings.
"""

from qt_version.utils.configuration_service import ConfigurationService

def main():
    # Get the singleton instance
    config = ConfigurationService()
    
    # Get settings with type hints
    model = config.get_typed("llm_model", str, "gpt-4o-mini")
    temperature = config.get_typed("temperature", float, 0.7)
    debug_mode = config.get_typed("debug_mode", bool, False)
    
    print(f"Current LLM Model: {model}")
    print(f"Temperature: {temperature}")
    print(f"Debug Mode: {debug_mode}")
    
    # Set a setting with validation
    success = config.set("temperature", 0.8)
    if success:
        print("Temperature updated successfully")
    else:
        print("Failed to update temperature")
    
    # Get a complex setting (dictionary)
    font_settings = config.get_typed("live_text_font", dict, {})
    print(f"Font Settings: {font_settings}")
    
    # Reset a setting to default
    config.reset("temperature")
    print(f"Reset temperature to: {config.get('temperature')}")
    
    # Export settings to a file
    config.export_settings("settings_backup.json")
    print("Settings exported to settings_backup.json")

if __name__ == "__main__":
    main()

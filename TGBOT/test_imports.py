#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""
try:
    print("Testing imports...")
    
    # Test basic imports
    from aiogram import Router, types, F
    print("✅ aiogram imported")
    
    from handlers import instructions as instructions_handlers
    print("✅ instructions handlers imported")
    
    from handlers import main_menu as main_menu_handlers
    print("✅ main_menu handlers imported")
    
    from keyboards import main_menu_after_auth_keyboard
    print("✅ keyboards imported")
    
    # Test keyboard creation
    keyboard = main_menu_after_auth_keyboard()
    print("✅ keyboard created successfully")
    
    # Check if instructions button exists
    keyboard_text = str(keyboard)
    if "📚 Инструкции" in keyboard_text:
        print("✅ Instructions button found in keyboard")
    else:
        print("❌ Instructions button NOT found in keyboard")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
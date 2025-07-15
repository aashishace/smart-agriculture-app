#!/usr/bin/env python3
"""
Test script to verify translation system
"""

import os
import sys
sys.path.append('.')

def test_translations():
    from app import create_app
    from flask_babel import get_locale, gettext as _
    
    app = create_app()
    
    print("🧪 Testing Translation System")
    print("=" * 40)
    
    # Test Hindi context
    with app.test_request_context('/?lang=hi'):
        print(f"Hindi context - Locale: {get_locale()}")
        print(f"Dashboard: {_('Dashboard')}")
        print(f"Crops: {_('Crops')}")
        print(f"Weather: {_('Weather')}")
        print(f"Help: {_('Help')}")
    
    print()
    
    # Test English context  
    with app.test_request_context('/?lang=en'):
        print(f"English context - Locale: {get_locale()}")
        print(f"Dashboard: {_('Dashboard')}")
        print(f"Crops: {_('Crops')}")
        print(f"Weather: {_('Weather')}")
        print(f"Help: {_('Help')}")
    
    print("\n✅ Translation test complete!")

if __name__ == "__main__":
    test_translations()

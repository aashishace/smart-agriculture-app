#!/usr/bin/env python3
"""
Manual Translation Compiler and Fixer
"""

import os
import re
import json
from babel.messages.pofile import read_po, write_po
from babel.messages.mofile import write_mo
from babel.messages.catalog import Catalog

def fix_hindi_translations():
    """Add missing Hindi translations to the PO file."""
    
    # Critical translations that need to be filled
    translations = {
        "Dashboard": "डैशबोर्ड",
        "Farms": "खेत", 
        "Crops": "फसलें",
        "Disease Scanner": "रोग स्कैनर",
        "Profile": "प्रोफाइल",
        "Help": "सहायता",
        "Logout": "लॉगआउट",
        "Login": "लॉगिन",
        "Register": "पंजीकरण",
        "Home": "होम",
        "Weather": "मौसम",
        "Clear": "साफ",
        "Smart Crop Care Assistant": "स्मार्ट फसल देखभाल सहायक",
        "Getting Started": "शुरुआत करें",
        "Add your farm first to get smart crop care recommendations": "स्मार्ट फसल देखभाल सुझाव पाने के लिए पहले अपना खेत जोड़ें",
        "Start Setup": "सेटअप शुरू करें",
        "Total Farms": "कुल खेत",
        "Active Crops": "सक्रिय फसलें", 
        "Weather Alerts": "मौसम अलर्ट",
        "No tasks for today!": "आज कोई काम नहीं है!",
        "Quick Actions": "त्वरित कार्य",
        "Add Farm": "खेत जोड़ें",
        "Add Crop": "फसल जोड़ें", 
        "Scan Disease": "रोग स्कैन करें",
        "View Crops": "फसलें देखें",
        "Help & Support": "सहायता और समर्थन",
        "Schedule Irrigation": "सिंचाई शेड्यूल करें",
        "Weather Information": "मौसम की जानकारी",
        "Humidity": "नमी",
        "Wind Speed": "हवा की गति",
        "Rain Forecast": "बारिश की संभावना",
        "Contact": "संपर्क",
        "About": "हमारे बारे में",
        "Settings": "सेटिंग्स",
        "Save": "सेव करें",
        "Cancel": "रद्द करें",
        "Submit": "सबमिट करें",
        "Back": "वापस",
        "Next": "अगला",
        "Previous": "पिछला",
        "Edit": "संपादित करें",
        "Delete": "हटाएं",
        "Add": "जोड़ें",
        "Remove": "हटाएं",
        "Update": "अपडेट करें",
        "Create": "बनाएं",
        "Search": "खोज",
        "Filter": "फिल्टर",
        "Sort": "क्रमबद्ध करें",
        "English": "अंग्रेजी",
        "Hindi": "हिंदी",
        "Language": "भाषा",
        "Select Language": "भाषा चुनें",
        "Farm Name": "खेत का नाम",
        "Crop Type": "फसल का प्रकार",
        "Area": "क्षेत्रफल",
        "Location": "स्थान",
        "Date": "तारीख",
        "Time": "समय",
        "Status": "स्थिति",
        "Active": "सक्रिय",
        "Inactive": "निष्क्रिय",
        "Completed": "पूर्ण",
        "Pending": "बकाया",
        "Success": "सफलता",
        "Error": "त्रुटि",
        "Warning": "चेतावनी",
        "Information": "जानकारी",
        "Yes": "हाँ",
        "No": "नहीं",
        "OK": "ठीक है",
        "Close": "बंद करें",
        "Open": "खोलें",
        "New": "नया",
        "Today": "आज",
        "Yesterday": "कल",
        "Tomorrow": "कल",
        "Week": "सप्ताह",
        "Month": "महीना",
        "Year": "साल",
        "Loading...": "लोड हो रहा है...",
        "Please wait...": "कृपया प्रतीक्षा करें...",
        "No data available": "कोई डेटा उपलब्ध नहीं",
        "No results found": "कोई परिणाम नहीं मिला",
        "State": "राज्य",
        "Select State": "राज्य चुनें",
        "Uttar Pradesh": "उत्तर प्रदेश",
        "Bihar": "बिहार",
        "Madhya Pradesh": "मध्य प्रदेश",
        "Rajasthan": "राजस्थान",
        "Punjab": "पंजाब",
        "Haryana": "हरियाणा",
        "Maharashtra": "महाराष्ट्र",
        "Karnataka": "कर्नाटक",
        "Tamil Nadu": "तमिल नाडु",
        "Andhra Pradesh": "आंध्र प्रदेश",
        "West Bengal": "पश्चिम बंगाल",
        "Gujarat": "गुजरात",
        "Odisha": "ओडिशा",
        "Telangana": "तेलंगाना",
        "Kerala": "केरल",
        "Jharkhand": "झारखंड",
        "Assam": "असम",
        "Chhattisgarh": "छत्तीसगढ़",
        "Uttarakhand": "उत्तराखंड",
        "Himachal Pradesh": "हिमाचल प्रदेश",
        "Jammu Kashmir": "जम्मू कश्मीर",
        "Other": "अन्य",
        "Full Name": "पूरा नाम",
        "Your full name": "आपका पूरा नाम",
        "Mobile Number": "मोबाइल नंबर",
        "10 digit Indian mobile number": "10 अंकों का भारतीय मोबाइल नंबर",
        "Village/City": "गाँव/शहर",
        "Your village or city": "आपका गाँव या शहर",
        "Password": "पासवर्ड",
        "Your password": "आपका पासवर्ड",
        "At least 6 characters": "कम से कम 6 अक्षर",
        "Confirm Password": "पासवर्ड दोबारा दर्ज करें",
        "Re-enter password": "पासवर्ड दोबारा दर्ज करें",
        "By registering you agree to our": "पंजीकरण करके आप हमारी शर्तों से सहमत हैं",
        "Terms": "नियम",
        "and": "और",
        "Privacy Policy": "गोपनीयता नीति",
        "Already have an account?": "क्या आपका पहले से खाता है?",
        "New user?": "नए उपयोगकर्ता?",
        "Remember me": "मुझे याद रखें",
        "Forgot password?": "पासवर्ड भूल गए?",
        "Or": "या",
        "create a new account": "नया खाता बनाएं",
        "Welcome": "स्वागत है",
        "Smart Agriculture Dashboard": "स्मार्ट कृषि डैशबोर्ड",
        "Today's Date": "आज की तारीख",
        "Making agriculture easier for Indian farmers with smart technology.": "स्मार्ट तकनीक के साथ भारतीय किसानों के लिए कृषि को आसान बनाना।",
        "Services": "सेवाएं",
        "Smart Irrigation": "स्मार्ट सिंचाई",
        "Disease Detection": "रोग की पहचान",
        "Crop Management": "फसल प्रबंधन",
        "acres": "एकड़",
        "Farm Location": "खेत का स्थान",
        "Planting Date": "रोपण तारीख",
        "Soil Type": "मिट्टी का प्रकार",
        "Clay Soil": "चिकनी मिट्टी",
        "Sandy Soil": "बलुई मिट्टी",
        "Loam Soil": "दोमट मिट्टी",
        "Black Soil": "काली मिट्टी",
        "Red Soil": "लाल मिट्टी"
    }
    
    hi_po_path = "app/translations/hi/LC_MESSAGES/messages.po"
    
    try:
        # Read current content
        with open(hi_po_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_count = 0
        
        # Update each translation
        for english, hindi in translations.items():
            # Pattern to match msgid followed by empty msgstr
            pattern = rf'msgid "{re.escape(english)}"\nmsgstr ""'
            replacement = f'msgid "{english}"\nmsgstr "{hindi}"'
            
            # Check if this translation exists and is empty
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated_count += 1
                print(f"Updated: {english} -> {hindi}")
        
        # Write back to file
        with open(hi_po_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Updated {updated_count} Hindi translations")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Hindi translations: {e}")
        return False

def compile_translations():
    """Compile .po files to .mo files."""
    print("\n🔧 Compiling translation files...")
    
    translations_compiled = 0
    
    # Compile Hindi translations
    hi_po_path = "app/translations/hi/LC_MESSAGES/messages.po"
    hi_mo_path = "app/translations/hi/LC_MESSAGES/messages.mo"
    
    if os.path.exists(hi_po_path):
        try:
            with open(hi_po_path, 'rb') as f:
                catalog = read_po(f)
            
            with open(hi_mo_path, 'wb') as f:
                write_mo(f, catalog)
            
            print(f"✅ Compiled Hindi translations: {hi_mo_path}")
            translations_compiled += 1
            
        except Exception as e:
            print(f"❌ Error compiling Hindi: {e}")
    else:
        print(f"❌ Hindi PO file not found: {hi_po_path}")
    
    # Compile English translations
    en_po_path = "app/translations/en/LC_MESSAGES/messages.po"
    en_mo_path = "app/translations/en/LC_MESSAGES/messages.mo"
    
    if os.path.exists(en_po_path):
        try:
            with open(en_po_path, 'rb') as f:
                catalog = read_po(f)
            
            with open(en_mo_path, 'wb') as f:
                write_mo(f, catalog)
            
            print(f"✅ Compiled English translations: {en_mo_path}")
            translations_compiled += 1
            
        except Exception as e:
            print(f"❌ Error compiling English: {e}")
    else:
        print(f"❌ English PO file not found: {en_po_path}")
    
    return translations_compiled > 0

def create_test_translation_app():
    """Create a test script to verify translations work."""
    test_script = '''#!/usr/bin/env python3
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
    
    print("\\n✅ Translation test complete!")

if __name__ == "__main__":
    test_translations()
'''
    
    with open("test_translations.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created translation test script: test_translations.py")

def update_config_if_needed():
    """Update config.py with translation settings if needed."""
    print("\n🔧 Checking config.py...")
    
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'LANGUAGES' not in content:
            print("⚠️ LANGUAGES config not found in config.py")
            print("Please add this to your config.py in the appropriate config class:")
            print("""
    # Translation Configuration
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिंदी'
    }
    BABEL_DEFAULT_LOCALE = 'hi'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Kolkata'
""")
        else:
            print("✅ Translation config found in config.py")
            
    except Exception as e:
        print(f"❌ Error checking config.py: {e}")

def main():
    """Main function to fix translations comprehensively."""
    print("🚀 Smart Agriculture Translation Fix")
    print("=" * 50)
    
    # Step 1: Fix Hindi translations
    print("\n📝 Step 1: Fixing Hindi translations...")
    if fix_hindi_translations():
        print("✅ Hindi translations updated successfully")
    else:
        print("❌ Failed to update Hindi translations")
    
    # Step 2: Compile translations
    print("\n🔧 Step 2: Compiling translations...")
    if compile_translations():
        print("✅ Translations compiled successfully")
    else:
        print("❌ Failed to compile translations")
    
    # Step 3: Check config
    update_config_if_needed()
    
    # Step 4: Create test script
    print("\n🧪 Step 4: Creating test script...")
    create_test_translation_app()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Translation Fix Complete!")
    print("\n📋 Next Steps:")
    print("1. Run: python test_translations.py")
    print("2. Restart your Flask application")
    print("3. Test language switching in browser")
    print("4. Check both Hindi and English pages")
    
    # Check if MO files were created
    hi_mo = "app/translations/hi/LC_MESSAGES/messages.mo"
    en_mo = "app/translations/en/LC_MESSAGES/messages.mo"
    
    print("\n📁 Translation Files Status:")
    print(f"Hindi .mo file: {'✅' if os.path.exists(hi_mo) else '❌'} {hi_mo}")
    print(f"English .mo file: {'✅' if os.path.exists(en_mo) else '❌'} {en_mo}")

if __name__ == "__main__":
    main()

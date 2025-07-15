#!/usr/bin/env python3
"""
Script to add Hindi translations for Help page and other missing translations
"""

import re

def update_hindi_translations():
    po_file_path = 'app/translations/hi/LC_MESSAGES/messages.po'
    
    # Read the current po file
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dictionary of translations to add
    translations = {
        'Frequently Asked Questions': 'अक्सर पूछे जाने वाले प्रश्न',
        'How to use the app?': 'ऐप का उपयोग कैसे करें?',
        'First register, then add your farm and crop information. You will automatically start receiving suggestions.': 'पहले पंजीकरण करें, फिर अपनी खेती और फसल की जानकारी जोड़ें। आपको स्वचालित रूप से सुझाव मिलना शुरू हो जाएंगे।',
        'Is this app free?': 'क्या यह ऐप निःशुल्क है?',
        'Yes, all main features are completely free. Our goal is to help farmers.': 'हां, सभी मुख्य सुविधाएं पूरी तरह निःशुल्क हैं। हमारा लक्ष्य किसानों की मदद करना है।',
        'How does the disease scanner work?': 'रोग स्कैनर कैसे काम करता है?',
        'Take a photo of your crop leaf or affected part. Our AI will immediately identify the disease and suggest treatment.': 'अपनी फसल के पत्ते या प्रभावित भाग की तस्वीर लें। हमारी AI तुरंत रोग की पहचान करेगी और उपचार सुझाएगी।',
        'How accurate is the weather information?': 'मौसम की जानकारी कितनी सटीक है?',
        'We use reliable weather APIs that are 80-90% accurate.': 'हम विश्वसनीय मौसम APIs का उपयोग करते हैं जो 80-90% सटीक हैं।',
        'More questions? Contact us': 'और प्रश्न? हमसे संपर्क करें',
        'Mobile Number': 'मोबाइल नंबर',
        'Welcome to Smart Crop Care Assistant!': 'स्मार्ट फसल देखभाल सहायक में आपका स्वागत है!',
        'Follow the steps below to start your farming journey': 'अपनी कृषि यात्रा शुरू करने के लिए नीचे दिए गए चरणों का पालन करें',
        'Add Crops': 'फसल जोड़ें',
        'Get Recommendations': 'सुझाव प्राप्त करें',
        'Step 1: Add Your Farm First': 'चरण 1: पहले अपना खेत जोड़ें',
        'Add your farm information such as name, area, soil type and location': 'अपने खेत की जानकारी जैसे नाम, क्षेत्रफल, मिट्टी का प्रकार और स्थान जोड़ें',
        'Add First Farm': 'पहला खेत जोड़ें',
        'Step 2: Add Crop Information': 'चरण 2: फसल की जानकारी जोड़ें',
        'Add your crop type, variety, and sowing date': 'अपनी फसल का प्रकार, किस्म और बुवाई की तारीख जोड़ें',
        '9 AM to 6 PM': 'सुबह 9 बजे से शाम 6 बजे तक',
        'Disease Scanner': 'रोग स्कैनर',
        'Scan and identify crop diseases': 'फसल रोगों की पहचान करें',
        'Irrigation Manager': 'सिंचाई प्रबंधक',
        'Smart irrigation recommendations': 'स्मार्ट सिंचाई सुझाव',
        'Activity Tracker': 'गतिविधि ट्रैकर',
        'Track your farm activities': 'अपनी खेती गतिविधियों को ट्रैक करें',
        'Analytics Dashboard': 'एनालिटिक्स डैशबोर्ड',
        'View detailed farm analytics': 'विस्तृत खेती एनालिटिक्स देखें'
    }
    
    # Update translations
    for english, hindi in translations.items():
        # Pattern to match msgid and empty msgstr
        pattern = rf'msgid "{re.escape(english)}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{hindi}"'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Also handle multiline strings
        if '\n' in english:
            # For multiline strings, we need a different approach
            multiline_pattern = rf'msgid ""\n"([^"]+)"\nmsgstr ""'
            if english.replace('\n', '') in content:
                # Handle multiline differently if needed
                pass
    
    # Write back to file
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Hindi translations updated successfully!")

if __name__ == '__main__':
    update_hindi_translations()

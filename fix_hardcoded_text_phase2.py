#!/usr/bin/env python3
"""
Comprehensive hardcoded Hindi text fix - Phase 2
This script will fix remaining hardcoded text patterns missed in the first pass
"""

import os
import re
from pathlib import Path

# Define additional hardcoded text patterns and their replacements
ADDITIONAL_REPLACEMENTS = {
    # Page titles
    'नियम और शर्तें - स्मार्ट फसल देखभाल सहायक': '{{ _("Terms and Conditions") }} - {{ _("Smart Crop Care Assistant") }}',
    'प्राइवेसी नीति - स्मार्ट फसल देखभाल सहायक': '{{ _("Privacy Policy") }} - {{ _("Smart Crop Care Assistant") }}',
    
    # Terms page content
    'नियम और शर्तें': '{{ _("Terms and Conditions") }}',
    'स्वीकृति की शर्तें': '{{ _("Terms of Acceptance") }}',
    'स्मार्ट फसल देखभाल सहायक का उपयोग करके, आप इन नियमों और शर्तों से सहमत होते हैं।': '{{ _("By using Smart Crop Care Assistant, you agree to these terms and conditions.") }}',
    'यदि आप इन शर्तों से सहमत नहीं हैं, तो कृपया इस ऐप का उपयोग न करें।': '{{ _("If you do not agree to these terms, please do not use this app.") }}',
    'सेवा का विवरण': '{{ _("Service Description") }}',
    'उपयोगकर्ता की जिम्मेदारियां': '{{ _("User Responsibilities") }}',
    'उपयोगकर्ता के रूप में, आप निम्नलिखित के लिए जिम्मेदार हैं:': '{{ _("As a user, you are responsible for the following:") }}',
    'सटीक और अद्यतन जानकारी प्रदान करना': '{{ _("Providing accurate and updated information") }}',
    'अपने खाते की सुरक्षा बनाए रखना': '{{ _("Maintaining the security of your account") }}',
    'कानूनी और नैतिक तरीके से ऐप का उपयोग करना': '{{ _("Using the app in a legal and ethical manner") }}',
    'अन्य उपयोगकर्ताओं के अधिकारों का सम्मान करना': '{{ _("Respecting the rights of other users") }}',
    
    # Prohibited activities
    'ऐप की सुरक्षा में हस्तक्षेप करना': '{{ _("Interfering with app security") }}',
    'झूठी या भ्रामक जानकारी प्रदान करना': '{{ _("Providing false or misleading information") }}',
    'अन्य उपयोगकर्ताओं को परेशान करना': '{{ _("Harassing other users") }}',
    'बिना अनुमति के डेटा का दुरुपयोग करना': '{{ _("Misusing data without permission") }}',
    
    # Service availability
    'हम 24/7 सेवा प्रदान करने का प्रयास करते हैं, लेकिन तकनीकी रखरखाव या अन्य कारणों से': '{{ _("We strive to provide 24/7 service, but due to technical maintenance or other reasons") }}',
    
    # GPS instructions
    'GPS निर्देशांक कैसे प्राप्त करें:': '{{ _("How to get GPS coordinates:") }}',
    'स्थान पर लंबा दबाएं (Long press)': '{{ _("Long press on the location") }}',
    'निर्देशांक दिखाई देंगे (जैसे: 26.8467, 80.9462)': '{{ _("Coordinates will appear (e.g.: 26.8467, 80.9462)") }}',
    'पहला नंबर Latitude है, दूसरा Longitude': '{{ _("First number is Latitude, second is Longitude") }}',
    
    # Location actions
    'स्थान की जानकारी हटा दी गई।': 'Location information cleared.',
    
    # Area display
    'एकड़': 'acres',
}

def fix_template_file(file_path):
    """Fix hardcoded text in a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Apply replacements
        for hindi_text, replacement in ADDITIONAL_REPLACEMENTS.items():
            if hindi_text in content:
                content = content.replace(hindi_text, replacement)
                changes_made += 1
                print(f"  ✓ Replaced: {hindi_text}")
        
        # Only write if changes were made
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Updated {file_path} with {changes_made} changes")
            return True
        else:
            print(f"  ⏭️ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all template files"""
    print("🔧 Starting Phase 2 hardcoded text fix...")
    
    # Find all HTML template files
    template_dir = Path("app/templates")
    if not template_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    html_files = list(template_dir.rglob("*.html"))
    print(f"📁 Found {len(html_files)} HTML template files")
    
    total_fixed = 0
    
    for file_path in html_files:
        print(f"\n🔍 Processing: {file_path}")
        if fix_template_file(file_path):
            total_fixed += 1
    
    print(f"\n✅ Phase 2 Completed! Fixed {total_fixed} out of {len(html_files)} files")
    print("\n📋 Next steps:")
    print("1. Run: python compile_translations.py")
    print("2. Add new translation entries to messages.po")
    print("3. Test the application in both languages")

if __name__ == "__main__":
    main()

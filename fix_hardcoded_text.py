#!/usr/bin/env python3
"""
Script to fix hardcoded Hindi text in templates
This script will replace common hardcoded Hindi text patterns with proper Flask-Babel translation functions
"""

import os
import re
from pathlib import Path

# Define common hardcoded text patterns and their replacements
REPLACEMENTS = {
    # Farm related
    'खेत संपादित करें': '{{ _("Edit Farm") }}',
    'वापस खेत विवरण में': '{{ _("Back to Farm Details") }}',
    'खेत का नाम': '{{ _("Farm Name") }}',
    'जैसे: मुख्य खेत, पूर्वी खेत, आदि': '{{ _("e.g.: Main Farm, East Farm, etc") }}',
    'क्षेत्रफल बदलने के लिए नया खेत बनाएं। (फसलों की सुरक्षा के लिए)': '{{ _("Create a new farm to change area. (For crop safety)") }}',
    'खेत का सांख्यिकी': '{{ _("Farm Statistics") }}',
    'खेत की जानकारी': '{{ _("Farm Information") }}',
    'खेत संपादित करें': '{{ _("Edit Farm") }}',
    'खेत हटाएं': '{{ _("Delete Farm") }}',
    'खेत हटाने से सभी फसलों की जानकारी भी हट जाएगी।': '{{ _("Deleting farm will also remove all crop information.") }}',
    'खेत सूची में वापस': '{{ _("Back to Farm List") }}',
    'इस खेत में अपनी पहली फसल जोड़ें': '{{ _("Add your first crop to this farm") }}',
    
    # Location related
    'Google Maps खोलें और अपने खेत का स्थान खोजें': '{{ _("Open Google Maps and find your farm location") }}',
    
    # Area and measurement
    'एकड़ क्षेत्रफल': '{{ _("acres area") }}',
    'उपयोग में (एकड़)': '{{ _("In Use (acres)") }}',
    'उपलब्ध (एकड़)': '{{ _("Available (acres)") }}',
    'क्षेत्रफल (एकड़ में)': '{{ _("Area (in acres)") }}',
    
    # Status and time
    'दिन पुराना': '{{ _("days old") }}',
    'दिन बाकी': '{{ _("days remaining") }}',
    
    # Forms and actions
    'नाम:': '{{ _("Name:") }}',
    'चेतावनी:': '{{ _("Warning:") }}',
    'सक्रिय फसलों की जानकारी भी हट जाएगी।': '{{ _("active crops information will also be deleted.") }}',
    
    # Dates and updates
    'अंतिम अपडेट: दिसंबर 2024': '{{ _("Last Updated: December 2024") }}',
    'समय-समय पर अपडेट कर सकते हैं': '{{ _("may be updated from time to time") }}',
    'महत्वपूर्ण बदलावों': '{{ _("significant changes") }}',
    'निर्णय लेने से पहले जानकारी की पुष्टि करें': '{{ _("verify information before making important decisions") }}',
    
    # Services and descriptions
    'सेवा की उपलब्धता': '{{ _("Service Availability") }}',
    'व्यक्तिगत जानकारी (नाम, ईमेल, फोन नंबर)': '{{ _("Personal information (name, email, phone number)") }}',
    'खेत और फसल की जानकारी': '{{ _("Farm and crop information") }}',
    'कृषि सलाह और रिपोर्ट्स देने के लिए': '{{ _("to provide agricultural advice and reports") }}',
    'स्मार्ट फसल देखभाल सहायक एक कृषि प्रबंधन प्लेटफॉर्म है जो किसानों को खेती में सहायता प्रदान करता है।': '{{ _("Smart Crop Care Assistant is an agricultural management platform that helps farmers with farming.") }}',
    'हम मौसम की जानकारी, फसल की निगरानी, और कृषि सलाह जैसी सेवाएं देते हैं।': '{{ _("We provide services like weather information, crop monitoring, and agricultural advice.") }}',
    
    # Activity descriptions
    'कीटनाशक का नाम और छिड़काव की विधि बताएं': '{{ _("Specify pesticide name and spraying method") }}',
    'कोई फसल उपलब्ध नहीं': '{{ _("No crops available") }}',
    'पहला खेत जोड़ें': '{{ _("Add first farm") }}',
}

def fix_template_file(file_path):
    """Fix hardcoded text in a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Apply replacements
        for hindi_text, replacement in REPLACEMENTS.items():
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
    print("🔧 Starting hardcoded text fix...")
    
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
    
    print(f"\n✅ Completed! Fixed {total_fixed} out of {len(html_files)} files")
    print("\n📋 Next steps:")
    print("1. Run: python compile_translations.py")
    print("2. Test the application in both languages")
    print("3. Verify all UI elements display correctly")

if __name__ == "__main__":
    main()

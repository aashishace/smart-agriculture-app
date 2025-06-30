#!/usr/bin/env python3
"""
Script to add Hindi translations to the messages.po file
"""

import re

# Dictionary of English to Hindi translations for common terms
HINDI_TRANSLATIONS = {
    # Navigation and Basic UI
    "Smart Agriculture": "स्मार्ट कृषि",
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
    "About": "हमारे बारे में",
    "Contact": "संपर्क",
    "Settings": "सेटिंग्स",
    
    # Dashboard specific
    "Welcome %(name)s!": "नमस्कार %(name)s!",
    "Smart Agriculture Dashboard": "स्मार्ट कृषि डैशबोर्ड",
    "Today's Date": "आज की तारीख",
    "Weather": "मौसम",
    "Clear": "साफ",
    "Getting Started": "शुरुआत करें",
    "Add your farm first to get smart agriculture recommendations": "स्मार्ट कृषि सुझाव पाने के लिए पहले अपना खेत जोड़ें",
    "Start Setup": "सेटअप शुरू करें",
    
    # Statistics and Cards
    "Total Farms": "कुल खेत",
    "Active Crops": "सक्रिय फसलें",
    "Today's Tasks": "आज के काम",
    "Weather Alerts": "मौसम अलर्ट",
    "Weather Information": "मौसम की जानकारी",
    "Recent Activity": "हाल की गतिविधि",
    "Quick Actions": "त्वरित कार्य",
    "No tasks for today!": "आज कोई काम नहीं है!",
    "No recent activity": "कोई हाल की गतिविधि नहीं",
    
    # Actions
    "Add Farm": "नया खेत जोड़ें",
    "Add Crop": "नई फसल जोड़ें",
    "Scan Disease": "रोग स्कैन करें",
    "View Crops": "फसलें देखें",
    "Help & Support": "सहायता और समर्थन",
    "Schedule Irrigation": "सिंचाई शेड्यूल करें",
    "Edit": "संपादित करें",
    "Delete": "हटाएं",
    "Save": "सेव करें",
    "Cancel": "रद्द करें",
    "Submit": "सबमिट करें",
    "Back": "वापस",
    "Next": "अगला",
    "Previous": "पिछला",
    
    # Farm and Crop related
    "Farm Name": "खेत का नाम",
    "Farm Location": "खेत का स्थान",
    "Area": "क्षेत्रफल",
    "acres": "एकड़",
    "Crop Type": "फसल का प्रकार",
    "Planting Date": "रोपण तारीख",
    "Expected Harvest": "अपेक्षित कटाई",
    "Current Stage": "वर्तमान अवस्था",
    "Status": "स्थिति",
    "Days Since Planting": "रोपण के दिन",
    "Days to Harvest": "कटाई तक दिन",
    "Growth Stage": "वृद्धि अवस्था",
    "Stage": "अवस्था",
    "Unknown": "अज्ञात",
    "Farm": "खेत",
    "Back to Crops": "फसलों की सूची",
    "Crop Information": "फसल की जानकारी",
    "Crop Details": "फसल विवरण",
    "Smart Agriculture App": "स्मार्ट कृषि ऐप",
    
    # Weather and Environment
    "Humidity": "नमी",
    "Wind Speed": "हवा की गति",
    "Rain Forecast": "बारिश की संभावना",
    "It may rain in the next 24 hours": "अगले 24 घंटों में बारिश हो सकती है",
    "Weather information not available": "मौसम की जानकारी उपलब्ध नहीं है",
    
    # Charts and Analysis
    "Growth Timeline": "वृद्धि समयरेखा",
    "Activity Timeline": "गतिविधि समयरेखा", 
    "Yield Prediction": "उत्पादन पूर्वानुमान",
    "Recent Activities": "हाल की गतिविधियां",
    "Add Activity": "गतिविधि जोड़ें",
    
    # Messages and Alerts
    "Today's irrigation has been scheduled!": "आज की सिंचाई शेड्यूल हो गई है!",
    "Error": "त्रुटि",
    "Something went wrong. Please try again.": "कुछ गलत हुआ है। कृपया पुनः प्रयास करें।",
    "Success": "सफलता",
    "Warning": "चेतावनी",
    "Information": "जानकारी",
    
    # Common Actions and Forms
    "Required": "आवश्यक",
    "Optional": "वैकल्पिक",
    "Please fill in all required fields": "कृपया सभी आवश्यक फ़ील्ड भरें",
    "Field is required": "फ़ील्ड आवश्यक है",
    "Invalid input": "अमान्य इनपुट",
    "Please try again": "कृपया पुनः प्रयास करें",
    
    # Time and Date
    "Today": "आज",
    "Yesterday": "कल",
    "Tomorrow": "कल",
    "This Week": "इस सप्ताह",
    "This Month": "इस महीने",
    "Date": "तारीख",
    "Time": "समय",
    
    # General
    "Yes": "हाँ",
    "No": "नहीं",
    "All": "सभी",
    "None": "कोई नहीं",
    "Loading...": "लोड हो रहा है...",
    "Please wait...": "कृपया प्रतीक्षा करें...",
}

def update_hindi_translations():
    """Update the Hindi translation file with common translations"""
    file_path = "app/translations/hi/LC_MESSAGES/messages.po"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count updates
        updated_count = 0
        
        # Update translations
        for english, hindi in HINDI_TRANSLATIONS.items():
            # Escape special regex characters in the English text
            escaped_english = re.escape(english)
            
            # Pattern to match msgid followed by empty msgstr
            pattern = rf'msgid "{escaped_english}"\nmsgstr ""'
            replacement = f'msgid "{english}"\nmsgstr "{hindi}"'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated_count += 1
                print(f"Updated: {english} -> {hindi}")
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nTotal translations updated: {updated_count}")
        print(f"Updated {file_path}")
        
    except Exception as e:
        print(f"Error updating translations: {e}")

if __name__ == "__main__":
    update_hindi_translations()

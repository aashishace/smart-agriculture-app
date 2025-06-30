"""
Translation dictionaries for dynamic content that can't be handled by Flask-Babel
This includes database content and programmatically generated text.
"""

from flask_babel import lazy_gettext as _l

# Crop type translations
CROP_TRANSLATIONS = {
    'wheat': {
        'hi': 'गेहूं',
        'en': 'Wheat'
    },
    'rice': {
        'hi': 'चावल',
        'en': 'Rice'
    },
    'sugarcane': {
        'hi': 'गन्ना',
        'en': 'Sugarcane'
    },
    'corn': {
        'hi': 'मक्का',
        'en': 'Corn'
    },
    'cotton': {
        'hi': 'कपास',
        'en': 'Cotton'
    },
    'mustard': {
        'hi': 'सरसों',
        'en': 'Mustard'
    },
    'potato': {
        'hi': 'आलू',
        'en': 'Potato'
    },
    'pigeon_pea': {
        'hi': 'अरहर',
        'en': 'Pigeon Pea'
    }
}

# Activity type translations
ACTIVITY_TRANSLATIONS = {
    'irrigation': {
        'hi': 'सिंचाई',
        'en': 'Irrigation'
    },
    'fertilizer': {
        'hi': 'उर्वरक',
        'en': 'Fertilizer'
    },
    'pesticide': {
        'hi': 'कीटनाशक',
        'en': 'Pesticide'
    },
    'weeding': {
        'hi': 'निराई-गुड़ाई',
        'en': 'Weeding'
    },
    'harvesting': {
        'hi': 'कटाई',
        'en': 'Harvesting'
    },
    'planting': {
        'hi': 'बुवाई',
        'en': 'Planting'
    },
    'pruning': {
        'hi': 'छंटाई',
        'en': 'Pruning'
    }
}

# Soil type translations
SOIL_TRANSLATIONS = {
    'loam': {
        'hi': 'दोमट मिट्टी',
        'en': 'Loam Soil'
    },
    'clay': {
        'hi': 'चिकनी मिट्टी',
        'en': 'Clay Soil'
    },
    'sandy': {
        'hi': 'बलुई मिट्टी',
        'en': 'Sandy Soil'
    },
    'black': {
        'hi': 'काली मिट्टी',
        'en': 'Black Soil'
    },
    'red': {
        'hi': 'लाल मिट्टी',
        'en': 'Red Soil'
    },
    'alluvial': {
        'hi': 'जलोढ़ मिट्टी',
        'en': 'Alluvial Soil'
    }
}

# Growth stage translations
GROWTH_STAGE_TRANSLATIONS = {
    'germination': {
        'hi': 'अंकुरण',
        'en': 'Germination'
    },
    'tillering': {
        'hi': 'कल्ले निकलना',
        'en': 'Tillering'
    },
    'flowering': {
        'hi': 'फूल आना',
        'en': 'Flowering'
    },
    'grain_filling': {
        'hi': 'दाना भरना',
        'en': 'Grain Filling'
    },
    'maturity': {
        'hi': 'पकना',
        'en': 'Maturity'
    },
    'vegetative': {
        'hi': 'वानस्पतिक वृद्धि',
        'en': 'Vegetative Growth'
    },
    'reproductive': {
        'hi': 'प्रजनन अवस्था',
        'en': 'Reproductive Stage'
    }
}

# Status translations
STATUS_TRANSLATIONS = {
    'active': {
        'hi': 'सक्रिय',
        'en': 'Active'
    },
    'completed': {
        'hi': 'पूर्ण',
        'en': 'Completed'
    },
    'pending': {
        'hi': 'बकाया',
        'en': 'Pending'
    },
    'overdue': {
        'hi': 'विलंबित',
        'en': 'Overdue'
    },
    'cancelled': {
        'hi': 'रद्द',
        'en': 'Cancelled'
    },
    'good': {
        'hi': 'अच्छा',
        'en': 'Good'
    },
    'warning': {
        'hi': 'चेतावनी',
        'en': 'Warning'
    },
    'poor': {
        'hi': 'खराब',
        'en': 'Poor'
    }
}

def get_translation(category, key, language='hi'):
    """
    Get translation for dynamic content.
    
    Args:
        category (str): Translation category (crops, activities, etc.)
        key (str): Translation key
        language (str): Target language ('hi' or 'en')
    
    Returns:
        str: Translated text or original key if not found
    """
    translation_maps = {
        'crops': CROP_TRANSLATIONS,
        'activities': ACTIVITY_TRANSLATIONS,
        'soil': SOIL_TRANSLATIONS,
        'growth_stages': GROWTH_STAGE_TRANSLATIONS,
        'status': STATUS_TRANSLATIONS
    }
    
    category_map = translation_maps.get(category, {})
    key_map = category_map.get(key, {})
    
    return key_map.get(language, key)

def get_crop_name(crop_key, language='hi'):
    """Get translated crop name."""
    return get_translation('crops', crop_key, language)

def get_activity_name(activity_key, language='hi'):
    """Get translated activity name."""
    return get_translation('activities', activity_key, language)

def get_soil_name(soil_key, language='hi'):
    """Get translated soil type name."""
    return get_translation('soil', soil_key, language)

def get_status_name(status_key, language='hi'):
    """Get translated status name."""
    return get_translation('status', status_key, language)

def get_translated_crop_name(crop_type, locale=None):
    """Get translated crop name for the given locale."""
    if not locale:
        from flask_babel import get_locale
        locale = str(get_locale())
    
    return CROP_TRANSLATIONS.get(crop_type, {}).get(locale, crop_type.title())

def get_translated_activity_type(activity_type, locale=None):
    """Get translated activity type for the given locale."""
    if not locale:
        from flask_babel import get_locale
        locale = str(get_locale())
    
    return ACTIVITY_TRANSLATIONS.get(activity_type, {}).get(locale, activity_type.title())

def get_translated_soil_type(soil_type, locale=None):
    """Get translated soil type for the given locale."""
    if not locale:
        from flask_babel import get_locale
        locale = str(get_locale())
    
    return SOIL_TRANSLATIONS.get(soil_type, {}).get(locale, soil_type.title())

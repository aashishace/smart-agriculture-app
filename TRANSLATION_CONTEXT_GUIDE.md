# Translation Context Guidelines

## Adding Context for Translators

When adding new translatable strings, provide context using comments:

### For Templates:
```html
{# Translators: Button to save farm information #}
{{ _('Save') }}

{# Translators: Title for the main navigation #}
{{ _('Smart Crop Care Assistant') }}
```

### For Python Code:
```python
# Translators: Success message when crop is added
flash(_('Crop added successfully.'), 'success')

# Translators: Error message for invalid form data
flash(_('Please correct the errors below.'), 'error')
```

### For Forms with Variables:
```python
# Translators: %(count)d is the number of activities created
flash(_('%(count)d activities scheduled automatically.', count=len(created_activities)), 'success')

# Translators: %(name)s is the farm name
flash(_('Farm "%(name)s" deleted successfully.', name=farm_name), 'success')
```

## Pluralization Examples:
```python
from flask_babel import ngettext

# Translators: Message about number of crops
message = ngettext(
    'You have %(num)d crop',
    'You have %(num)d crops',
    len(crops)
)
```

## Dynamic Content:
For dynamic content like crop types, use the translations_helper.py file instead of Flask-Babel.

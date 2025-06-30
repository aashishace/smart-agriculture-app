#!/usr/bin/env python3
"""
Script to automatically fill English translations where msgstr is empty.
For English locale, the translation should be the same as the msgid.
"""

import re

def update_english_po_file(file_path):
    """Update the English .po file to have msgstr same as msgid where msgstr is empty"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match msgid/msgstr pairs where msgstr is empty
    # This handles both single-line and multi-line msgid/msgstr
    pattern = r'(msgid\s+"[^"]*(?:\n"[^"]*")*)\n(msgstr\s+"")'
    
    def replace_empty_msgstr(match):
        msgid_part = match.group(1)
        # Extract the actual message from msgid "message"
        msgid_content = re.findall(r'msgid\s+"([^"]*)"', msgid_part)
        if msgid_content:
            message = msgid_content[0]
            return f'{msgid_part}\nmsgstr "{message}"'
        return match.group(0)
    
    # Replace empty msgstr with the msgid content
    updated_content = re.sub(pattern, replace_empty_msgstr, content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated {file_path}")

if __name__ == "__main__":
    update_english_po_file("app/translations/en/LC_MESSAGES/messages.po")

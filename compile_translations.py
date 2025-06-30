#!/usr/bin/env python3
"""
Compile translation files manually
"""
import polib
import os

def compile_po_to_mo(po_file_path, mo_file_path):
    """Convert .po file to .mo file."""
    po = polib.pofile(po_file_path)
    po.save_as_mofile(mo_file_path)
    print(f"Compiled {po_file_path} -> {mo_file_path}")

def main():
    """Compile all translation files."""
    base_dir = os.path.dirname(__file__)
    translations_dir = os.path.join(base_dir, 'app', 'translations')
    
    # Languages to compile
    languages = ['hi', 'en']
    
    for lang in languages:
        po_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_file = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_file):
            compile_po_to_mo(po_file, mo_file)
        else:
            print(f"PO file not found: {po_file}")

if __name__ == '__main__':
    main()

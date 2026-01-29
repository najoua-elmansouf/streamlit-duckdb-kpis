"""
Script to automatically convert section-card divs to context managers
This will simplify app.py by removing repetitive HTML markup
"""

import re

def convert_section_cards(filepath):
    """Convert all section-card divs to use context manager"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match: st.markdown('<div class="section-card">', unsafe_allow_html=True)
    # followed by content
    # followed by: st.markdown("</div>", unsafe_allow_html=True)
    
    # Count how many we have
    count_open = content.count('st.markdown(\'<div class="section-card">\', unsafe_allow_html=True)')
    count_close = content.count('st.markdown("</div>", unsafe_allow_html=True)')
    
    print(f"Found {count_open} opening divs and {count_close} closing divs")
    
    # Replace opening divs
    content = content.replace(
        '            st.markdown(\'<div class="section-card">\', unsafe_allow_html=True)',
        '            with section_card():'
    )
    content = content.replace(
        '        st.markdown(\'<div class="section-card">\', unsafe_allow_html=True)',
        '        with section_card():'
    )
    
    # Remove closing divs (they're automatic with context manager)
    content = content.replace(
        '\n            st.markdown("</div>", unsafe_allow_html=True)',
        ''
    )
    content = content.replace(
        '\n        st.markdown("</div>", unsafe_allow_html=True)',
        ''
    )
    
    # Fix indentation issues - any content after "with section_card():" should be indented
    # This is tricky and might need manual fixes
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Conversion complete!")
    print("Please check the file for indentation issues and test the app")

if __name__ == "__main__":
    filepath = r"c:\Users\masis.zovikoglu\streamlit-duckdb-kpis-1\APP\app.py"
    convert_section_cards(filepath)

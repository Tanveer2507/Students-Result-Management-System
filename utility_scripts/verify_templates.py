"""
Template Verification Script
Verifies that all authentication templates extend the correct base template
"""

import os
from pathlib import Path

def check_template_extends(file_path):
    """Check which base template a file extends"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if 'extends' in first_line:
                return first_line
    except Exception as e:
        return f"Error reading file: {e}"
    return None

def main():
    # Define templates to check
    templates_dir = Path('templates/accounts')
    
    auth_templates = [
        'student_login.html',
        'teacher_login.html',
        'admin_login.html',
        'student_forgot_password.html',
        'teacher_forgot_password.html',
        'admin_forgot_password.html',
        'student_registration.html',
        'teacher_registration.html',
        'login_select.html',
    ]
    
    print("=" * 60)
    print("TEMPLATE VERIFICATION REPORT")
    print("=" * 60)
    print()
    
    all_correct = True
    
    for template in auth_templates:
        file_path = templates_dir / template
        if file_path.exists():
            extends_line = check_template_extends(file_path)
            if extends_line:
                if "'base.html'" in extends_line or '"base.html"' in extends_line:
                    status = "✅ CORRECT"
                else:
                    status = "❌ INCORRECT"
                    all_correct = False
                print(f"{template:40} {status}")
                print(f"  → {extends_line}")
            else:
                print(f"{template:40} ⚠️  No extends found")
        else:
            print(f"{template:40} ❌ File not found")
            all_correct = False
        print()
    
    print("=" * 60)
    if all_correct:
        print("✅ All templates are correctly configured!")
    else:
        print("❌ Some templates need attention!")
    print("=" * 60)

if __name__ == "__main__":
    main()

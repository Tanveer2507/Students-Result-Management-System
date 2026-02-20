"""
Simple script to create favicon from logo
Requires: pip install Pillow
"""

try:
    from PIL import Image
    import os
    
    # Paths
    logo_path = 'static/images/logo.png'
    favicon_path = 'static/images/favicon.png'
    
    if os.path.exists(logo_path):
        # Open logo
        img = Image.open(logo_path)
        
        # Resize to favicon size
        img_resized = img.resize((64, 64), Image.Resampling.LANCZOS)
        
        # Save as favicon
        img_resized.save(favicon_path, 'PNG')
        
        print('✅ Favicon created successfully!')
        print(f'   Saved to: {favicon_path}')
    else:
        print('❌ Logo file not found!')
        print(f'   Please place your logo at: {logo_path}')
        print('   Then run this script again.')
        
except ImportError:
    print('⚠️  Pillow library not installed')
    print('   Install it with: pip install Pillow')
    print('   Or create favicon manually using online tools')
except Exception as e:
    print(f'❌ Error: {e}')
    print('   You can create favicon manually using online tools like:')
    print('   https://favicon.io/favicon-converter/')

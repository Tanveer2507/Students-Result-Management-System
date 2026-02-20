"""
Test script to verify View Details button URL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.urls import reverse
from results.models import Result

print("Testing View Details Button...")
print("=" * 60)

# Get first result
result = Result.objects.first()
if result:
    print(f"\nResult ID: {result.id}")
    print(f"Student: {result.student.user.get_full_name()}")
    print(f"Roll Number: {result.student.roll_number}")
    print("-" * 60)
    
    # Generate URL
    try:
        url = reverse('admin_result_detail', args=[result.id])
        print(f"\n✅ URL Generated Successfully:")
        print(f"   {url}")
        print(f"\n   Full URL: http://127.0.0.1:8000{url}")
        
        # Test in template format
        print(f"\n✅ Template Tag Format:")
        print(f"   {{% url 'admin_result_detail' {result.id} %}}")
        
        print("\n" + "=" * 60)
        print("✅ View Details button should work!")
        print("\nTest in browser:")
        print(f"http://127.0.0.1:8000{url}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
else:
    print("❌ No results found in database!")

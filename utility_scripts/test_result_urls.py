"""
Test script to verify result URLs are working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms_project.settings')
django.setup()

from django.urls import reverse
from results.models import Result

print("Testing Result URLs...")
print("=" * 50)

# Get a sample result
results = Result.objects.all()
if results.exists():
    result = results.first()
    result_id = result.id
    
    print(f"\nTesting with Result ID: {result_id}")
    print(f"Student: {result.student.user.get_full_name()}")
    print(f"Roll Number: {result.student.roll_number}")
    print("-" * 50)
    
    # Test all URLs
    urls_to_test = [
        ('admin_manage_results', None, 'Manage Results List'),
        ('admin_generate_result', None, 'Generate Result'),
        ('admin_result_detail', result_id, 'View Result Detail'),
        ('admin_edit_result', result_id, 'Edit/Recalculate Result'),
        ('admin_delete_result', result_id, 'Delete Result'),
        ('admin_publish_result', result_id, 'Publish/Unpublish Result'),
        ('admin_bulk_publish_results', None, 'Bulk Publish Results'),
    ]
    
    print("\nURL Resolution Test:")
    print("-" * 50)
    
    for url_name, url_id, description in urls_to_test:
        try:
            if url_id:
                url = reverse(url_name, args=[url_id])
            else:
                url = reverse(url_name)
            print(f"✅ {description:30} -> {url}")
        except Exception as e:
            print(f"❌ {description:30} -> ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("URL Test Complete!")
    print("\nTo test in browser:")
    print(f"1. View Details: http://127.0.0.1:8000{reverse('admin_result_detail', args=[result_id])}")
    print(f"2. Recalculate: http://127.0.0.1:8000{reverse('admin_edit_result', args=[result_id])}")
    print(f"3. Delete: http://127.0.0.1:8000{reverse('admin_delete_result', args=[result_id])}")
    
else:
    print("❌ No results found in database!")
    print("Please generate some results first.")

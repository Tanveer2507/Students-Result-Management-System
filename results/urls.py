from django.urls import path
from . import views

urlpatterns = [
    path('enter-marks/', views.enter_marks, name='enter_marks'),
    path('generate/<int:student_id>/', views.generate_result, name='generate_result'),
    path('view/<int:student_id>/', views.view_result, name='view_result'),
    path('all/', views.all_results, name='all_results'),
]

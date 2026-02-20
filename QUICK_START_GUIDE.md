# SRMS - Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Login Selection**: http://localhost:8000/login/

---

## 👥 User Roles

### 1. Admin
- **Login**: http://localhost:8000/login/admin/
- **Features**:
  - Manage students, teachers, classes, subjects
  - Generate and publish results
  - View complete system history
  - Access Django admin panel

### 2. Teacher
- **Login**: http://localhost:8000/login/teacher/
- **Registration**: http://localhost:8000/register/teacher/
- **Features**:
  - View students in their classes
  - Enter and view marks
  - Mark attendance
  - Create and grade assignments
  - View profile and ID card

### 3. Student
- **Login**: http://localhost:8000/login/student/
- **Registration**: http://localhost:8000/register/student/
- **Features**:
  - View marks and results
  - View attendance records
  - View and submit assignments
  - Download marksheet
  - View profile and ID card

---

## 📋 Key Features

### Attendance Management
- **Teacher**: Mark and view attendance
  - URL: `/students/teacher/attendance/mark/`
  - URL: `/students/teacher/attendance/view/`
- **Student**: View personal attendance
  - URL: `/students/student/attendance/`

### Assignment Management
- **Teacher**: Create and grade assignments
  - Create: `/students/teacher/assignments/create/`
  - View All: `/students/teacher/assignments/`
  - Grade: `/students/teacher/submission/<id>/grade/`
- **Student**: View and submit assignments
  - View All: `/students/student/assignments/`
  - Submit: `/students/student/assignment/<id>/submit/`

### Results Management
- **Admin**: Generate and publish results
  - URL: `/students/admin/results/generate/`
- **Student**: View results and download marksheet
  - URL: `/students/student/result/`
  - Download: `/students/student/download-marksheet/`

---

## 🗄️ Database Models

### Core Models:
1. **User** - Django's built-in user model
2. **UserProfile** - Extended user info (role: admin/teacher/student)
3. **Student** - Student details (roll number, class, profile picture)
4. **Teacher** - Teacher details (employee ID, subjects, qualifications)
5. **Class** - Class information (name, section)
6. **Subject** - Subject details (name, code, class, teacher)

### Academic Models:
7. **Marks** - Student marks for subjects
8. **Result** - Published results for students
9. **Attendance** - Daily attendance records
10. **Assignment** - Assignments created by teachers
11. **AssignmentSubmission** - Student assignment submissions
12. **Announcement** - System announcements

---

## 🔑 Default Test Data

### Create Test Users (Optional)
Use the utility scripts in `utility_scripts/` folder:

```bash
# Create test student
python utility_scripts/create_test_student.py

# Create test teacher
python utility_scripts/create_test_teacher.py

# Create sample data
python utility_scripts/create_sample_data.py
```

---

## 📁 Project Structure

```
srms_project/
├── accounts/              # Authentication and user management
├── students/              # Student, teacher, class management
├── results/               # Marks and results management
├── templates/             # HTML templates
│   ├── accounts/         # Login, registration templates
│   ├── students/         # Student/teacher portal templates
│   └── results/          # Results templates
├── static/               # CSS, JS, images
├── media/                # Uploaded files (profiles, assignments)
├── utility_scripts/      # Helper scripts
└── manage.py             # Django management script
```

---

## 🎨 Template Structure

### Base Templates:
- `base.html` - Main layout with navbar
- `home.html` - Landing page

### Portal Templates:
- **Admin**: `admin_dashboard.html`, `admin_*.html`
- **Teacher**: `teacher_dashboard.html`, `teacher_*.html`
- **Student**: `student_dashboard.html`, `student_*.html`

---

## 🔧 Common Tasks

### Add a New Student (Admin)
1. Login as admin
2. Go to: `/students/admin/students/add/`
3. Fill in student details
4. Submit form

### Create an Assignment (Teacher)
1. Login as teacher
2. Go to: `/students/teacher/assignments/create/`
3. Fill in assignment details
4. Upload attachment (optional)
5. Submit form

### Submit an Assignment (Student)
1. Login as student
2. Go to: `/students/student/assignments/`
3. Click on assignment
4. Click "Submit Assignment"
5. Upload file or write text
6. Submit

### Mark Attendance (Teacher)
1. Login as teacher
2. Go to: `/students/teacher/attendance/mark/`
3. Select date and class
4. Load students
5. Mark attendance status
6. Save

---

## 🐛 Troubleshooting

### Issue: "No module named 'PIL'"
**Solution**: Install Pillow
```bash
pip install Pillow
```

### Issue: "No module named 'reportlab'"
**Solution**: Install reportlab
```bash
pip install reportlab
```

### Issue: "CSRF verification failed"
**Solution**: Make sure `{%raw%}{% csrf_token %}{%endraw%}` is in all forms

### Issue: "Media files not loading"
**Solution**: Check `MEDIA_URL` and `MEDIA_ROOT` in settings.py

### Issue: "Static files not loading"
**Solution**: Run `python manage.py collectstatic`

---

## 📧 Email Configuration

### For Development:
Email credentials are currently hardcoded in the code. For production:

1. Install python-decouple:
```bash
pip install python-decouple
```

2. Create `.env` file:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

3. Update settings.py to use environment variables

---

## 🔒 Security Checklist

### Before Deployment:
- [ ] Change `DEBUG = False`
- [ ] Set `ALLOWED_HOSTS`
- [ ] Generate new `SECRET_KEY`
- [ ] Move email credentials to environment variables
- [ ] Enable HTTPS
- [ ] Set secure cookie settings
- [ ] Configure CORS if needed
- [ ] Set up proper logging

---

## 📊 Admin Panel

### Access Django Admin:
URL: http://localhost:8000/admin/

### Available Admin Sections:
- Users and Groups
- User Profiles
- Students
- Teachers
- Classes
- Subjects
- Marks
- Results
- Attendance
- Assignments
- Assignment Submissions
- Announcements

---

## 🎯 Testing the Application

### Test Flow:

1. **Admin Setup**:
   - Create classes (e.g., "Class 10-A")
   - Create subjects (e.g., "Mathematics")
   - Add teachers and assign subjects
   - Add students to classes

2. **Teacher Actions**:
   - Login as teacher
   - View assigned students
   - Mark attendance
   - Create assignment
   - Enter marks

3. **Student Actions**:
   - Login as student
   - View attendance
   - View and submit assignment
   - View marks and results

---

## 📞 Support

For issues or questions:
1. Check the `PROJECT_COMPLETION_SUMMARY.md` file
2. Review Django documentation: https://docs.djangoproject.com/
3. Check the code comments in views.py files

---

## ✨ Features Summary

### ✅ Implemented:
- User authentication (Admin, Teacher, Student)
- Student management
- Teacher management
- Class and subject management
- Marks entry and management
- Result generation and publishing
- Attendance tracking
- Assignment creation and submission
- Assignment grading
- Profile management
- ID card generation
- History tracking
- PDF marksheet download

### 🔄 Future Enhancements:
- Email notifications
- Advanced analytics
- Mobile app
- Parent portal
- Messaging system
- Bulk operations
- Export to Excel

---

**Last Updated**: February 15, 2026
**Version**: 1.0.0
**Status**: Production Ready ✅

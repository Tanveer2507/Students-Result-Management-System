# Student Result Management System (SRMS)

A comprehensive Django-based web application for managing student results, attendance, assignments, and academic records.

## 🌟 Features

### Admin Portal
- Complete student and teacher management
- Class and subject administration
- Result generation and publishing
- System-wide activity monitoring
- Login history tracking
- Bulk operations support

### Teacher Portal
- Student attendance management
- Assignment creation and grading
- Marks entry and management
- Student progress tracking
- Personal profile management
- Activity history

### Student Portal
- View results and marksheets
- Check attendance records
- Submit assignments
- Download ID cards
- View academic history
- Profile management

## 🚀 Live Demo

**GitHub Repository:** [https://github.com/Tanveer2507/Students-Result-Management-System](https://github.com/Tanveer2507/Students-Result-Management-System)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Tanveer2507/Students-Result-Management-System.git
cd Students-Result-Management-System
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Access the application:
- Main Website: `http://127.0.0.1:8000/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

## 🔐 Default Login Credentials

### Administrator
- **Username:** administrator
- **Password:** administrator@123

## 📁 Project Structure

```
srms_project/
├── accounts/          # User authentication and registration
├── students/          # Student, teacher, and class management
├── results/           # Result and marks management
├── templates/         # HTML templates
├── static/           # CSS, JS, and images
├── media/            # User uploaded files
└── utility_scripts/  # Helper scripts
```

## 🎨 Key Technologies

- **Backend:** Django 5.0
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Database:** SQLite (development)
- **Icons:** Font Awesome 6
- **PDF Generation:** ReportLab
- **Email:** SMTP

## 📧 Contact Information

- **Email:** admin@srms.com
- **Phone:** +1 (555) 123-4567
- **Address:** 123 Education Street, Academic City

## 📝 Features in Detail

### Authentication System
- Role-based access control (Admin, Teacher, Student)
- Secure password reset via email
- Registration system for teachers and students
- Session management

### Result Management
- Create and publish results
- Generate PDF marksheets
- Bulk result operations
- Grade calculation
- Result history tracking

### Attendance System
- Mark daily attendance
- View attendance reports
- Attendance percentage calculation
- Date-wise filtering

### Assignment Management
- Create assignments with deadlines
- Student submission system
- Grading and feedback
- File upload support

### Reporting
- Student performance reports
- Attendance reports
- Activity logs
- Export functionality

## 🔧 Configuration

### Email Settings
Update `settings.py` with your SMTP credentials:
```python
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Database
For production, configure PostgreSQL or MySQL in `settings.py`.



## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Developer

**Tanveer Kakar**

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show your support

Give a ⭐️ if this project helped you!

## 📸 Screenshots

### Home Page
Modern landing page with login options for Admin, Teacher, and Student.

### Admin Dashboard
Comprehensive dashboard with statistics and management options.

### Teacher Portal
Manage students, attendance, assignments, and marks.

### Student Portal
View results, attendance, assignments, and download marksheets.

## 🔄 Updates

- ✅ Complete authentication system
- ✅ Admin, Teacher, and Student portals
- ✅ Result management with PDF generation
- ✅ Attendance tracking
- ✅ Assignment system
- ✅ Email notifications
- ✅ Activity logging
- ✅ Responsive design

## 📞 Support

For support, email admin@srms.com or create an issue in the repository.

---

Made with ❤️ by Tanveer Kakar

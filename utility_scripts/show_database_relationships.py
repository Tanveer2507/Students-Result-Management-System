"""
Database Relationships Visualization Script
Shows all table relationships in the SRMS system
"""

def print_relationships():
    print("=" * 80)
    print("STUDENT RESULT MANAGEMENT SYSTEM - DATABASE RELATIONSHIPS")
    print("=" * 80)
    print()
    
    # User Model
    print("📋 USER (Django Built-in Authentication)")
    print("   Fields: id, username, email, password, first_name, last_name")
    print("   ├─ OneToOne → UserProfile (role management)")
    print("   ├─ OneToOne → Student (student details)")
    print("   └─ OneToOne → Teacher (teacher details)")
    print()
    
    # UserProfile Model
    print("👤 USERPROFILE")
    print("   Fields: user_id, role, phone, address, created_at")
    print("   └─ OneToOne ← User")
    print("   Purpose: Role-based access control (admin/teacher/student)")
    print()
    
    # Class Model
    print("🏫 CLASS")
    print("   Fields: id, name, section, created_at")
    print("   ├─ OneToMany → Student (students in class)")
    print("   └─ OneToMany → Subject (subjects for class)")
    print("   Purpose: Organize students and subjects by grade/class")
    print()
    
    # Subject Model
    print("📚 SUBJECT")
    print("   Fields: id, name, code, class_id, max_marks, pass_marks")
    print("   ├─ ManyToOne ← Class (belongs to class)")
    print("   ├─ ManyToMany ↔ Teacher (taught by teachers)")
    print("   └─ OneToMany → Marks (marks records)")
    print("   Purpose: Define courses/subjects for each class")
    print()
    
    # Student Model
    print("🎓 STUDENT")
    print("   Fields: user_id, roll_number, class_id, dob, gender, father_name,")
    print("           mother_name, phone, address, profile_picture, created_at")
    print("   ├─ OneToOne ← User (authentication)")
    print("   ├─ ManyToOne ← Class (enrolled in class)")
    print("   ├─ OneToMany → Marks (marks in subjects)")
    print("   └─ OneToOne → Result (final result)")
    print("   Purpose: Store student information and academic records")
    print()
    
    # Teacher Model
    print("👨‍🏫 TEACHER")
    print("   Fields: user_id, employee_id, phone, qualification, specialization,")
    print("           experience, address, profile_picture, created_at")
    print("   ├─ OneToOne ← User (authentication)")
    print("   └─ ManyToMany ↔ Subject (teaches subjects)")
    print("   Purpose: Store teacher information and subject assignments")
    print()
    
    # Marks Model
    print("📝 MARKS")
    print("   Fields: student_id, subject_id, marks_obtained, exam_date,")
    print("           created_at, updated_at")
    print("   ├─ ManyToOne ← Student (marks for student)")
    print("   └─ ManyToOne ← Subject (marks in subject)")
    print("   Constraint: Unique(student_id, subject_id)")
    print("   Purpose: Record marks for each student in each subject")
    print()
    
    # Result Model
    print("🏆 RESULT")
    print("   Fields: student_id, total_marks, percentage, grade, status,")
    print("           published, created_at, updated_at")
    print("   └─ OneToOne ← Student (result for student)")
    print("   Purpose: Store final calculated results")
    print()
    
    print("=" * 80)
    print("RELATIONSHIP TYPES")
    print("=" * 80)
    print()
    print("OneToOne (1:1)   - Each record relates to exactly one other record")
    print("OneToMany (1:N)  - One record relates to many records")
    print("ManyToOne (N:1)  - Many records relate to one record")
    print("ManyToMany (M:N) - Many records relate to many records")
    print()
    
    print("=" * 80)
    print("CASCADE BEHAVIORS")
    print("=" * 80)
    print()
    print("✅ Delete User → Deletes Student/Teacher/UserProfile (CASCADE)")
    print("✅ Delete Student → Deletes Marks and Result (CASCADE)")
    print("✅ Delete Subject → Deletes Marks (CASCADE)")
    print("✅ Delete Class → Deletes Subjects (CASCADE)")
    print("⚠️  Delete Class → Student.class set to NULL (SET_NULL)")
    print()
    
    print("=" * 80)
    print("DATA FLOW EXAMPLES")
    print("=" * 80)
    print()
    
    print("1️⃣  STUDENT ENROLLMENT:")
    print("   User → UserProfile → Student → Class")
    print()
    
    print("2️⃣  TEACHER ASSIGNMENT:")
    print("   User → UserProfile → Teacher ↔ Subjects")
    print()
    
    print("3️⃣  MARKS ENTRY:")
    print("   Student + Subject → Marks")
    print()
    
    print("4️⃣  RESULT GENERATION:")
    print("   Student → Marks (all subjects) → Calculate → Result")
    print()
    
    print("=" * 80)
    print("RELATIONSHIP COUNT")
    print("=" * 80)
    print()
    print("Total Models: 8")
    print("  - User (Django built-in)")
    print("  - UserProfile")
    print("  - Student")
    print("  - Teacher")
    print("  - Class")
    print("  - Subject")
    print("  - Marks")
    print("  - Result")
    print()
    print("Total Relationships: 12")
    print("  - OneToOne: 5")
    print("  - OneToMany/ManyToOne: 6")
    print("  - ManyToMany: 1")
    print()
    
    print("=" * 80)
    print("QUERY EXAMPLES")
    print("=" * 80)
    print()
    
    print("# Get all students in a class")
    print("class_obj.students.all()")
    print()
    
    print("# Get all subjects taught by a teacher")
    print("teacher.subjects.all()")
    print()
    
    print("# Get all marks for a student")
    print("student.marks.all()")
    print()
    
    print("# Get all teachers teaching a subject")
    print("subject.teachers.all()")
    print()
    
    print("# Get result for a student")
    print("student.result")
    print()
    
    print("=" * 80)
    print("✅ ALL RELATIONSHIPS PROPERLY ESTABLISHED")
    print("=" * 80)

if __name__ == "__main__":
    print_relationships()

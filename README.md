# Student Management System

A comprehensive Django-based Student Management System with role-based access control and watery glassy interfaces.

## Features

- **User Authentication**: Registration, login, and profile management
- **Role-based Access**: Differentiated access for students, lecturers, and admins
- **Course Management**: Create, view, and enroll in courses
- **Student Features**: Enrollment, assignment submission, course materials access
- **Lecturer Features**: Course creation, announcements, assignment grading
- **Admin Management**: User role assignment and system-wide configurations
- **Responsive Design**: Modern, water/glass-style interface

## Tech Stack

- **Backend**: Django 5.1.5
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (default), can be configured to use PostgreSQL, MySQL, etc.
- **Authentication**: Django's built-in authentication system with customizations

## Integration Between Apps

The system integrates all four apps to work seamlessly together:

- **Central Authentication (accounts app)**: Provides the foundation with a custom User model that defines roles (student/lecturer) used by all other apps.

- **Data Flow**: 
  - Courses created by lecturers (lecturer app) become available for student enrollment (student app)
  - Student assignments submitted through the student app are graded by lecturers through the lecturer app
  - Course materials uploaded in the course app are accessible to both students and lecturers

- **Role-Based Access Control**:
  - Admin users can promote regular users to lecturers via the admin interface
  - Views and templates in each app check user permissions before displaying content
  - URL patterns enforce role-based access restrictions

- **Cross-App Functionality**:
  - Notifications system alerts users across different roles about relevant updates
  - Dashboard for each user type aggregates information from all relevant apps
  - Shared templates ensure consistent UI/UX across the entire system

## Database Relationships

- User (accounts) → StudentProfile (student) / LecturerProfile (lecturer)
- Course (course) ← Enrollment (student)
- Course (course) ← LecturerCourse (lecturer)
- Course (course) → Assignment (student) → Submission/Grading (lecturer)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd studentproject
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the site at http://localhost:8000

## Project Structure

- **accounts**: User authentication and profile management
- **student**: Student-specific functionality
- **lecturer**: Lecturer-specific functionality
- **course**: Course management and related operations

## Usage

1. Admin users can access the Django admin site to manage users and assign roles
2. Students can enroll in courses, view materials, and submit assignments
3. Lecturers can create courses, post announcements, and grade assignments

## Data Validation and Error Handling

- Form validation for all input fields
- Custom validators for complex data requirements
- User-friendly error messages
- Secure handling of sensitive data

## Design Principles

The application follows a modular approach with Django's MVT (Model-View-Template) pattern:
- **Models**: Define the data structure
- **Views**: Control logic and request handling
- **Templates**: Handle the presentation layer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

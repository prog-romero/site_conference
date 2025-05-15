# Conference 2025 Website

A complete Django website for a conference event, featuring a responsive design with Bootstrap 5.

## Features

- Responsive design optimized for all device sizes
- Speaker profiles and session details
- Interactive agenda with filtering
- Registration system
- Contact form
- Venue information and FAQ sections

## Tech Stack

- Django 4.2
- Bootstrap 5
- Font Awesome Icons
- SQLite (for development)

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```
   python manage.py migrate
   ```
4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```
   python manage.py runserver
   ```
6. Visit http://127.0.0.1:8000/ in your browser

## Admin Interface

The Django admin interface is available at http://127.0.0.1:8000/admin/. Use it to:
- Add and manage speakers
- Create and schedule sessions
- Configure agenda items
- Manage attendee types and registrations

## Project Structure

- **conference_project** - Main Django project folder
- **conference_app** - Main application containing all models, views, and templates
  - **models.py** - Database models for speakers, sessions, attendees, etc.
  - **views.py** - View functions and classes
  - **urls.py** - URL routing
  - **forms.py** - Form definitions for registration and contact
  - **templates/conference_app/** - HTML templates using Bootstrap 5

## License

This project is available for your use and modification.
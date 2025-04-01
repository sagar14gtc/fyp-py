# Global Universities Recommendation System

A comprehensive platform for international education consultancy, helping students find and apply to universities worldwide. This system is inspired by platforms like ApplyBoard.com.

## Features

- **University Search**: Find universities and programs based on various criteria
- **Application Management**: Track and manage university applications
- **Document Management**: Upload and organize application documents
- **Real-time Chat**: Communicate with consultants and receive support
- **AI Chatbot**: Get instant answers to common questions
- **Appointment Scheduling**: Book consultations with education experts
- **Personalized Dashboard**: Track applications, messages, and appointments
- **Analytics**: View insights and statistics (for admins and consultants)

## Technology Stack

- **Backend**: Python Django
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Django Authentication System
- **File Storage**: Django File Storage
- **Real-time Features**: Django Channels (for chat)

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Git

### Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/universidad.git
cd universidad
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```
venv\Scripts\activate
```
- macOS/Linux:
```
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a PostgreSQL database:
```
createdb universidad
```

6. Copy the `.env.example` file to `.env` and update the database settings:
```
cp .env.example .env
```

7. Apply migrations:
```
python manage.py migrate
```

8. Create a superuser:
```
python manage.py createsuperuser
```

9. Run the development server:
```
python manage.py runserver
```

10. Navigate to `http://127.0.0.1:8000/` in your browser.

## Project Structure

- `accounts/`: User authentication and profile management
- `universities/`: University and program information
- `applications/`: Application submission and tracking
- `messaging/`: Chat and appointment functionality
- `dashboard/`: User dashboards and analytics
- `core/`: Core functionality and shared components
- `static/`: Static files (CSS, JS, images)
- `media/`: User-uploaded files
- `templates/`: HTML templates

## Configuration

- Environment variables are stored in the `.env` file
- Database configuration is in `settings.py`
- URL routes are defined in `urls.py` files in each app

## Data Models

- **CustomUser**: Extended user model with roles and profiles
- **University**: University information and details
- **Program**: Academic programs offered by universities
- **Application**: Student applications to programs
- **Document**: Files attached to applications
- **Conversation**: Chat conversations between users
- **Message**: Individual chat messages
- **Appointment**: Scheduled consultations

## Deployment

1. Set `DEBUG=False` in production
2. Configure a proper database for production use
3. Set up a web server (e.g., Nginx, Apache)
4. Use a WSGI server (e.g., Gunicorn)
5. Set up static file serving
6. Configure SSL/TLS for secure connections

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name - Lead Developer
- Add other contributors here

## Acknowledgments

- ApplyBoard.com for inspiration
- Django community for the excellent framework
- Bootstrap team for the UI components 
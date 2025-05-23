# Python_manager

A Flask application for managing Python projects and users with role-based access control.

![Pylint](https://github.com/YourUsername/Lab_Manager-1/actions/workflows/pylint.yml/badge.svg)

## Features
- User authentication and registration
- Role-based access control (user, admin, admin_manager)
- Session management
- Activity logging
- System settings management
- Project creation and management
- API endpoints for integration with other systems

## Installation

### Prerequisites
- Python 3.7+
- pip
- Virtual environment (recommended)

### Setup Steps
1. Clone the repository
   ```
   git clone <repository-url>
   cd Python_manager
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables   ```
   # Create a .env file with the following variables
   FLASK_APP=app.py
   FLASK_DEBUG=1  # Set to 1 for development mode, 0 for production
   SECRET_KEY=your_secret_key
   DATABASE_URI=sqlite:///your_database.db
   ```

5. Initialize the database
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application
   ```
   flask run
   ```
   The application will be available at http://localhost:5000

## Configuration

Configuration options can be modified in `config.py` or through environment variables. Key configuration options include:

- `SECRET_KEY`: Used for session security
- `DATABASE_URI`: Database connection string
- `LOG_LEVEL`: Logging verbosity
- `SESSION_LIFETIME`: Session timeout duration

## Usage

### User Roles

- **User**: Can view and manage their own projects
- **Admin**: Can manage users and all projects
- **Admin Manager**: Has full system access, including role management

### Example Operations

- Creating a new project
- Managing user permissions
- Viewing activity logs
- Configuring system settings

## API Documentation

API documentation is available at `/api/docs` when the application is running.

## Project Structure

```
Python_manager/
├── app/
│   ├── controllers/     # Route handlers
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── static/          # CSS, JS, images
│   ├── templates/       # HTML templates
│   └── utils/           # Helper functions
├── migrations/          # Database migrations
├── tests/               # Test suite
├── .env                 # Environment variables
├── app.py               # Application entry point
├── config.py            # Configuration
└── requirements.txt     # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or questions, please open an issue on the project repository.
�
# Lab Manager

A comprehensive Flask-based laboratory management system with advanced features for educational institutions and research facilities. This system provides robust lab session management, real-time monitoring, and user authentication capabilities.

## ✨ Features

### 🔐 Authentication & Security
- Multi-level user authentication and registration  
- Role-based access control with 3 user levels:
  - **Regular User** (user) - Standard users with basic permissions
  - **Administrator** (admin) - Administrators with content management access
  - **System Administrator** (system_admin) - System administrators with full access
- Enhanced CSRF protection with automatic token refresh
- Secure session management with consistency checks
- Activity logging and audit trails
- Password reset functionality with secure tokens

### 🧪 Lab Session Management
- Create and manage lab sessions with QR code verification
- Student registration and attendance tracking
- Real-time session monitoring and status updates
- Automated session scheduling and room assignment
- Lab result submission and management
- Verification code generation with QR code support

### ⚡ Enhanced Lab Session Management (NEW)
- **Advanced Analytics Dashboard**: Real-time statistics and performance metrics
- **Smart Filtering & Search**: Multi-criteria filtering with tags, difficulty levels, and room assignments
- **Bulk Operations**: Mass update, delete, and export capabilities
- **Rich Session Metadata**: Support for session thumbnails, tags, difficulty ratings, and detailed descriptions
- **Enhanced Export Features**: Export session data to CSV, Excel, and PDF formats
- **Session Templates**: Create reusable session templates for quick setup
- **Equipment Integration**: Manage lab equipment booking and availability
- **Session Rating System**: Student feedback and rating collection
- **Notification Center**: Real-time alerts and updates for session changes
- **Multi-format File Support**: Attach various file types to sessions
- **Advanced Status Tracking**: Detailed session lifecycle management
- **Capacity Management**: Intelligent participant limit handling with waitlist support

### 🔌 Real-time Features

- Real-time dashboard updates with WebSocket support  
- System health monitoring and metrics
- CSRF-protected form submissions with automatic validation

### 📊 Administrative Tools
- User management with role assignment
- System configuration and settings
- Advanced filtering and search capabilities
- Comprehensive activity logging
- System metrics and performance monitoring

### 🧪 Testing & Quality Assurance
- Unit tests for core functionality
- Integration tests with Selenium WebDriver
- System health checks and validation
- Comprehensive CSRF security testing
- Automated test runners with HTML reporting

## 📋 Installation

### Prerequisites

- Python 3.8+ (required for all features)
- pip (Python package manager)
- Git (for version control)
- Chrome/Chromium browser (for Selenium testing)
- Virtual environment (strongly recommended)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Lab_Manager
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   
   **🪟 Windows Users - If you get compilation errors:**
   ```bash
   # Method 1: Use the automated fix script
   python fix_installation.py

   # Method 2: Use the Windows batch script  
   install_windows.bat

   # Method 3: Install safe requirements first
   pip install -r requirements_safe.txt

   # Method 4: Install with binary wheels only
   pip install --only-binary=:all: -r requirements.txt
   ```

   **🐧 Linux/Mac Users:**
   ```bash
   pip install -r requirements.txt
   
   # If you get build errors, install build tools first:
   # Ubuntu/Debian: sudo apt-get install build-essential libxml2-dev libxslt1-dev
   # CentOS/RHEL: sudo yum install gcc libxml2-devel libxslt-devel  
   # macOS: xcode-select --install
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=1
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///instance/app.db
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```
   The application will be available at http://localhost:5000

## 🔄 Database Migration for Enhanced Features

If you're upgrading from an earlier version of Lab Manager, you'll need to migrate your database to support the new enhanced features:

### Automatic Migration (Recommended)

```bash
# Create migration for new features
flask db migrate -m "Add enhanced lab session features"

# Apply migration
flask db upgrade
```

### Manual Migration (If needed)

If automatic migration fails, you can manually update the database schema:

```sql
-- Database Schema Normalized to 3NF (Third Normal Form)

-- Core Entity Tables

-- 1. Users Table (normalized)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    role_id INTEGER NOT NULL DEFAULT 1,
    profile_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES user_roles (id),
    FOREIGN KEY (profile_id) REFERENCES user_profiles (id)
);

-- 2. User Roles (separate table for normalization)
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- user, admin, system_admin
    description VARCHAR(255),
    level INTEGER NOT NULL DEFAULT 1
);

-- 3. User Profiles (separated from users for N3)
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bio TEXT,
    reset_token VARCHAR(100),
    reset_token_expiry INTEGER,
    verification_token VARCHAR(100),
    verification_token_expiry INTEGER,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login DATETIME,
    account_locked_until DATETIME
);

-- 4. Lab Sessions (normalized)
CREATE TABLE IF NOT EXISTS lab_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location_id INTEGER NOT NULL,
    difficulty_id INTEGER NOT NULL DEFAULT 2,
    status_id INTEGER NOT NULL DEFAULT 1,
    max_participants INTEGER NOT NULL DEFAULT 30,
    verification_code VARCHAR(10) NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations (id),
    FOREIGN KEY (difficulty_id) REFERENCES difficulty_levels (id),
    FOREIGN KEY (status_id) REFERENCES session_statuses (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- 5. Locations (separate table for normalization)
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    capacity INTEGER DEFAULT 30,
    equipment_available TEXT
);

-- 6. Difficulty Levels (separate table)
CREATE TABLE IF NOT EXISTS difficulty_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- easy, medium, hard
    description VARCHAR(255),
    sort_order INTEGER
);

-- 7. Session Statuses (separate table)
CREATE TABLE IF NOT EXISTS session_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- scheduled, ongoing, completed, cancelled
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT 1
);

-- 8. Session Registrations (normalized)
CREATE TABLE IF NOT EXISTS session_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lab_session_id INTEGER NOT NULL,
    registration_status_id INTEGER NOT NULL DEFAULT 1,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lab_session_id) REFERENCES lab_sessions (id),
    FOREIGN KEY (registration_status_id) REFERENCES registration_statuses (id),
    UNIQUE(user_id, lab_session_id)
);

-- 9. Registration Statuses
CREATE TABLE IF NOT EXISTS registration_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- registered, confirmed, cancelled, attended
    description VARCHAR(255)
);

-- 10. Session Entries (normalized)
CREATE TABLE IF NOT EXISTS session_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lab_session_id INTEGER NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME,
    score INTEGER,
    results TEXT,
    submission_status_id INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lab_session_id) REFERENCES lab_sessions (id),
    FOREIGN KEY (submission_status_id) REFERENCES submission_statuses (id)
);

-- 11. Submission Statuses
CREATE TABLE IF NOT EXISTS submission_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- not_submitted, submitted, graded
    description VARCHAR(255)
);

-- 12. System Settings (normalized)
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(64) UNIQUE NOT NULL,
    value TEXT,
    setting_type_id INTEGER NOT NULL DEFAULT 1,
    description VARCHAR(256),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (setting_type_id) REFERENCES setting_types (id)
);

-- 13. Setting Types
CREATE TABLE IF NOT EXISTS setting_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(16) UNIQUE NOT NULL,  -- string, integer, boolean, float
    validation_rule TEXT
);

-- 14. Activity Logs (normalized)
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type_id INTEGER NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (action_type_id) REFERENCES action_types (id)
);

-- 15. Action Types
CREATE TABLE IF NOT EXISTS action_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,  -- login, logout, create_session, etc.
    category VARCHAR(20),  -- authentication, session_management, user_management
    description VARCHAR(255)
);

-- 16. Courses (normalized)
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    course_category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_category_id) REFERENCES course_categories (id)
);

-- 17. Course Categories
CREATE TABLE IF NOT EXISTS course_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    sort_order INTEGER
);

-- 18. Lessons (normalized)
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    course_id INTEGER NOT NULL,
    lesson_order INTEGER DEFAULT 1,
    duration_minutes INTEGER,
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

-- 19. Course Enrollments (normalized)
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_status_id INTEGER NOT NULL DEFAULT 1,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completion_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id),
    FOREIGN KEY (enrollment_status_id) REFERENCES enrollment_statuses (id),
    UNIQUE(user_id, course_id)
);

-- 20. Enrollment Statuses
CREATE TABLE IF NOT EXISTS enrollment_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,  -- enrolled, completed, dropped, suspended
    description VARCHAR(255)
);

-- Initial Data for Lookup Tables
INSERT INTO user_roles (id, name, description, level) VALUES
(1, 'user', 'Regular user with basic permissions', 1),
(2, 'admin', 'Administrator with content management access', 2),
(3, 'system_admin', 'System administrator with full access', 3);

INSERT INTO difficulty_levels (id, name, description, sort_order) VALUES
(1, 'easy', 'Beginner level', 1),
(2, 'medium', 'Intermediate level', 2),
(3, 'hard', 'Advanced level', 3);

INSERT INTO session_statuses (id, name, description, is_active) VALUES
(1, 'scheduled', 'Session is scheduled', 1),
(2, 'ongoing', 'Session is currently running', 1),
(3, 'completed', 'Session has been completed', 0),
(4, 'cancelled', 'Session has been cancelled', 0);

INSERT INTO registration_statuses (id, name, description) VALUES
(1, 'registered', 'User has registered'),
(2, 'confirmed', 'Registration confirmed'),
(3, 'cancelled', 'Registration cancelled'),
(4, 'attended', 'User attended the session');

INSERT INTO submission_statuses (id, name, description) VALUES
(1, 'not_submitted', 'No submission yet'),
(2, 'submitted', 'Work has been submitted'),
(3, 'graded', 'Work has been graded');

INSERT INTO setting_types (id, name, validation_rule) VALUES
(1, 'string', NULL),
(2, 'integer', '^[0-9]+$'),
(3, 'boolean', '^(true|false|0|1)$'),
(4, 'float', '^[0-9]*\.?[0-9]+$');

INSERT INTO enrollment_statuses (id, name, description) VALUES
(1, 'enrolled', 'Active enrollment'),
(2, 'completed', 'Course completed'),
(3, 'dropped', 'Enrollment dropped'),
(4, 'suspended', 'Enrollment suspended');
```

### Verify Migration

After migration, verify the application is working:

```bash
# Check database schema
flask shell
>>> from app.models import *
>>> db.engine.execute("PRAGMA table_info(ca_thuc_hanh)")
```

## ⚙️ Configuration

The application can be configured through `config.py` or environment variables. Key configuration options:

### Core Settings

- `SECRET_KEY`: Flask secret key for sessions and CSRF protection
- `DATABASE_URL`: Database connection string (default: SQLite)
- `FLASK_DEBUG`: Enable debug mode (0 for production, 1 for development)
- `FLASK_ENV`: Environment mode (production/development)

### Security Settings

- `WTF_CSRF_TIME_LIMIT`: CSRF token expiration (None for no limit)
- `WTF_CSRF_CHECK_DEFAULT`: Enable CSRF protection by default
- `SESSION_COOKIE_SECURE`: Use secure cookies in production
- `SESSION_COOKIE_HTTPONLY`: Prevent XSS attacks on cookies

### Application Settings

- `MAX_CONTENT_LENGTH`: Maximum file upload size
- `UPLOAD_FOLDER`: Directory for uploaded files
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Database Models

The system uses the following main database models normalized to 3NF:

**Core Entity Tables:**
- `User` - User accounts with normalized role relationships
- `UserRole` - User roles lookup table (user, admin, system_admin)
- `UserProfile` - User profile information separated for normalization
- `LabSession` - Laboratory sessions with foreign key relationships
- `Location` - Session locations lookup table
- `DifficultyLevel` - Session difficulty levels lookup table
- `SessionStatus` - Session status lookup table

**Registration & Participation:**
- `SessionRegistration` - User session registrations with status
- `RegistrationStatus` - Registration status lookup table
- `SessionEntry` - Session entry/exit tracking
- `SubmissionStatus` - Work submission status lookup table

**System Management:**
- `SystemSetting` - Configuration with type normalization
- `SettingType` - Setting data types lookup table
- `ActivityLog` - System activities with action types
- `ActionType` - Activity action types lookup table

**Course Management:**
- `Course` - Courses with category relationships
- `CourseCategory` - Course categories lookup table
- `Lesson` - Individual lessons within courses
- `Enrollment` - Course enrollments with status
- `EnrollmentStatus` - Enrollment status lookup table

#### Database Normalization to 3NF Benefits

**First Normal Form (1NF):** 
- Eliminated repeating groups and arrays
- Each cell contains atomic values
- All entries in a column are of the same data type

**Second Normal Form (2NF):**
- All non-key attributes are fully functionally dependent on primary key
- Removed partial dependencies
- Separated composite attributes into individual tables

**Third Normal Form (3NF):**
- Eliminated transitive dependencies
- Created lookup tables for repeated values (roles, statuses, types)
- Reduced data redundancy and storage requirements
- Improved data integrity and consistency

#### Key Normalization Changes

**Lookup Tables Created:**
- `user_roles` - Instead of storing role names directly
- `difficulty_levels` - Instead of hardcoded difficulty strings
- `session_statuses` - Instead of status strings in main table
- `registration_statuses` - Normalized registration states
- `submission_statuses` - Standardized submission states
- `setting_types` - Data type validation rules
- `action_types` - Categorized system actions
- `course_categories` - Course classification
- `enrollment_statuses` - Student enrollment states

**Data Integrity Improvements:**
- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate registrations
- Standardized status values through lookup tables
- Centralized validation rules for settings

**Performance Benefits:**
- Reduced storage through elimination of redundancy
- Faster queries with proper indexing on foreign keys
- Easier maintenance of reference data
- Consistent data validation

### System Architecture & Integration

**Lab Manager is a completely independent system:**

- ❌ **No external services**: No dependencies on third-party services
- ✅ **Self-developed web interface**: Comprehensive web interface for all features  
- ✅ **Self-contained Architecture**: Operates independently, no internet required
- ✅ **Zero External Dependencies**: No reliance on cloud services
- ✅ **Complete Data Privacy**: No data sharing with external parties

**Benefits of independent architecture:**

- 🔒 **Maximum Security**: Data is completely protected
- 💰 **No additional costs**: No cloud service fees
- ⚡ **High Performance**: Not limited by rate limits
- 🛡️ **Stability**: No dependence on external services

## 👥 User Management & Permissions

### User Roles and Permissions

The Lab Manager system implements a sophisticated role-based access control system with three distinct user levels:

#### 📊 User Role Feature Matrix

| **Feature** | **User** (user) | **Administrator** (admin) | **System Administrator** (system_admin) |
|---|:---:|:---:|:---:|
| **🔐 Authentication & Account** | | | |
| Login/Logout | ✅ | ✅ | ✅ |
| Password Reset | ✅ | ✅ | ✅ |
| Update Personal Profile | ✅ | ✅ | ✅ |
| **📚 Lab Session Management** | | | |
| View Available Sessions | ✅ | ✅ | ✅ |
| Register for Sessions | ✅ | ✅ | ✅ |
| Create Lab Sessions | ❌ | ✅ | ✅ |
| Edit Lab Sessions | ❌ | ✅ | ✅ |
| Delete Lab Sessions | ❌ | ✅ | ✅ |
| **👥 User Management** | | | |
| View User List | ❌ | ✅ | ✅ |
| Create User Accounts | ❌ | ✅ | ✅ |
| Edit User Information | ❌ | ✅ | ✅ |
| Promote to Admin | ❌ | ❌ | ✅ |
| Promote to System Admin | ❌ | ❌ | ✅ |
| Demote Admin Privileges | ❌ | ❌ | ✅ |
| Delete Users | ❌ | ❌ | ✅ |
| **⚙️ System Management** | | | |
| Access Admin Dashboard | ❌ | ✅ | ✅ |
| View System Statistics | ❌ | ✅ | ✅ |
| Basic System Settings | ❌ | ✅ | ✅ |
| Advanced System Settings | ❌ | ❌ | ✅ |
| System Maintenance | ❌ | ❌ | ✅ |
| Clear System Logs | ❌ | ❌ | ✅ |
| Reset Database | ❌ | ❌ | ✅ |
| **📊 Monitoring & Reports** | | | |
| View Activity Logs | ❌ | ✅ | ✅ |
| Generate Usage Reports | ❌ | ✅ | ✅ |
| Real-time Monitoring | ❌ | ✅ | ✅ |
| **🔧 API Access** | | | |
| Basic API Usage | ✅ | ✅ | ✅ |
| User Management API | ❌ | ❌ | ✅ |
| System Administration API | ❌ | ❌ | ✅ |

#### 🔑 Role Permissions Detail

##### User (Regular User)

- Access Level: 1
- Primary Functions: Use basic system features
- Restrictions: No administrative access, personal account management only

##### Administrator (Admin)

- Access Level: 2
- Primary Functions: Content and user management
- Access Control: `@admin_required` decorator
- Restrictions: Cannot modify user roles or advanced system settings

##### System Administrator (System Admin)

- Access Level: 3  
- Primary Functions: Full system administration
- Access Control: `@admin_required` and `@system_admin_required` decorators
- Special Privileges:
  - Cannot be deleted from the system
  - Full access to all system features
  - User role management capabilities
  - Can perform dangerous operations (DB reset, log clearing)

#### 🛡️ Security Implementation

```python
# Role hierarchy checking
def role_level(self):
    levels = {"system_admin": 3, "admin": 2, "user": 1}
    return levels.get(self.role, 0)

# Access control decorators
@admin_required       # Requires level 2+ (admin or system admin)
@system_admin_required  # Requires level 3 (system admin only)
```

#### 🔄 Role Upgrade Process

The system follows a strict role hierarchy:

```text
user → admin → system_admin
  ↑       ↑         ↑
  (Only System Administrators can perform role changes)
```

## 🚀 Usage

### Key User Workflows

#### Regular User Features

- Register for lab sessions
- View available sessions and schedules
- Submit lab results and verification codes
- Track personal lab session history
- Access student dashboard

#### Administrator Features

- Create and manage lab sessions
- View and manage user registrations
- Generate QR codes for session verification
- Access admin dashboard with system metrics
- Manage session attendance and results

#### System Administrator Features

- Full system administration access
- User role management and permissions
- System configuration and settings
- Advanced reporting and analytics
- System health monitoring

### Common Workflows

#### Creating a Lab Session (Admin)

1. Navigate to Admin Dashboard → Lab Sessions
2. Click "Create New Session"
3. Fill in session details (title, description, date/time, location)
4. Set maximum participants and verification code
5. Generate QR code for easy access
6. Activate session for student registration

#### Student Registration Process

1. Browse available lab sessions
2. Click "Register" on desired session
3. Confirm registration details
4. Receive confirmation and session details
5. Use QR code or verification code to enter lab

#### Session Verification and Entry

1. Student scans QR code or enters verification code
2. System validates code and session timing
3. Student gains access to active lab session
4. Submit results and complete session when finished

### API Usage

#### 🔐 API Usage Status

**Lab Manager is a completely independent system:**

- ❌ **No external APIs**: No integration with third-party services
- ✅ **Comprehensive internal API**: Self-developed REST API for all functions
- ✅ **Self-contained**: Operates independently, no internet dependency
- ✅ **High security**: No data sharing with external parties

#### 🌐 Internal REST API Endpoints

##### Authentication & User Management

```bash
POST /api/auth/login             # User login
POST /api/auth/logout            # User logout
GET  /api/auth/me               # Current user information
POST /api/auth/change-password   # Change password
GET  /api/users                 # User list (admin)
POST /api/users                 # Create new user (admin)
GET  /api/users/{id}            # User details
PUT  /api/users/{id}            # Update user (admin)
```

##### Lab Session Management

```bash
GET    /api/lab-sessions                    # Lab sessions list
POST   /api/lab-sessions                    # Create new session (admin)
GET    /api/lab-sessions/{id}               # Session details
PUT    /api/lab-sessions/{id}               # Update session (admin)
DELETE /api/lab-sessions/{id}               # Delete session (admin)
POST   /api/lab-sessions/register           # Register for session
POST   /api/lab-sessions/{id}/checkin       # Check-in to session
POST   /api/lab-sessions/entry/{id}/checkout # Check-out from session
GET    /api/lab-sessions/my-sessions        # My sessions
GET    /api/lab-sessions/{id}/attendees     # Attendees list (admin)
```

##### System Administration

```bash
GET  /api/admin/dashboard-stats    # Dashboard statistics (admin)
GET  /api/admin/activities         # Activity logs (admin)
POST /api/admin/user-management    # User permissions management (admin)
GET  /api/admin/reports/usage      # Usage reports (admin)
POST /api/admin/system-maintenance # System maintenance (admin)
```

##### System Monitoring & Health

```bash
GET /api/system/health          # System health check
GET /api/system/metrics         # System performance metrics
GET /api/system/metrics-demo    # Demo metrics (no authentication required)
GET /api/system/status          # System status
```

##### CSRF Security

```bash
GET  /api/v1/csrf-token          # Get CSRF token
POST /api/v1/csrf-token/refresh  # Refresh token
POST /api/v1/csrf-token/validate # Validate token
```

#### 🔧 JavaScript API Client

The system provides a client-side API wrapper:

```javascript
// Initialize API client
const labAPI = new LabAPI();

// Use API
const sessions = await labAPI.getLabSessions();
const user = await labAPI.getCurrentUser();
const metrics = await labAPI.getSystemMetrics();
```

#### 📡 Real-time Features

- **WebSocket**: Real-time dashboard updates
- **Server-Sent Events**: Status notifications
- **Auto-refresh**: Automatic data refresh

## 🧪 Testing

The Lab Manager includes comprehensive testing capabilities to ensure security and functionality.

### Test Categories

#### Unit Tests
Basic functionality tests for core components:
```bash
python test/csrf_unit_tests.py
```

#### Integration Tests
Full workflow testing with Selenium WebDriver:
```bash
python test/csrf_integration_tests.py
```

#### System Tests
Complete system validation and health checks:
```bash
python test/csrf_system_test.py
```

### Running All Tests

Use the master test runner for comprehensive testing:
```bash
# Run all tests with detailed reporting
python test/run_all_csrf_tests.py

# Run with specific options
python test/run_all_csrf_tests.py --generate-report --verbose --stop-on-error
```

### Test Reports

Tests generate detailed HTML reports in the `test_reports/` directory:
- `csrf_test_report.html` - Comprehensive test results
- `system_health_report.html` - System status and metrics
- Test logs and screenshots for failed tests

### Demo Pages

Interactive testing and demonstration pages:
- `/csrf-test` - CSRF functionality testing
- `/csrf-demo` - Interactive CSRF demonstration
- `/api-integration-demo` - API testing interface

## 📁 Project Structure

```
Lab_Manager/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── decorators.py            # Custom decorators
│   ├── utils.py                 # Utility functions
│   ├── session_handler.py       # Session management
│   ├── real_time_monitor.py     # System monitoring
│   ├── csrf_middleware.py       # CSRF protection middleware
│   ├── init_sample_data.py      # Sample data initialization
│   ├── init_users.py            # User initialization
│   │
│   ├── api/                     # REST API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication API
│   │   ├── users.py             # User management API
│   │   ├── lab_sessions.py      # Lab session API
│   │   ├── admin.py             # Admin API
│   │   ├── system.py            # System API
│   │   └── csrf.py              # CSRF token API
│   │
│   ├── routes/                  # Web routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── user.py              # User routes
│   │   ├── admin.py             # Admin routes
│   │   ├── lab.py               # Lab session routes
│   │   └── search.py            # Search functionality
│   │
│   ├── static/                  # Static assets
│   │   ├── css/                 # Stylesheets
│   │   │   ├── base.css
│   │   │   ├── admin_tables.css
│   │   │   ├── system_dashboard.css
│   │   │   └── theme/           # Theme files
│   │   │
│   │   └── js/                  # JavaScript files
│   │       ├── lab-api.js       # Lab API client
│   │       ├── lab_sessions.js  # Session management
│   │       ├── admin_tables.js  # Admin interface
│   │       ├── system_dashboard.js # Dashboard functionality
│   │       ├── realtime_dashboard.js # Real-time updates
│   │       ├── flash_messages.js # Message handling
│   │       ├── log_regis.js     # Login/registration
│   │       └── verify_qr.js     # QR code verification
│   │
│   └── templates/               # Jinja2 templates
│       ├── base.html            # Base template with CSRF handling
│       ├── index.html           # Home page
│       ├── dashboard.html       # User dashboard
│       ├── csrf_test.html       # CSRF testing page
│       ├── csrf_demo.html       # CSRF demonstration
│       ├── api_integration_demo.html # API demo
│       │
│       ├── auth/                # Authentication templates
│       │   └── log_regis.html   # Login/registration
│       │
│       ├── admin/               # Admin templates
│       │   ├── admin_base.html
│       │   ├── admin_dashboard.html
│       │   ├── admin_users.html
│       │   ├── admin_lab_sessions.html
│       │   └── admin_create_lab_session.html
│       │
│       ├── lab/                 # Lab session templates
│       │   ├── lab_sessions.html
│       │   ├── my_sessions.html
│       │   ├── verify_session.html
│       │   └── active_session.html
│       │
│       └── user/                # User templates
│           └── profile.html
│
├── test/                        # Test suite
│   ├── setup_csrf_tests.py      # Test environment setup
│   ├── run_all_csrf_tests.py    # Master test runner
│   ├── csrf_unit_tests.py       # Unit tests
│   ├── csrf_integration_tests.py # Integration tests
│   ├── csrf_system_test.py      # System tests
│   ├── check_users.py           # User validation
│   └── system_health_check.py   # Health monitoring
│
├── migrations/                  # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/                # Migration files
│
├── instance/                    # Instance-specific files
│   └── app.db                   # SQLite database
│
├── logs/                        # Application logs
│   └── activity.log             # Activity log file
│
├── doc/                         # Documentation
│   └── DESIGN_SYSTEM.md         # Design system guide
│
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Development & Contributing

### Development Setup

1. **Fork and clone the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   pip install -r requirements.txt
   python test/setup_csrf_tests.py
   ```

4. **Make your changes**
5. **Run tests to ensure functionality**
   ```bash
   python test/run_all_csrf_tests.py
   ```

6. **Submit a pull request**

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include unit tests for new functionality
- Update documentation for new features

### Architecture Notes

- **CSRF Protection**: Enhanced with automatic token refresh and multi-endpoint fallback
- **API Design**: RESTful endpoints with consistent response formats
- **Real-time Features**: WebSocket integration for live updates
- **Security**: Role-based access control with session management
- **Testing**: Multi-layer testing strategy (unit, integration, system)

## 🛠️ Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Reset database
flask db init
flask db migrate -m "Reset database"
flask db upgrade
```

#### CSRF Token Issues
- Check that JavaScript is enabled in your browser
- Clear browser cache and cookies
- Verify that the CSRF middleware is properly configured

#### Testing Environment Issues
```bash
# Reset test environment
python test/setup_csrf_tests.py --reset
# Install Chrome/Chromium for Selenium tests
python -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

#### Permission Errors
- Ensure proper user roles are assigned
- Check that the user has necessary permissions for the action
- Verify session is not expired

### Getting Help

1. **Check the logs**: `logs/activity.log` contains detailed application logs
2. **Run system health check**: `python test/system_health_check.py`
3. **Check API status**: Visit `/api/system/health` endpoint
4. **Review test reports**: Check `test_reports/` directory for detailed diagnostics

## 📚 Additional Resources

### Key Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-SocketIO**: Real-time communication
- **Selenium**: Web browser automation for testing
- **pytest**: Testing framework

### Useful Commands

```bash
# Database operations
flask db migrate -m "Description"    # Create migration
flask db upgrade                     # Apply migrations
flask db downgrade                   # Rollback migrations

# Testing
python test/run_all_csrf_tests.py           # Run all tests
python test/csrf_system_test.py --verbose   # System tests with output
python test/setup_csrf_tests.py --check     # Verify test environment

# Development
python run.py                        # Start development server
python -m flask shell               # Interactive shell
python test/system_health_check.py  # Check system status
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support & Contact

- **Issues**: Report bugs and feature requests through the project repository
- **Documentation**: Additional documentation available in the `doc/` directory  
- **System Health**: Monitor system status at `/api/system/health`
- **API Testing**: Interactive API testing at `/api-integration-demo`

## 🎯 Roadmap

### Upcoming Features

- [ ] Advanced analytics and reporting dashboard
- [ ] Email notifications for lab sessions
- [ ] Mobile app support
- [ ] Integration with external calendar systems
- [ ] Advanced user management features
- [ ] Enhanced security features and audit trails

### Recent Updates

- ✅ Comprehensive CSRF protection system
- ✅ Real-time monitoring and dashboard updates
- ✅ Enhanced API with full CRUD operations
- ✅ Selenium-based integration testing
- ✅ Interactive demo and testing pages
- ✅ Automated test suite with HTML reporting

---

**Lab Manager** - A comprehensive laboratory management system built with Flask, designed for educational institutions and research facilities.

## 🚀 Deployment

### Local Development
```bash
python run.py
```
The application will be available at http://localhost:5000

### Azure App Service Deployment

Deploy Lab Manager to Azure App Service in just a few minutes:

#### Quick Deployment
```bash
# Install Azure CLI (if not already installed)
# Windows: https://aka.ms/installazurecliwindows
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Deploy automatically
python deploy_azure.py
```

#### Manual Azure Setup
```bash
# Create Azure resources
az group create --name lab-manager-rg --location southeastasia
az appservice plan create --name lab-manager-plan --resource-group lab-manager-rg --sku B1 --is-linux
az webapp create --name your-app-name --resource-group lab-manager-rg --plan lab-manager-plan --runtime "PYTHON|3.11"

# Configure and deploy
az webapp config set --name your-app-name --resource-group lab-manager-rg --startup-file "run_azure.py"
az webapp deployment source config-local-git --name your-app-name --resource-group lab-manager-rg
git remote add azure <git-url-from-above>
git push azure main
```

#### Azure Files Created
- `.env.azure` - Azure environment configuration
- `run_azure.py` - Azure App Service runner
- `deploy_azure.py` - Automated deployment script
- `startup.sh` - Azure startup script
- `AZURE_DEPLOYMENT.md` - Detailed deployment guide
- `AZURE_QUICKSTART.md` - Quick start guide

See **AZURE_QUICKSTART.md** for detailed Azure deployment instructions.

### Cost Estimate
- **B1 Basic**: ~$13/month (recommended for production)
- **F1 Free**: $0/month (limited resources, good for testing)

## 💻 Technology Stack

Lab Manager is built with a modern and diverse technology stack to ensure optimal performance, security, and user experience.

### 🐍 Backend Technology Stack

#### Core Framework & Libraries
- **Flask 2.2.3** - Main Python web framework
- **Flask-SQLAlchemy 3.0.3** - ORM and database management
- **Flask-Login 0.6.2** - Authentication and session management
- **Flask-WTF 1.1.1** - Form handling and CSRF protection
- **Flask-Migrate 4.1.0** - Database migration and versioning
- **Flask-SocketIO 5.3.6** - Real-time WebSocket communication
- **Flask-Caching 2.3.1** - High-performance caching system
- **Flask-Mail 0.10.0** - Email sending and notifications

#### Database & Storage
- **SQLAlchemy 1.4.46** - Database abstraction layer
- **SQLite** (Development) - Lightweight database for development
- **PostgreSQL Support** - Production support with psycopg2-binary
- **Alembic 1.15.2** - Database migration tool

#### Security & Authentication
- **Werkzeug 2.2.3** - WSGI utilities and password hashing
- **PyJWT 2.10.1** - JSON Web Token for API authentication
- **Cryptography 42.0.8** - Advanced encryption and security
- **WTForms 3.0.1** - Form validation and security

#### Performance & Monitoring
- **Redis 4.6.0** - In-memory caching and session storage
- **Celery 5.3.1** - Task queue and background processing
- **psutil 5.9.5** - System monitoring and resource tracking

### 🌐 Frontend Technology Stack

#### Core Web Technologies
- **HTML5** - Semantic markup with accessibility support
- **CSS3** - Modern styling with CSS Variables and Grid
- **JavaScript ES6+** - Native JavaScript with module pattern
- **Bootstrap 5.x** - Responsive CSS framework

#### JavaScript Libraries & Frameworks
- **Chart.js** - Interactive charts and data visualization
- **Socket.IO Client** - Real-time communication
- **AOS (Animate On Scroll)** - Scroll animations
- **QR Code Libraries** - QR code generation and scanning

#### CSS Architecture
```css
/* Modern CSS Features */
- CSS Custom Properties (Variables)
- CSS Grid & Flexbox
- CSS Animations & Transitions
- Backdrop Filter & Glass Morphism
- CSS Containment API
```

#### Design System Components
- **Variables.css** - Centralized design tokens
- **Base.css** - Core styling and typography
- **System Dashboard.css** - Dashboard-specific components
- **Admin Tables.css** - Data table styling
- **Flash Messages.css** - Notification system
- **Responsive.css** - Mobile-first responsive design

### 🎨 UI/UX Design Features

#### Visual Design System
- **Glass Morphism Effects** - Backdrop blur and transparency
- **Gradient Backgrounds** - Dynamic color transitions
- **Card-based Layout** - Modern component architecture
- **Icon Integration** - Font Awesome 5 icons
- **Custom Animations** - CSS keyframes and transitions

#### Responsive Design
- **Mobile-First Approach** - Progressive enhancement
- **Breakpoint System** - 576px, 768px, 992px, 1200px+
- **Flexible Grid System** - CSS Grid with auto-fit
- **Touch-Friendly Interface** - Mobile gesture support

### 🛠️ Development & Testing Tools

#### Development Dependencies
- **pytest 7.4.3** - Python testing framework
- **pytest-cov 4.1.0** - Code coverage analysis
- **pytest-mock 3.12.0** - Mocking utilities
- **Selenium 4.15.2** - Browser automation testing
- **WebDriver Manager 4.0.1** - Automatic driver management
- **ChromeDriver AutoInstaller 0.6.4** - Chrome driver setup

#### Code Quality & Linting
- **pylint 3.3.7** - Python code analysis
- **isort 6.0.1** - Import statement sorting
- **pre-commit 4.2.0** - Git hooks and code quality
- **astroid 3.3.10** - Abstract syntax tree analysis

#### Data Processing & Analysis
- **pandas 2.2.3** - Data manipulation and analysis
- **numpy 2.2.6** - Numerical computing
- **pyarrow 20.0.0** - Columnar data processing
- **reportlab 4.4.1** - PDF generation

#### API Testing & Development
- **Flask-RESTful 0.3.9** - Quickly build REST APIs
- **Flask-Swagger-UI 3.61.2** - Swagger UI integration
- **Flask-CORS 3.0.10** - Handle Cross-Origin Resource Sharing
- **httpie 3.2.1** - User-friendly HTTP client

#### Performance Monitoring
- **Flask-DebugToolbar 0.13.1** - Debugging and profiling
- **Flask-Profiler 0.6.0** - Performance profiling
- **Sentry SDK 2.11.0** - Error tracking and monitoring

### 🏗️ Backend Technology

#### Server & WSGI
- **Waitress 2.1.2** - Production WSGI server (Windows-compatible)
- **Gunicorn** - UNIX-based WSGI server
- **Eventlet 0.33.3** - Concurrent networking library

#### Environment & Configuration
- **python-dotenv 1.0.0** - Environment variable management
- **PyYAML 6.0.2** - YAML configuration files
- **pytz 2025.2** - Timezone handling
- **tzdata 2025.2** - Timezone database

#### Web Scraping & HTML Processing
- **BeautifulSoup4 4.12.2** - HTML/XML parsing
- **requests 2.31.0** - HTTP library
- **html5lib 1.1** - HTML5 parser
- **chardet 5.2.0** - Character encoding detection

### 📊 Real-time Features & Monitoring

#### System Monitoring
```javascript
// Real-time system metrics
- CPU Usage Tracking
- Memory Usage Monitoring  
- Disk Space Analysis
- Network Performance
- User Activity Tracking
- Session Management
```

#### Live Dashboard Features
- **WebSocket Communication** - Real-time data updates
- **Interactive Charts** - Chart.js with live data binding
- **Performance Metrics** - System health monitoring
- **Activity Logs** - Real-time user activity tracking
- **Notification System** - Live alerts and messages

### 🏗️ Architecture Patterns

#### Backend Architecture
- **Blueprint Pattern** - Modular Flask application structure
- **Service Layer Pattern** - Business logic separation
- **Repository Pattern** - Data access abstraction
- **Decorator Pattern** - Authentication and authorization
- **Factory Pattern** - Application configuration

#### Frontend Architecture
- **Component-Based Design** - Reusable UI components
- **Module Pattern** - JavaScript code organization
- **Observer Pattern** - Event-driven programming
- **MVC Pattern** - Model-View-Controller separation

### 🔒 Security Implementation

#### Authentication & Authorization
```python
# Security measures implemented
- Role-based Access Control (RBAC)
- CSRF Protection with automatic token refresh
- Secure Password Hashing (Werkzeug)
- Session Management with Flask-Login
- API Authentication with JWT tokens
```

#### Data Protection
- **Input Validation** - WTForms validation
- **SQL Injection Prevention** - SQLAlchemy ORM
- **XSS Protection** - Template escaping
- **HTTPS Support** - SSL/TLS configuration
- **Rate Limiting** - Request throttling

### 📱 Progressive Web App Features

#### Modern Web Standards
- **Service Workers** (Planned) - Offline functionality
- **Web App Manifest** (Planned) - Installable web app
- **Push Notifications** (Planned) - Browser notifications
- **Cache API** - Client-side caching strategy

### 🔮 Future Technology Roadmap

#### Planned Enhancements
- **GraphQL API** - Flexible data querying
- **TypeScript Integration** - Type-safe frontend development
- **Docker Containerization** - Deployment standardization
- **Kubernetes Support** - Container orchestration
- **Machine Learning Integration** - Predictive analytics
- **Progressive Web App** - Full PWA implementation

Lab Manager uses a modern and scalable technology stack, ensuring high performance, excellent security, and outstanding user experience for educational laboratory management systems.

## 🎨 Enhanced Admin Interface

The Lab Manager now includes a completely redesigned admin interface for enhanced lab session management:

### 🚀 New Admin Dashboard Features

#### **Enhanced Lab Sessions Management Page**
- **Modern Material Design UI**: Clean, responsive interface with intuitive navigation
- **Real-time Analytics Dashboard**: Live statistics showing session counts, participant metrics, and system health
- **Advanced Filtering & Search**: Multi-criteria filtering by status, room, date, tags, and difficulty level
- **Smart Bulk Operations**: Mass update, delete, and status change capabilities with progress tracking
- **Rich Data Display**: Card-based layout with session thumbnails, tags, and quick action buttons
- **Export Capabilities**: Generate comprehensive reports in CSV, Excel, and PDF formats

#### **Session Creation & Management**
- **Template-based Creation**: Use pre-built templates for quick session setup
- **Rich Metadata Support**: Add thumbnails, tags, difficulty ratings, and detailed descriptions
- **Equipment Integration**: Manage lab equipment booking and availability tracking
- **File Attachments**: Support for multiple file types with drag-and-drop upload
- **Capacity Management**: Intelligent participant limits with waitlist functionality
- **Notification System**: Automated alerts for session changes and updates

#### **Analytics & Reporting**
- **Real-time Metrics**: Live dashboard with session statistics and performance indicators
- **Interactive Charts**: Visual representation of session data with drill-down capabilities
- **Export Tools**: Generate detailed reports with customizable parameters
- **Trend Analysis**: Track session popularity, attendance rates, and resource utilization

### 🔧 Admin Access & Navigation

#### **Accessing Enhanced Features**
1. Log in as an administrator (`quan_tri_vien` or `quan_tri_he_thong`)
2. Navigate to **Admin Panel** → **Enhanced Lab Sessions** from the main menu
3. Use the new interface for advanced session management

#### **Key Features Overview**
- **Dashboard Overview**: Real-time statistics and key performance indicators
- **Session Grid View**: Card-based display with filtering and search capabilities
- **Bulk Actions Panel**: Mass operations with progress tracking and confirmation dialogs
- **Export Center**: Multi-format report generation with customizable parameters
- **Quick Actions**: One-click operations for common tasks

### 📱 Responsive Design

The enhanced admin interface is fully responsive and optimized for:
- **Desktop**: Full-featured interface with advanced controls
- **Tablet**: Touch-optimized UI with essential features
- **Mobile**: Streamlined interface for on-the-go management

### 🔐 Security & Permissions

Enhanced admin features maintain the same security standards:
- **Role-based Access**: Only authorized administrators can access enhanced features
- **CSRF Protection**: All forms and API calls are protected against CSRF attacks
- **Activity Logging**: All administrative actions are logged for audit purposes
- **Session Management**: Secure session handling with automatic timeout

## 📡 Enhanced API Endpoints

The Lab Manager now provides comprehensive API endpoints for enhanced lab session management:

### 🔧 Enhanced Lab Sessions API

#### **Core Endpoints**
- `GET /api/lab-sessions/enhanced` - Get enhanced lab sessions with filtering and pagination
- `GET /api/lab-sessions/enhanced/stats` - Real-time analytics and statistics
- `POST /api/lab-sessions/enhanced/bulk-update` - Bulk update multiple sessions
- `DELETE /api/lab-sessions/enhanced/bulk-delete` - Bulk delete multiple sessions
- `GET /api/lab-sessions/enhanced/export` - Export sessions to CSV/Excel/PDF
- `GET /api/lab-sessions/enhanced/search` - Advanced search with multiple criteria

#### **Template Management**
- `GET /api/session-templates` - Get all session templates
- `POST /api/session-templates` - Create new template
- `PUT /api/session-templates/{id}` - Update template
- `DELETE /api/session-templates/{id}` - Delete template

#### **Equipment Integration**
- `GET /api/equipment` - Get all lab equipment
- `POST /api/equipment/book` - Book equipment for session
- `GET /api/equipment/availability` - Check equipment availability

#### **Rating & Feedback**
- `POST /api/sessions/{id}/rate` - Submit session rating
- `GET /api/sessions/{id}/ratings` - Get session ratings
- `GET /api/sessions/ratings/stats` - Rating statistics

#### **File Management**
- `POST /api/sessions/{id}/files` - Upload session files
- `GET /api/sessions/{id}/files` - Get session files
- `DELETE /api/files/{file_id}` - Delete session file

#### **Notifications**
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications/mark-read` - Mark notifications as read
- `POST /api/notifications/send` - Send notification (admin only)

### 📊 API Response Examples

#### **Enhanced Sessions List**
```json
{
  "sessions": [
    {
      "id": 1,
      "ten_ca": "Python Programming Lab",
      "mo_ta": "Introduction to Python programming",
      "tags": ["python", "programming", "beginner"],
      "muc_do_kho": 2,
      "anh_bia": "/uploads/python_lab.jpg",
      "thoi_gian_du_kien": 120,
      "so_luong_toi_da": 25,
      "so_nguoi_dang_ky": 18,
      "trang_thai": "dang_mo",
      "rating_average": 4.2,
      "rating_count": 12
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 12,
    "total": 45,
    "pages": 4
  },
  "stats": {
    "total_sessions": 45,
    "active_sessions": 23,
    "completed_sessions": 15,
    "cancelled_sessions": 7
  }
}
```

#### **Analytics Data**
```json
{
  "overview": {
    "total_sessions": 156,
    "total_participants": 2847,
    "average_rating": 4.3,
    "completion_rate": 89.2
  },
  "recent_activity": [
    {
      "type": "session_created",
      "session_name": "Advanced Database Design",
      "timestamp": "2024-01-15T10:30:00Z",
      "user": "Dr. Smith"
    }
  ],
  "charts": {
    "sessions_by_month": [...],
    "participants_by_status": [...],
    "ratings_distribution": [...]
  }
}
```

## 🚀 Upgrade Guide

### From Previous Versions

If you're upgrading from an earlier version of Lab Manager, follow these steps:

#### **1. Backup Your Data**
```bash
# Backup current database
cp instance/app.db instance/app.db.backup

# Backup configuration
cp config.py config.py.backup
```

#### **2. Update Dependencies**
```bash
# Pull latest changes
git pull origin main

# Update Python packages
pip install -r requirements.txt
```

#### **3. Run Database Migration**
```bash
# Generate migration
flask db migrate -m "Add enhanced features"

# Apply migration
flask db upgrade
```

#### **4. Update Configuration**
```bash
# Copy new configuration options from config.py.example
# Add any new environment variables to your .env file
```

#### **5. Test Enhanced Features**
```bash
# Start the application
python run.py

# Access enhanced admin interface
# Navigate to: http://localhost:5000/admin/
```

### New Feature Highlights

#### **For Administrators**
- Modern dashboard with real-time analytics
- Bulk operations for efficient management
- Enhanced filtering and search capabilities
- Multi-format export functionality
- Template-based session creation

#### **For Users**
- Improved session browsing with rich metadata
- Rating and feedback system
- File attachments and resources
- Enhanced notification system
- Better mobile experience

#### **For Developers**
- Better caching and performance optimization
- Enhanced error handling and validation
- Comprehensive documentation
- Docker support for easy deployment

### Compatibility Notes

- **Database**: Automatic migration preserves all existing data
- **Templates**: Existing templates work unchanged
- **User Authentication**: No changes to user accounts or permissions
- **Configuration**: Backward compatible with existing config files

For detailed technical documentation, see the `/docs` directory.
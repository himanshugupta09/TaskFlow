# TaskFlow - Project Management & Task Tracking Application

TaskFlow is a modern, full-stack project management and task tracking application built with Django REST Framework and React. It enables teams to collaborate on projects, manage tasks, track progress, and communicate effectively.

## 🎯 Features

### Core Functionality
- **User Authentication**: Secure JWT-based authentication with registration and login
- **Project Management**: Create, edit, and manage projects with team collaboration
- **Task Management**: Create tasks with detailed descriptions, priorities, statuses, and due dates
- **Team Collaboration**: Add team members to projects with role-based access (Admin/Member)
- **Task Assignment**: Assign tasks to team members and track accountability
- **Status Tracking**: Multiple task statuses (To Do, In Progress, In Review, Completed, Blocked, etc.)
- **Priority Levels**: Categorize tasks by priority (Critical, High, Medium, Low)
- **Dashboard**: Real-time dashboard showing project statistics and task overview
- **User Search**: Find and invite other users to projects
- **Notifications**: System notifications for task updates, assignments, and project invitations
- **Project Invitations**: Invite external users to projects via unique tokens
- **Task Comments**: Add comments to tasks for discussion and updates
- **Task History**: Track changes to task status and updates

## 🏗️ Project Structure

```
TaskFlow/
├── taskflow/                    # Django project directory
│   ├── api/                     # Main Django app
│   │   ├── migrations/          # Database migrations
│   │   ├── templates/
│   │   │   └── index.html       # React SPA entry point
│   │   ├── admin.py             # Django admin configuration
│   │   ├── apps.py              # App configuration
│   │   ├── models.py            # Database models
│   │   ├── views.py             # API view handlers
│   │   ├── serializers.py       # DRF serializers
│   │   ├── permissions.py       # Custom permissions
│   │   ├── urls.py              # API URL routing
│   │   └── tests.py             # Unit tests
│   ├── taskflow/                # Project settings directory
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # Project URL routing
│   │   ├── wsgi.py              # WSGI application
│   │   ├── asgi.py              # ASGI application
│   │   └── __init__.py
│   ├── manage.py                # Django management script
│   └── db.sqlite3               # SQLite database (development)
├── venv/                        # Python virtual environment
├── requirements.txt             # Python dependencies
├── Procfile                     # Heroku/Railway deployment config
├── railway.toml                 # Railway deployment config
└── README.md                    # This file
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise
- **CORS**: django-cors-headers

### Frontend
- **Library**: React 18
- **Build Tool**: Babel (for JSX transpilation in browser)
- **State Management**: React Hooks (useState, useEffect)
- **HTTP Client**: Fetch API
- **Storage**: LocalStorage for JWT tokens

### Deployment
- **Platform**: Railway / Heroku compatible
- **Database**: PostgreSQL on Railway
- **Environment**: Python 3.10+

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TaskFlow
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to project directory**
   ```bash
   cd taskflow
   ```

5. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Frontend: http://127.0.0.1:8000
   - Admin Panel: http://127.0.0.1:8000/admin

## 🚀 Running the Application

### Development Mode
```bash
cd taskflow
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Production Mode (using Gunicorn)
```bash
cd taskflow
gunicorn taskflow.wsgi:application --bind 0.0.0.0:8000
```

## 🗄️ Database Models

### User
Extends Django's built-in User model with:
- username
- email
- first_name
- last_name
- password (hashed)

### Project
```python
- name: CharField (max 200)
- description: TextField
- created_by: ForeignKey(User)
- created_at: DateTimeField (auto)
```

### ProjectMember
```python
- project: ForeignKey(Project)
- user: ForeignKey(User)
- role: CharField (choices: 'admin', 'member')
- joined_at: DateTimeField (auto)
```

### Task
```python
- project: ForeignKey(Project)
- title: CharField (max 300)
- description: TextField
- status: CharField (choices: todo, in_progress, in_review, completed, blocked, dismissed)
- priority: CharField (choices: critical, high, medium, low)
- tags: CharField
- assigned_to: ForeignKey(User, nullable)
- created_by: ForeignKey(User)
- due_date: DateField (nullable)
- created_at: DateTimeField (auto)
- updated_at: DateTimeField (auto)
```

### TaskComment
```python
- task: ForeignKey(Task)
- author: ForeignKey(User)
- text: TextField
- created_at: DateTimeField (auto)
```

### TaskStatusHistory
```python
- task: ForeignKey(Task)
- old_status: CharField
- new_status: CharField
- changed_by: ForeignKey(User)
- changed_at: DateTimeField (auto)
```

### Notification
```python
- recipient: ForeignKey(User)
- actor: ForeignKey(User, nullable)
- notif_type: CharField (choices: various notification types)
- title: CharField
- message: TextField
- task: ForeignKey(Task, nullable)
- project: ForeignKey(Project, nullable)
- is_read: BooleanField
- created_at: DateTimeField (auto)
```

### ProjectInvite
```python
- project: ForeignKey(Project)
- invited_by: ForeignKey(User)
- email: EmailField
- role: CharField
- token: UUIDField (unique)
- status: CharField (choices: pending, accepted, expired)
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user info

### Dashboard
- `GET /api/dashboard/` - Get dashboard statistics and task counts

### Projects (CRUD)
- `GET /api/projects/` - List user's projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Project Members
- `GET /api/projects/{project_id}/members/` - List project members
- `POST /api/projects/{project_id}/members/` - Add member to project
- `DELETE /api/projects/{project_id}/members/{member_id}/` - Remove member

### Tasks (CRUD)
- `GET /api/tasks/` - List tasks assigned to current user
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Project Tasks
- `GET /api/projects/{project_id}/tasks/` - List tasks in a project
- `GET /api/projects/{project_id}/tasks/?status=todo` - Filter by status

### Task Comments
- `GET /api/tasks/{task_id}/comments/` - List comments
- `POST /api/tasks/{task_id}/comments/` - Add comment
- `DELETE /api/tasks/{task_id}/comments/{comment_id}/` - Delete comment

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread/` - Get unread count
- `POST /api/notifications/mark-read/` - Mark notifications as read
- `DELETE /api/notifications/{id}/` - Delete notification

### User Search
- `GET /api/users/search/?q=query` - Search for users by email or username

### Project Invitations
- `POST /api/projects/{project_id}/invite/` - Send project invitation
- `GET /api/projects/{project_id}/invites/` - List pending invitations
- `DELETE /api/projects/{project_id}/invites/{invite_id}/` - Cancel invitation
- `GET /api/invites/{token}/` - Get invitation info
- `POST /api/invites/{token}/accept/` - Accept project invitation

## 🎨 Frontend Structure

The frontend is a Single Page Application (SPA) built with React, served as a single `index.html` file with embedded React and Babel.

### Components
- **AuthPage**: Login/Registration form
- **Dashboard**: Overview of projects and task statistics
- **Projects**: List and manage projects
- **ProjectDetail**: View project tasks and members
- **TaskModal**: Create/edit tasks with form
- **MyTasks**: View and manage assigned tasks
- **Modal**: Reusable modal component for dialogs

### Key Features
- JWT token-based authentication stored in LocalStorage
- Real-time API communication with error handling
- Responsive design with CSS Grid and Flexbox
- Status and priority badges
- Team member avatars and roles

## 🔐 Authentication & Authorization

### JWT Authentication
- Users receive `access` and `refresh` tokens on login
- Access token expires in 24 hours
- Refresh token expires in 7 days
- Tokens stored in browser LocalStorage

### Permission Levels
- **Public Endpoints**: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/`
- **Protected Endpoints**: All other endpoints require valid JWT token
- **Project Access**: Users can only access projects they're members of
- **Admin Rights**: Project admins can manage members and delete projects

## 🔧 Configuration

### Environment Variables (Production)
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=https://yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Development Settings
- DEBUG = True
- SQLite database by default
- Console email backend (prints emails to terminal)
- CORS enabled for all origins

## 📊 How It Works

### User Flow
1. **Registration**: New user creates account via `/api/auth/register/`
2. **Login**: User logs in and receives JWT tokens
3. **Create Project**: User creates a project
4. **Add Members**: Project admin invites team members
5. **Create Tasks**: Team members create tasks and assign them
6. **Update Status**: Tasks move through workflow (To Do → In Progress → Review → Done)
7. **Comments**: Team members collaborate via task comments
8. **Notifications**: System sends notifications for important events

### Task Lifecycle
1. **Creation**: Task created with initial status (usually "To Do")
2. **Assignment**: Task assigned to team member
3. **Progress**: Task status updated as work progresses
4. **Completion**: Task marked as completed or dismissed
5. **History**: All changes tracked in TaskStatusHistory

### Invitation System
1. Project admin sends invitation to email
2. Unique token generated for invitation link
3. Recipient accepts invitation via token
4. User becomes project member with assigned role

## 🚀 Deployment

### Railway Deployment
1. Push code to GitHub
2. Connect GitHub repo to Railway
3. Set environment variables in Railway dashboard
4. Railway automatically detects `Procfile` and deploys
5. PostgreSQL database automatically provisioned

### Environment Setup for Railway
- `SECRET_KEY`: Generate a secure key
- `DATABASE_URL`: Automatically provided by Railway
- `DEBUG`: Set to False
- `ALLOWED_HOSTS`: Add your Railway domain

## 🧪 Testing

Run tests with:
```bash
python manage.py test api
```

## 📝 Common Operations

### Create a New Project
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Description"}'
```

### Create a Task
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project": 1, "title": "Task Title", "priority": "high"}'
```

### Update Task Status
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## 🐛 Troubleshooting

### Database Errors
```bash
# Reset migrations (development only)
python manage.py migrate api zero
python manage.py migrate

# Recreate database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Frontend Not Loading
- Clear browser cache
- Check that `api/templates/index.html` exists
- Verify static files are served: `python manage.py collectstatic --noinput`

### API Not Responding
- Check Django development server is running
- Verify CORS headers are configured
- Check JWT token hasn't expired
- Review Django logs for errors

## Tradeoffs & What I'd Do With More Time

This assignment intentionally forced prioritization. Here are the architectural tradeoffs I made to deliver a robust backend within the time constraint:

1. **Framework Choice (Django over FastAPI):**
   I utilized Django REST Framework because its built-in ORM and migration system allowed me to rapidly model complex authorization boundaries (e.g., ensuring users cannot access tasks in unassigned projects). While FastAPI offers superior async performance, DRF allowed me to focus heavily on the background processing and caching requirements rather than writing boilerplate CRUD SQL queries.

2. **Cache Invalidation Strategy:**
   I implemented a strict "Delete on Write" pattern using `django-redis` wildcard pattern matching (`cache.delete_pattern()`). When a task updates, I wipe all cached task querysets for the users in that specific project. 
   *Tradeoff:* While this guarantees no stale reads (a primary requirement), it is aggressive. With more time, I would implement a finer-grained cache update strategy or use Redis Sets to track specific query keys to avoid deleting unrelated cached queries for a user.

3. **Background Notifications (Celery vs. RQ):**
   I chose Celery backed by Redis. While RQ is simpler to set up, Celery is the enterprise standard for Django and provides better retry mechanisms and rate-limiting configurations. 
   *Tradeoff:* Since actual email/SMS delivery wasn't required, the Celery task currently relies on standard Python `logging`. In production, I would wire this to Amazon SES or Twilio and implement exponential backoff for delivery failures.

4. **Metrics Endpoint:**
   The current `/metrics` endpoint is a simple JSON view returning database counts. With more time, I would replace this with `django-prometheus` to expose native PromQL metrics (like request latency histograms and error rates) for scraping by a Grafana dashboard.

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [JWT Authentication](https://jwt.io/)

## 📄 License

This project is open source and available under the MIT License.

## 👥 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues, questions, or suggestions, please create an issue in the repository.

---

**Last Updated**: August 2026  
**Version**: 1.0.0

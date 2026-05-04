# 🗂️ Team Task Manager

A full-stack collaborative task management web application built with Flask and Vanilla JavaScript.

## 🌐 Live URL
https://team-task-manager-production-3c59.up.railway.app/

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite with SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Deployment:** Railway

## 🚀 Features
- User Signup and Login with JWT authentication
- Create projects (creator becomes Admin)
- Admin can add/remove team members
- Create tasks with Title, Description, Due Date, Priority
- Assign tasks to team members
- Update task status: To Do, In Progress, Done
- Dashboard: total tasks, status count, overdue tasks
- Role-based access control (Admin/Member)

## ⚙️ Setup Instructions
1. Clone the repo
2. cd backend
3. python -m venv venv
4. venv\Scripts\activate
5. pip install -r requirements.txt
6. python app.py
7. Open http://127.0.0.1:5000

## 📡 API Endpoints
- POST /auth/signup
- POST /auth/login
- GET /projects
- POST /projects
- POST /projects/<id>/members
- DELETE /projects/<id>/members/<uid>
- GET /projects/<id>/tasks
- POST /projects/<id>/tasks
- PATCH /tasks/<id>
- GET /projects/<id>/dashboard

## 🔐 Environment Variables
- SECRET_KEY=Vivek@2026SecretKey
- FLASK_APP=app.py

## 👨‍💻 Developer
Vivek Pawar

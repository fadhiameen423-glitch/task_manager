# Personal Task Manager

A multi-user task management system built using FastAPI, SQLite, and Streamlit.

## Features

* User Registration
* User Login
* Secure Authentication using HTTPBearer
* Password Hashing using bcrypt
* Create Tasks
* View Tasks
* Edit Tasks
* Delete Tasks
* Mark Tasks as Done
* Filter Tasks by Status and Priority
* Task Summary Dashboard
* Multi-user Support
* Personalized User Greeting

## Tech Stack

### Backend

* FastAPI
* SQLite
* Passlib (bcrypt)

### Frontend

* Streamlit

## Project Structure

```text
task_manager/
│
├── backend/
│   ├── routers/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
│
├── frontend/
│   └── app.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

## How to Run

### Activate Virtual Environment

```bash
venv\Scripts\activate
```

### Run Backend

```bash
cd backend
uvicorn main:app --reload
```

### Run Frontend

Open another terminal:

```bash
cd frontend
streamlit run app.py
```

## API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

## Author

Fadhi Ameen

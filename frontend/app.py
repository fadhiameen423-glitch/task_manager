import streamlit as st
import requests
from datetime import date


API_BASE_URL = "http://127.0.0.1:8000"


def api_call(method, endpoint, data=None, token=None, params=None):
    url = API_BASE_URL + endpoint
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method,
            url,
            json=data,
            headers=headers,
            params=params
        )

        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"detail": "No response body"}

    except requests.exceptions.ConnectionError:
        return 0, {"detail": "FastAPI server is not running"}


if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "token" not in st.session_state:
    st.session_state["token"] = None

if "email" not in st.session_state:
    st.session_state["email"] = None

if "name" not in st.session_state:
    st.session_state["name"] = None

if "selected_task_id" not in st.session_state:
    st.session_state["selected_task_id"] = None


def show_register():
    st.title("Register")

    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if name == "" or email == "" or password == "":
            st.error("Name, email and password are required")
            return

        status_code, result = api_call(
            "POST",
            "/auth/register",
            data={
                "name": name,
                "email": email,
                "password": password
            }
        )

        if status_code == 201:
            st.success("Registration successful. Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error(result.get("detail", "Registration failed"))

    if st.button("Already have an account? Login"):
        st.session_state["page"] = "login"
        st.rerun()


def show_login():
    st.title("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if email == "" or password == "":
            st.error("Email and password are required")
            return

        status_code, result = api_call(
            "POST",
            "/auth/login",
            data={
                "email": email,
                "password": password
            }
        )

        if status_code == 200:
            token = result["token"]

            status_code_user, user = api_call(
                "GET",
                "/auth/me",
                token=token
            )

            if status_code_user == 200:
                st.session_state["token"] = token
                st.session_state["email"] = user["email"]
                st.session_state["name"] = user["name"]
                st.session_state["page"] = "dashboard"
                st.rerun()
            else:
                st.error(user.get("detail", "Could not load user details"))
        else:
            st.error(result.get("detail", "Login failed"))

    if st.button("Create new account"):
        st.session_state["page"] = "register"
        st.rerun()


def show_dashboard():
    st.title("Task Dashboard")

    st.subheader(f"Hi, {st.session_state['name']} 👋")
    st.write(f"Logged in as: {st.session_state['email']}")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Add New Task"):
            st.session_state["page"] = "add_task"
            st.rerun()

    with col_b:
        if st.button("Logout"):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()

    st.subheader("Task Summary")

    status_code, summary = api_call(
        "GET",
        "/tasks/summary",
        token=st.session_state["token"]
    )

    if status_code == 200:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", summary["total"])
        col2.metric("Pending", summary["pending"])
        col3.metric("In Progress", summary["in_progress"])
        col4.metric("Done", summary["done"])
    else:
        st.error(summary.get("detail", "Could not load summary"))

    st.subheader("Filters")

    status_filter = st.selectbox(
        "Status",
        ["", "pending", "in-progress", "done"]
    )

    priority_filter = st.selectbox(
        "Priority",
        ["", "low", "medium", "high"]
    )

    params = {}

    if status_filter:
        params["status"] = status_filter

    if priority_filter:
        params["priority"] = priority_filter

    status_code, tasks = api_call(
        "GET",
        "/tasks/",
        token=st.session_state["token"],
        params=params
    )

    st.subheader("My Tasks")

    if status_code == 200:
        if len(tasks) == 0:
            st.info("No tasks found")
        else:
            for task in tasks:
                st.write("---")
                st.write(f"**ID:** {task['id']}")
                st.write(f"**Title:** {task['title']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Status:** {task['status']}")
                st.write(f"**Due Date:** {task['due_date']}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("View", key=f"view_{task['id']}"):
                        st.session_state["selected_task_id"] = task["id"]
                        st.session_state["page"] = "view_task"
                        st.rerun()

                with col2:
                    if st.button("Mark Done", key=f"done_{task['id']}"):
                        api_call(
                            "PATCH",
                            f"/tasks/{task['id']}/status",
                            data={"status": "done"},
                            token=st.session_state["token"]
                        )
                        st.rerun()

                with col3:
                    if st.button("Delete", key=f"delete_{task['id']}"):
                        api_call(
                            "DELETE",
                            f"/tasks/{task['id']}",
                            token=st.session_state["token"]
                        )
                        st.rerun()
    else:
        st.error(tasks.get("detail", "Could not load tasks"))


def show_add_task():
    st.title("Add New Task")

    with st.form("add_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["low", "medium", "high"])
        due_date = st.date_input("Due Date")
        submit = st.form_submit_button("Add Task")

    if submit:
        if title == "":
            st.error("Title is required")
            return

        status_code, result = api_call(
            "POST",
            "/tasks/",
            data={
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": str(due_date)
            },
            token=st.session_state["token"]
        )

        if status_code == 201:
            st.success("Task added successfully")
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error(result.get("detail", "Could not add task"))

    if st.button("Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        st.rerun()


def show_view_task():
    st.title("Task Details")

    task_id = st.session_state["selected_task_id"]

    if task_id is None:
        st.error("No task selected")
        st.session_state["page"] = "dashboard"
        st.rerun()

    status_code, task = api_call(
        "GET",
        f"/tasks/{task_id}",
        token=st.session_state["token"]
    )

    if status_code == 404:
        st.error("Task not found")
        st.session_state["page"] = "dashboard"
        st.rerun()

    elif status_code == 403:
        st.error("You are not allowed to view this task")
        st.session_state["page"] = "dashboard"
        st.rerun()

    elif status_code != 200:
        st.error(task.get("detail", "Could not load task"))
        return

    st.write(f"**ID:** {task['id']}")
    st.write(f"**Title:** {task['title']}")
    st.write(f"**Description:** {task['description']}")
    st.write(f"**Priority:** {task['priority']}")
    st.write(f"**Status:** {task['status']}")
    st.write(f"**Due Date:** {task['due_date']}")
    st.write(f"**Owner:** {task['owner_email']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Edit"):
            st.session_state["page"] = "edit_task"
            st.rerun()

    with col2:
        if st.button("Delete"):
            api_call(
                "DELETE",
                f"/tasks/{task_id}",
                token=st.session_state["token"]
            )
            st.session_state["selected_task_id"] = None
            st.session_state["page"] = "dashboard"
            st.rerun()

    with col3:
        if st.button("Back"):
            st.session_state["page"] = "dashboard"
            st.rerun()


def show_edit_task():
    st.title("Edit Task")

    task_id = st.session_state["selected_task_id"]

    if task_id is None:
        st.error("No task selected")
        st.session_state["page"] = "dashboard"
        st.rerun()

    status_code, task = api_call(
        "GET",
        f"/tasks/{task_id}",
        token=st.session_state["token"]
    )

    if status_code != 200:
        st.error(task.get("detail", "Could not load task"))
        st.session_state["page"] = "dashboard"
        st.rerun()

    priority_options = ["low", "medium", "high"]

    if task["priority"] in priority_options:
        current_priority_index = priority_options.index(task["priority"])
    else:
        current_priority_index = 0

    with st.form("edit_task_form"):
        title = st.text_input("Title", value=task["title"])
        description = st.text_area("Description", value=task["description"] or "")

        priority = st.selectbox(
            "Priority",
            priority_options,
            index=current_priority_index
        )

        try:
            current_due_date = date.fromisoformat(task["due_date"])
        except:
            current_due_date = date.today()

        due_date = st.date_input("Due Date", value=current_due_date)

        submit = st.form_submit_button("Update Task")

    if submit:
        if title == "":
            st.error("Title is required")
            return

        status_code, result = api_call(
            "PUT",
            f"/tasks/{task_id}",
            data={
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": str(due_date)
            },
            token=st.session_state["token"]
        )

        if status_code == 200:
            st.success("Task updated successfully")
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error(result.get("detail", "Could not update task"))

    if st.button("Cancel"):
        st.session_state["page"] = "dashboard"
        st.rerun()


if st.session_state["page"] == "login":
    show_login()

elif st.session_state["page"] == "register":
    show_register()

elif st.session_state["page"] == "dashboard":
    show_dashboard()

elif st.session_state["page"] == "add_task":
    show_add_task()

elif st.session_state["page"] == "view_task":
    show_view_task()

elif st.session_state["page"] == "edit_task":
    show_edit_task()
# Smart Campus 🏫

A web-based campus portal built with **Python and Flask** to help
students access campus services and submit complaints through a simple
interface.

> **Repository:**
> [codeswithaditya/Smart-Campus](https://github.com/codeswithaditya/Smart-Campus)

## ✨ Features

Based on the current project structure, Smart Campus includes pages for:

-   **Login and registration** --- user access pages.
-   **Complaint submission** --- a page for raising a new complaint.
-   **My Complaints** --- a page to view submitted complaints.
-   **Admin dashboard** --- an interface for administrators.
-   **HTML templates and CSS styling** --- templates are stored in
    `templates/` and styles in `static/css/`.

*Note: Update this list if any feature is planned but not yet
implemented.*

## 🧰 Tech Stack

-   **Backend:** Python, Flask (assumed from the project structure;
    confirm in `app.py`)
-   **Frontend:** HTML, CSS
-   **Dependencies:** `requirements.txt`
-   **Version control:** Git and GitHub

## 📁 Project Structure

``` text
Smart-Campus/
├── app.py
├── requirements.txt
├── .gitignore
├── static/
│   └── css/
└── templates/
    ├── admin_dashboard.html
    ├── dashboard.html
    ├── login.html
    ├── my_complaints.html
    ├── new_complaint.html
    └── register.html
```

The exact files may change as the project develops.

## 🚀 Getting Started

### 1. Prerequisites

Install:

-   Python 3.10 or a compatible version for your dependencies
-   Git
-   A terminal or command prompt

### 2. Clone the repository

``` bash
git clone https://github.com/codeswithaditya/Smart-Campus.git
cd Smart-Campus
```

### 3. Create and activate a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

``` bat
.venv\Scripts\activate.bat
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

If the app uses a `.env` file, create one locally and add the variables
required by `app.py` (for example, a secret key or database settings).

**Do not commit `.env`, passwords, API keys, or other secrets to
GitHub.** Keep `.env` in `.gitignore`. If the application does not
require environment variables, skip this step.

### 6. Run the application

``` bash
python app.py
```

Open the local URL shown in your terminal (commonly
`http://127.0.0.1:5000/` for Flask apps).

If the command or URL differs, follow the instructions defined in
`app.py`.

## 🖼️ Screenshots

Add screenshots of your actual application here to help visitors
understand the interface.

``` markdown
![Login page](screenshots/login.png)
![Dashboard](screenshots/dashboard.png)
![Complaint form](screenshots/new-complaint.png)
![Admin dashboard](screenshots/admin-dashboard.png)
```

Create a `screenshots/` folder and add the images before enabling these
links.

## 🔐 Security Notes

-   Never upload `.env` files, credentials, or private keys.
-   Use a strong, unique secret key in production.
-   Validate and sanitize user input.
-   Protect admin-only pages with server-side authorization.
-   Use a production-ready database and deployment configuration before
    handling real user data.

## 🛠️ Troubleshooting

-   **`ModuleNotFoundError`:** Activate the virtual environment and run
    `pip install -r requirements.txt`.
-   **Port already in use:** Stop the other process using the port, or
    configure a different port in the app.
-   **Template or static file not found:** Check that the folder names
    and file paths match the project structure.

## 🗺️ Future Improvements

Possible enhancements, depending on your project goals:

-   Complaint status tracking (e.g. Submitted, In Progress, Resolved)
-   Search and filtering for complaints
-   Role-based access for students and administrators
-   Form validation and helpful error messages
-   Responsive layout for mobile devices
-   Deployment with a public demo link

## 🤝 Contributing

Suggestions and improvements are welcome. For a change, create a branch,
make your update, and open a pull request.

## 📄 License

No license has been specified yet. Add a `LICENSE` file before
describing this project as open source.

------------------------------------------------------------------------

**Developed by Aditya Tiwari**\
[GitHub Repository](https://github.com/codeswithaditya/Smart-Campus)

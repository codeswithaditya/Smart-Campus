from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

app = Flask(__name__, template_folder="templates")

# Secret key .env file se aayegi
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# ==========================================
# MySQL Database Connection
# ==========================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# ==========================================
# Home
# ==========================================

@app.route("/")
def home():
    return redirect(url_for("register"))


# ==========================================
# Student Registration
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return "Please fill in all fields.", 400

        if len(password) < 6:
            return "Password must be at least 6 characters.", 400

        hashed_password = generate_password_hash(password)

        db = None
        cursor = None

        try:
            db = get_db_connection()
            cursor = db.cursor()

            query = """
                INSERT INTO Users (name, email, password, role)
                VALUES (%s, %s, %s, 'student')
            """

            cursor.execute(query, (name, email, hashed_password))
            db.commit()

            return """
                <h2>Registration Successful!</h2>
                <p>Your student account has been created.</p>
                <a href="/login">Go to Login</a>
            """

        except mysql.connector.IntegrityError:
            return """
                <h2>Registration Failed</h2>
                <p>This email may already be registered.</p>
                <a href="/register">Go Back</a>
            """

        except mysql.connector.Error:
            return "Database error during registration. Check your database connection.", 500

        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    return render_template("register.html")


# ==========================================
# Login
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = None
        cursor = None

        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM Users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()

            password_ok = False

            if user:
                stored_password = user["password"]

                # Modern hashed password
                if stored_password.startswith(("scrypt:", "pbkdf2:")):
                    password_ok = check_password_hash(stored_password, password)

                # Old plain-text account: convert to hash after successful login
                else:
                    password_ok = (stored_password == password)

                    if password_ok:
                        new_hash = generate_password_hash(password)

                        cursor.execute(
                            """
                            UPDATE Users
                            SET password = %s
                            WHERE user_id = %s
                            """,
                            (new_hash, user["user_id"])
                        )
                        db.commit()

            if not user or not password_ok:
                return "Invalid email or password.", 401

            # Start a fresh session after login
            session.clear()
            session["student_id"] = user["user_id"]
            session["student_name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        except mysql.connector.Error:
            return "Database error during login. Check your database connection.", 500

        finally:
            if cursor:
                cursor.close()
            if db and db.is_connected():
                db.close()

    return render_template("login.html")


# ==========================================
# Admin Dashboard
# ==========================================

@app.route("/admin/dashboard")
def admin_dashboard():

    # Must be logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Only admin can access this route
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT
                c.complaint_id,
                c.title,
                c.description,
                c.priority,
                c.status,
                c.created_at,
                u.name AS student_name,
                u.email AS student_email,
                cat.category_name
            FROM Complaints c
            JOIN Users u
                ON c.user_id = u.user_id
            JOIN Categories cat
                ON c.category_id = cat.category_id
            ORDER BY c.created_at DESC
        """

        cursor.execute(query)
        complaints = cursor.fetchall()

        return render_template(
            "admin_dashboard.html",
            complaints=complaints
        )

    except mysql.connector.Error:
        return "Could not load admin dashboard. Check database tables.", 500

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# Admin: Update Complaint Status and Remark
# ==========================================

@app.route(
    "/admin/complaint/update/<int:complaint_id>",
    methods=["POST"]
)
def update_complaint(complaint_id):

    # Must be logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Only admin can update complaints
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status", "").strip()
    remark = request.form.get("remark", "").strip()

    allowed_statuses = ["Pending", "In Progress", "Resolved"]

    if status not in allowed_statuses:
        return "Invalid complaint status.", 400

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Update complaint's current status
        update_query = """
            UPDATE Complaints
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE complaint_id = %s
        """

        cursor.execute(update_query, (status, complaint_id))

        # Make sure the complaint ID exists
        if cursor.rowcount == 0:
            db.rollback()
            return "Complaint not found.", 404

        # Save admin's remark in complaint update history
        # Confirm that your database table is named complaint_updates.
        remark_query = """
            INSERT INTO complaint_updates
                (complaint_id, admin_id, status, remark)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            remark_query,
            (
                complaint_id,
                session["student_id"],
                status,
                remark
            )
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    except mysql.connector.Error:
        if db:
            db.rollback()
        return (
            "Could not update complaint. Check the complaint_updates table "
            "and its column names in MySQL.",
            500
        )

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# Student Dashboard
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect(url_for("login"))

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        student_id = session["student_id"]

        # Complaint statistics
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(status = 'Pending') AS pending,
                SUM(status = 'In Progress') AS in_progress,
                SUM(status = 'Resolved') AS resolved
            FROM Complaints
            WHERE user_id = %s
            """,
            (student_id,)
        )

        stats = cursor.fetchone()

        total = stats["total"] or 0
        pending = stats["pending"] or 0
        in_progress = stats["in_progress"] or 0
        resolved = stats["resolved"] or 0

        # Latest five complaints
        cursor.execute(
            """
            SELECT
                c.complaint_id,
                c.title,
                c.description,
                c.priority,
                c.status,
                c.created_at,
                cat.category_name
            FROM Complaints c
            JOIN Categories cat
                ON c.category_id = cat.category_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
            LIMIT 5
            """,
            (student_id,)
        )

        recent_complaints = cursor.fetchall()

        return render_template(
            "dashboard.html",
            name=session["student_name"],
            total=total,
            pending=pending,
            in_progress=in_progress,
            resolved=resolved,
            recent_complaints=recent_complaints
        )

    except mysql.connector.Error:
        return "Could not load student dashboard. Check database connection.", 500

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# Student: Submit New Complaint
# ==========================================

@app.route("/complaint/new", methods=["GET", "POST"])
def new_complaint():

    if "student_id" not in session:
        return redirect(url_for("login"))

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == "POST":
            category_id = request.form.get("category_id", "").strip()
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            priority = request.form.get("priority", "").strip()

            allowed_priorities = ["Low", "Medium", "High"]

            if not category_id or not title or not description:
                return "Please complete all complaint fields.", 400

            if priority not in allowed_priorities:
                return "Invalid priority.", 400

            query = """
                INSERT INTO Complaints
                    (user_id, category_id, title, description, priority)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    session["student_id"],
                    category_id,
                    title,
                    description,
                    priority
                )
            )

            db.commit()
            return redirect(url_for("dashboard"))

        cursor.execute("SELECT * FROM Categories ORDER BY category_name")
        categories = cursor.fetchall()

        return render_template(
            "new_complaint.html",
            categories=categories
        )

    except mysql.connector.Error:
        if db:
            db.rollback()
        return "Could not process complaint. Check your database tables.", 500

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# Student: My Complaints
# ==========================================

@app.route("/complaints")
def my_complaints():

    if "student_id" not in session:
        return redirect(url_for("login"))

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT
                c.complaint_id,
                c.title,
                c.description,
                c.priority,
                c.status,
                c.created_at,
                cat.category_name,
                (
                    SELECT cu.remark
                    FROM complaint_updates cu
                    WHERE cu.complaint_id = c.complaint_id
                    ORDER BY cu.updated_at DESC
                    LIMIT 1
                ) AS admin_remark
            FROM Complaints c
            JOIN Categories cat
                ON c.category_id = cat.category_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """

        cursor.execute(query, (session["student_id"],))
        complaints = cursor.fetchall()

        return render_template(
            "my_complaints.html",
            complaints=complaints
        )

    except mysql.connector.Error:
        return (
            "Could not load your complaints. Check the complaint_updates table.",
            500
        )

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# ==========================================
# Logout
# ==========================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================================
# Run Flask App
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
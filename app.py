import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db import get_db_connection, init_db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_voting_key_xyz123')


# --- Initialize DB (ONLY ONCE) ---
try:
    init_db()
except Exception as e:
    print("DB INIT ERROR:", e)


# --- Middleware ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Administrator access required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("Email is already registered.", "danger")
                    return redirect(url_for('register'))

                cursor.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'voter')",
                    (name, email, hashed_pw)
                )

            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('login'))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    session['name'] = user['name']

                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    flash("Invalid email or password.", "danger")

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")

        finally:
            conn.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "primary")
    return redirect(url_for('login'))


# --- Voter Routes ---

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT has_voted FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            has_voted = user['has_voted'] if user else False

            candidates = []
            if not has_voted:
                cursor.execute("SELECT * FROM candidates")
                candidates = cursor.fetchall()

        return render_template('dashboard.html', has_voted=has_voted, candidates=candidates)

    except Exception:
        flash("Could not load dashboard data.", "danger")
        return redirect(url_for('index'))

    finally:
        conn.close()


@app.route('/vote/<int:candidate_id>', methods=['POST'])
@login_required
def vote(candidate_id):
    if session.get('role') == 'admin':
        flash("Admins cannot vote.", "danger")
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT has_voted FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()

            if user['has_voted']:
                flash("You have already voted.", "warning")
                return redirect(url_for('dashboard'))

            cursor.execute(
                "INSERT INTO votes (user_id, candidate_id) VALUES (%s, %s)",
                (session['user_id'], candidate_id)
            )

            cursor.execute(
                "UPDATE users SET has_voted = TRUE WHERE id = %s",
                (session['user_id'],)
            )

        conn.commit()
        flash("Vote cast successfully!", "success")

    except Exception:
        conn.rollback()
        flash("Error while voting.", "danger")

    finally:
        conn.close()

    return redirect(url_for('dashboard'))


@app.route('/results')
@login_required
def results():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.name, COUNT(v.id) as vote_count
                FROM candidates c
                LEFT JOIN votes v ON c.id = v.candidate_id
                GROUP BY c.id, c.name
                ORDER BY vote_count DESC
            """)
            results_data = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as count FROM votes")
            total_votes = cursor.fetchone()['count']

        return render_template('results.html', results=results_data, total_votes=total_votes)

    except Exception:
        flash("Could not load results.", "danger")
        return redirect(url_for('dashboard'))

    finally:
        conn.close()


# --- Admin Routes ---

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM candidates")
            candidates = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='voter'")
            total_voters = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as total FROM votes")
            total_votes = cursor.fetchone()['total']

        return render_template('admin_dashboard.html',
                               candidates=candidates,
                               total_voters=total_voters,
                               total_votes=total_votes)

    except Exception:
        flash("Could not load admin dashboard.", "danger")
        return redirect(url_for('index'))

    finally:
        conn.close()


@app.route('/admin/candidate/add', methods=['POST'])
@admin_required
def add_candidate():
    name = request.form.get('name')

    if not name:
        flash("Candidate name is required.", "danger")
        return redirect(url_for('admin_dashboard'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO candidates (name) VALUES (%s)", (name,))
        conn.commit()
        flash("Candidate added successfully.", "success")

    except Exception:
        conn.rollback()
        flash("Error adding candidate.", "danger")

    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/candidate/delete/<int:id>', methods=['POST'])
@admin_required
def delete_candidate(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM candidates WHERE id = %s", (id,))
        conn.commit()
        flash("Candidate removed.", "info")

    except Exception:
        conn.rollback()
        flash("Error removing candidate.", "danger")

    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))


# --- Run App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

# helpers.py
from flask import render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from config import DB_PATH




# ---------- DB utils ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bike_make TEXT NOT NULL,
            bike_model TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def is_ajax_request():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or bool(request.is_json)




# ---------- Register routes ----------
def register_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""

            if not username or not password:
                flash("Please fill in all fields.", "danger")
                return render_template("register.html")

            if password != confirm_password:
                flash("Passwords do not match. Please try again.", "danger")
                return render_template("register.html")

            password_hash = generate_password_hash(password)
            conn = get_db_connection()
            try:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                flash("Account created. You can now log in.", "success")
                return redirect("/login")
            except sqlite3.IntegrityError:
                flash("Username already taken. Choose another.", "warning")
            finally:
                conn.close()

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            if not username or not password:
                flash("Please fill in all fields.", "danger")
                return render_template("login.html")

            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, password_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
            conn.close()

            if user is None:
                flash(f"User '{username}' does not exist. You can register.", "warning")
                return render_template("login.html")
            if not check_password_hash(user["password_hash"], password):
                flash("Incorrect password. Try again.", "danger")
                return render_template("login.html")

            session["user_id"] = user["id"]
            session["username"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect("/")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect("/")

    @app.route("/wishlist")
    def wishlist():
        if "user_id" not in session:
            flash("Please log in to view your wishlist.", "warning")
            return redirect("/login")

        conn = get_db_connection()
        items = conn.execute(
            "SELECT id, bike_make, bike_model FROM wishlist WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()
        conn.close()
        return render_template("wishlist.html", items=items)

    @app.route("/add_to_wishlist", methods=["POST"])
    def add_to_wishlist():
        if "user_id" not in session:
            if is_ajax_request():
                return jsonify({"success": False, "message": "Not logged in"}), 401
            flash("Please log in to manage your wishlist.", "warning")
            return redirect("/login")

        data = request.get_json(silent=True) or {}
        bike_make = request.form.get("bike_make") or data.get("bike_make")
        bike_model = request.form.get("bike_model") or data.get("bike_model")



        if not bike_make or not bike_model:
            if is_ajax_request():
                return jsonify({"success": False, "message": "Missing bike data"}), 400
            flash("Invalid bike data.", "danger")
            return redirect("/wishlist")

        conn = get_db_connection()
        existing = conn.execute(
            "SELECT id FROM wishlist WHERE user_id = ? AND bike_make = ? AND bike_model = ?",
            (session["user_id"], bike_make, bike_model)
        ).fetchone()

        if existing:
            conn.execute("DELETE FROM wishlist WHERE id = ?", (existing["id"],))
            conn.commit()
            conn.close()
            message = f"{bike_make} {bike_model} removed from wishlist"
            if is_ajax_request():
                return jsonify({"success": True, "message": message, "action": "removed"})
            flash(message, "info")
        else:
            conn.execute(
                "INSERT INTO wishlist (user_id, bike_make, bike_model) VALUES (?, ?, ?)",
                (session["user_id"], bike_make, bike_model)
            )
            conn.commit()
            conn.close()
            message = f"{bike_make} {bike_model} added to wishlist"
            if is_ajax_request():
                return jsonify({"success": True, "message": message, "action": "added"})
            flash(message, "success")

        return redirect("/wishlist")

    @app.route("/remove_from_wishlist", methods=["POST"])
    def remove_from_wishlist():
    # Must be logged in
        if "user_id" not in session:
            msg = "Please log in first."
            if is_ajax_request():
                return jsonify({"success": False, "message": msg}), 401
            flash(msg, "warning")
            return redirect("/login")

        # Accept both JSON and form; accept either 'id' or 'wishlist_id'
        data = request.get_json(silent=True) or request.form
        item_id = (data.get("id") or data.get("wishlist_id") or "").strip()

        if not item_id:
            msg = "Missing wishlist item id."
            if is_ajax_request():
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "danger")
            return redirect("/wishlist")

        # Must be an integer
        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            msg = "Invalid wishlist item id."
            if is_ajax_request():
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "danger")
            return redirect("/wishlist")

        # Delete only if it belongs to this user
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM wishlist WHERE id = ? AND user_id = ?",
                (item_id, session["user_id"])
            )
            conn.commit()
            deleted = cur.rowcount  # how many rows actually removed
        finally:
            conn.close()

        if deleted == 0:
            msg = "Item not found or already removed."
            if is_ajax_request():
                return jsonify({"success": False, "message": msg}), 404
            flash(msg, "warning")
            return redirect("/wishlist")

        msg = "Item removed from wishlist."
        if is_ajax_request():
            return jsonify({"success": True, "message": msg})
        flash(msg, "info")
        return redirect("/wishlist")

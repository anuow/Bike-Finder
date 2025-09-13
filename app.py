import os
import requests
from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import Flask, render_template, request, flash, jsonify, redirect,session
from flask_session import Session
from concurrent.futures import ThreadPoolExecutor
from helpers import register_routes, init_db, get_db_connection







from config import API_KEY, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

init_db()
register_routes(app)

# Security: disable caching after each request
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-store"
    return response

def map_usage_to_category(usage, purpose):
    mapping = {
        "city": "standard",
        "offroad": "dual-sport",
        "touring": "touring",
        "mixed": "cruiser" if purpose == "fun" else "sport"
    }
    return mapping.get(usage, "standard")

def map_budget_to_engine(budget):
    ranges = {
        "under_2k": (50, 150),
        "2k_4k": (150, 300),
        "4k_6k": (300, 600),
        "above_6k": (600, 1200)
    }
    return ranges.get(budget, (100, 1200))

def fetch_make(make):
    headers = {"X-Api-Key": API_KEY}
    try:
        response = requests.get(
            "https://api.api-ninjas.com/v1/motorcycles",
            params={"make": make},
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {make}: {e}")
    return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    usage = request.form.get("usage")
    purpose = request.form.get("purpose")
    budget = request.form.get("budget")
    make = request.form.get("make")

    category = map_usage_to_category(usage, purpose)
    min_engine, max_engine = map_budget_to_engine(budget)

    fallback_makes = ["Honda", "Yamaha", "Suzuki", "Bajaj", "KTM"]
    makes_to_query = [make] if make and make != "no_preference" else fallback_makes

    # Fetch bikes in parallel
    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_make, makes_to_query)

    bikes = [bike for result in results for bike in result]

    # Filter bikes
    filtered_bikes = []
    for bike in bikes:
        try:
            cc = float(bike.get("displacement", "").split("ccm")[0].strip())
        except:
            cc = None

        cc_valid = cc and min_engine <= cc <= max_engine
        type_match = category.lower() in (bike.get("type") or "").lower()

        if cc_valid or type_match:
            filtered_bikes.append(bike)

    return render_template("result.html", bikes=filtered_bikes)

@app.route("/bikes")
def bikes():
    makes = ["Honda", "Yamaha", "Suzuki", "Bajaj", "KTM"]
    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_make, makes)

    all_bikes = []
    for result in results:
        all_bikes.extend(result)

    filtered_bikes = []
    for bike in all_bikes:
        try:
            cc = float(bike.get("displacement", "").split("ccm")[0].strip())
            if 100 <= cc <= 1200 and "scooter" not in (bike.get("type") or "").lower():
                filtered_bikes.append(bike)
        except:
            continue

    return render_template("result.html", bikes=filtered_bikes)

@app.route("/scooters")
def scooters():
    makes = ["Honda", "Yamaha", "Suzuki", "Bajaj", "KTM"]
    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_make, makes)

    filtered_scooters = []
    for result in results:
        for bike in result:
            try:
                cc = float(bike.get("displacement", "").split("ccm")[0].strip())
                if 50 <= cc <= 250 and "scooter" in (bike.get("type") or "").lower():
                    filtered_scooters.append(bike)
            except:
                continue

    return render_template("result.html", bikes=filtered_scooters)

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    wishlist_set = set()
    if "user_id" in session:
        conn = get_db_connection()
        wishlist_items = conn.execute(
            "SELECT bike_make, bike_model FROM wishlist WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()
        conn.close()
        wishlist_set = {(row["bike_make"], row["bike_model"]) for row in wishlist_items}

    if not query:
        flash("Please enter a search term.")
        return redirect("/")

    try:
        response = requests.get(
            f"https://api.api-ninjas.com/v1/motorcycles?model={query}",
            headers={"X-Api-Key": API_KEY},
            timeout=5
        )
        response.raise_for_status()
        bikes = response.json()
    except requests.RequestException:
        flash("Error fetching search results. Please try again.")
        return redirect("/")

    return render_template(
        "search_results.html",
        bikes=bikes,
        query=query,
        wishlist_set=wishlist_set
    )


@app.route("/search_suggestions")
def search_suggestions():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    try:
        response = requests.get(
            f"https://api.api-ninjas.com/v1/motorcycles?model={query}",
            headers={"X-Api-Key": API_KEY},
            timeout=5
        )
        response.raise_for_status()
        bikes = response.json()
    except requests.RequestException:
        return jsonify([])

    suggestions = [bike['model'] for bike in bikes if bike.get('model')]
    return jsonify(suggestions[:10])



@app.route("/wishlist/pdf")
def wishlist_pdf():
    if "user_id" not in session:
        flash("Please log in to download your wishlist.", "warning")
        return redirect("/login")

    # Fetch wishlist for current user
    conn = get_db_connection()
    wishlist = conn.execute(
        "SELECT bike_make, bike_model FROM wishlist WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

     # If wishlist is empty, don't create PDF
    if not wishlist:
        flash("Your wishlist is empty — nothing to download!", "info")
        return redirect("/wishlist")

    # Generate PDF in memory
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"{session['username']}'s Wishlist")
    pdf.setFont("Helvetica", 12)

    y = height - 100
    for idx, item in enumerate(wishlist, start=1):
        pdf.drawString(50, y, f"{idx}. {item['bike_make']} {item['bike_model']}")
        y -= 20
        if y < 50:  # new page if running out of space
            pdf.showPage()
            y = height - 50

    pdf.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="wishlist.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)

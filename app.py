from flask import *
import sqlite3
import re

#Creating the Flask
app = Flask(__name__)
#Secret Key for seassion management
app.secret_key = "123"
# Data Base name
DB_NAME = "portal.db"


# --------- HELPER-SIDE ---------

def connect_db():
    """
    Opens a connection path to SQLite Database.
    - Enables foreign key constraints
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets templates use event["name"] etc.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def current_user():
    """
       İf no user is logged in, returns None.
       - check authentication, check admin status
    """
    if "username" not in session:
        return None
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT username, fullname, email, is_admin FROM users WHERE username=?", (session["username"],))
    u = c.fetchone()
    conn.close()
    return u

def password_ok(pw: str) -> bool:
    # Password satisfier
    if pw is None:
        return False
    if len(pw) < 10: # character at least 10
        return False
    if not re.search(r"[A-Z]", pw): # 1 upper case
        return False
    if not re.search(r"[a-z]", pw): # 1 lower case
        return False
    if not re.search(r"\d", pw): # 1 digit
        return False
    return True

def parse_fee(fee_text: str):
    """
    if the event has fee, it gets as string this
    function converted on float to store it
    """
    try:
        return float(fee_text)
    except:
        return None


# ###### HOME(index.html) - STARTS #################
@app.route("/")
@app.route("/index", methods=["GET"])
def index():
    """
        HOME PAGE - that shows the login info and shows society
        list dor searching events
    """
    user = current_user()
    # societies with search combo
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT societyID, name FROM societies ORDER BY name;")
    societies = c.fetchall()
    conn.close()

    return render_template("index.html", user=user, societies=societies, error=None)

# ###### HOME(index.html) - ENDS #################

# ###### REGISTER(register.html) +calls: (register_ok.html) - STARTS #################
@app.route("/register", methods=["GET", "POST"])
def register():
    user = current_user()
    if user:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()

        # Mandatory fields
        if username == "" or password == "" or fullname == "" or email == "":
            return render_template("register.html", user=None, error="All fields are mandatory.")

        # Password rules are fine or not we check here by calling password_ok function
        # if it is fullfiles then we render template again
        if not password_ok(password):
            return render_template(
                "register.html",
                user=None,
                error="Password must be at least 10 characters and include at least one uppercase letter, one lowercase letter, and one digit."
            )
            # id it is not ok then returns the err msg and send none user due to not creatable

        # Admin rule, ergo; be conditional user like name diff on begining
        is_admin = 1 if email.startswith("org-") else 0
        # if created then push the new user attributes to SQLite DB, if the user exist it will catch it - Dont forget
        conn = connect_db()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users(username,password,fullname,email,is_admin) VALUES (?,?,?,?,?)",
                (username, password, fullname, email, is_admin)
            )
            conn.commit()
            conn.close()
            return render_template("register_ok.html", user=None)
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", user=None, error="Username already exists. Please choose another.")

    return render_template("register.html", user=None, error=None)

# ###### REGISTER(register.html) +calls: (register_ok.html) - ENDS #################


# ###### LOGIN(index/LOGIN FORCE) - STARS #################
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    row = c.fetchone()

    # Username Chechker condition, wheather exist or not
    if not row:
        conn.close()
        # show error just under login form (on home)
        c2 = connect_db().cursor()
        c2.execute("SELECT societyID, name FROM societies ORDER BY name;")
        societies = c2.fetchall()
        c2.connection.close()
        return render_template("index.html", user=None, societies=societies, error="Invalid username.")

    c.execute("SELECT username, is_admin FROM users WHERE username=? AND password=?", (username, password))
    ok = c.fetchone()
    conn.close()

    # Password Checker condition, wheathe username is matching with pwd
    if not ok:
        c2 = connect_db().cursor()
        c2.execute("SELECT societyID, name FROM societies ORDER BY name;")
        societies = c2.fetchall()
        c2.connection.close()
        return render_template("index.html", user=None, societies=societies, error="Incorrect password.")

    # when the both condition fullfieled, our user hop in our seassion
    session["username"] = username
    return redirect(url_for("index"))

# ###### LOGIN(index/LOGIN FORCE) - END #################

# ###### LOGOUT - STARTS #################
@app.route("/logout")
def logout():
    """
        SEASSİON DROPED
    """
    session.pop("username", None)
    return redirect(url_for("index"))

# ###### LOGOUT - END #################


# ###### ADVERTISED EVENTS(events.html) - START #################
@app.route("/events", methods=["GET", "POST"])
def events():
    """
    We may seperate this part in two independent get and post but, we desire them to inside
    in same page to decrease the worklflow between backend we foucs them inside as the both
    THUS, events() function bhandles both posting the events with their attributes and their
    as well as, show the events that created by the users.
    """
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    # Admins should manage societies, not announce events (matches spec menu split)
    if user["is_admin"] == 1:
        return redirect(url_for("societies"))

    conn = connect_db()
    c = conn.cursor()

    error = None

    # societies list for checkboxes
    c.execute("SELECT societyID, name FROM societies ORDER BY name;")
    societies = c.fetchall()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        time_date = request.form.get("time_date", "").strip()  # can be any string (spec)
        description = request.form.get("description", "").strip()
        fee_type = request.form.get("fee_type", "free")
        selected_societies = request.form.getlist("societies")

        # all mandatory
        if name == "" or time_date == "" or description == "" or fee_type == "":
            error = "All event fields are mandatory."
        elif len(selected_societies) == 0:
            error = "Select at least one society."
        else:
            fee_value = None
            if fee_type == "paid":
                fee_text = request.form.get("fee", "").strip()
                if fee_text == "":
                    error = "Fee is mandatory for paid events."
                else:
                    fee_value = parse_fee(fee_text)
                    if fee_value is None:
                        error = "Fee must be a number (e.g., 50 or 50.5)."

            if error is None:
                # Created event pushed in the DB, if there is no naming issue
                try:
                    c.execute(
                        "INSERT INTO events(name,time_date,description,fee,owner) VALUES (?,?,?,?,?)",
                        (name, time_date, description, fee_value, user["username"])
                    )
                    event_id = c.lastrowid
                    for sid in selected_societies:
                        c.execute("INSERT INTO event_societies(eventID,societyID) VALUES (?,?)", (event_id, sid))
                    conn.commit()
                except sqlite3.IntegrityError:
                    error = "Event name must be unique."

    # my events
    c.execute(
        "SELECT eventID, name, time_date, description, fee FROM events WHERE owner=? ORDER BY eventID DESC",
        (user["username"],)
    )
    my_events = c.fetchall()

    # map event -> societies string "S1,S2"
    event_soc_map = {}
    for e in my_events:
        c.execute("""
            SELECT s.name
            FROM societies s
            JOIN event_societies es ON s.societyID = es.societyID
            WHERE es.eventID=?
            ORDER BY s.name
        """, (e["eventID"],))
        names = [r["name"] for r in c.fetchall()]
        event_soc_map[e["eventID"]] = ",".join(names)

    conn.close()
    """
        After event attributes has been seleceted the created event sended to frontend portion
    """
    return render_template(
        "events.html",
        user=user,
        societies=societies,
        my_events=my_events,
        event_soc_map=event_soc_map,
        error=error
    )
# ###### ADVERTISED EVENTS(events.html) - END #################

# ###### DELETE EVENTS(events.html */events/<event_id>) - START #################

@app.route("/events/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    conn = connect_db()
    c = conn.cursor()
    # DELETING the event in the DB
    c.execute("DELETE FROM events WHERE eventID=? AND owner=?", (event_id, user["username"]))
    conn.commit()
    conn.close()
    return redirect(url_for("events"))

# ###### DELETE EVENTS(events.html */events/<event_id>) - END #################

# ###### MANAGE SOCIETIES(societies.html)-ADMIN unique - START #################
@app.route("/societies", methods=["GET", "POST"])
def societies():

    """
        Only user with Admin tag will alowed to acces this page to create or manage,
        the societies admin either select or Insert ne societies. nmaing of the societites
        had to be unique !
    """
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    if user["is_admin"] == 0:
        return redirect(url_for("index"))

    conn = connect_db()
    c = conn.cursor()
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name == "":
            error = "Society name is mandatory."
        else:
            try:
                c.execute("INSERT INTO societies(name) VALUES (?)", (name,))
                conn.commit()
            except sqlite3.IntegrityError:
                error = "Society name must be unique."

    c.execute("""
        SELECT s.name AS name, COUNT(es.eventID) AS event_count
        FROM societies s
        LEFT JOIN event_societies es ON s.societyID = es.societyID
        GROUP BY s.societyID
        ORDER BY s.name
    """)
    rows = c.fetchall()
    conn.close()

    return render_template("societies.html", user=user, societies=rows, error=error)

# ###### MANAGE SOCIETIES(societies.html)-ADMIN unique - END #################


# ###### PROFILE(profile.html) - START #################
@app.route("/profile", methods=["GET", "POST"])
def profile():
    """
        On this section user acces his/her own profile and their knowledge like name, pwd, mail etc.
        Thus, usermay update his attributes like name, pwd, mail etc. AND, banckend side, push those updated parts
        into the SQLite DB. Cant change the username because of the username has to be the same.
    """
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    conn = connect_db()
    c = conn.cursor()
    error = None
    success = None

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if fullname == "" or email == "":
            error = "Full name and email are mandatory."
        else:
            # if password provided, validate it
            if password.strip() != "" and not password_ok(password):
                error = "New password must be at least 10 characters and include uppercase, lowercase, and a digit."
            else:
                # update
                if password.strip() == "":
                    c.execute("UPDATE users SET fullname=?, email=? WHERE username=?",
                              (fullname, email, user["username"]))
                else:
                    c.execute("UPDATE users SET fullname=?, email=?, password=? WHERE username=?",
                              (fullname, email, password, user["username"]))
                conn.commit()
                success = "Profile updated successfully."

    c.execute("SELECT username, password, fullname, email, is_admin FROM users WHERE username=?", (user["username"],))
    profile_row = c.fetchone()
    conn.close()

    return render_template("profile.html", user=user, profile=profile_row, error=error, success=success)

# ###### PROFILE(profile.html) - END #################

# ###### SEARCH(search.html) - START #################
@app.route("/search", methods=["GET", "POST"])
def search():
    """
        Search page:
        - Anyone can search (logged in or not)
        - User enters keywords (partial match)
        - Can filter by a society or select ALL
        - If ALL, we show results grouped by each society name
    """
    user = current_user()

    # open DB connection
    conn = connect_db()
    c = conn.cursor()

    # Get all societies
    c.execute("SELECT societyID, name FROM societies ORDER BY name")
    societies = c.fetchall()

    # results will be a dict like: { "Robotics Society": [event rows], "Music Society": [event rows] }
    results_by_soc = {}

    # keep these so we can re-fill the form after submit
    keyword_text = ""
    selected_society = "ALL"

    # ============================
    # GET  → show nothing initially
    # ============================
    if request.method == "GET":
        return render_template(
            "search.html",
            user=user,
            societies=societies,
            results_by_soc=None,
            keyword_text="",
            selected_society="ALL",
            error=None
        )

    # ============================
    # POST → search
    # ============================
    keyword_text = request.form.get("keywords", "").strip()
    selected_society = request.form.get("society", "ALL")

    # split keywords by spaces (example: "game jam robotics" -> ["game","jam","robotics"])
    keywords = [k for k in keyword_text.split() if k.strip() != ""]

    # We build SQL conditions for keywords safely using parameters
    keyword_sql = ""
    keyword_params = []

    # if there are keywords, create OR conditions:
    # for each keyword, it matches any event field we care about (name, time_date, description, etc.)
    if len(keywords) > 0:
        parts = []
        for kw in keywords:
            like = f"%{kw}%"
            parts.append(
                "(e.name LIKE ? OR e.time_date LIKE ? OR e.description LIKE ? OR s.name LIKE ? OR CAST(e.fee AS TEXT) LIKE ?)")
            # add params for the ? placeholders in the same order
            keyword_params.extend([like, like, like, like, like])
        # final form becomes: AND ( (...) OR (...) OR (...) )
        keyword_sql = " AND (" + " OR ".join(parts) + ")"


    # CASE 1: Search across ALL societies
    # We loop each society and run a query for that society,
    # then store results in results_by_soc[society_name]
    if selected_society == "ALL":
        for s in societies:
            # base query: events that belong to this society
            # join is needed because events and societies have many-to-many relationship
            base_sql = """
                SELECT DISTINCT e.eventID, e.name, e.time_date, e.description, e.fee
                FROM events e
                JOIN event_societies es ON e.eventID = es.eventID
                JOIN societies s ON s.societyID = es.societyID
                WHERE es.societyID = ?
            """
            params = [s["societyID"]] # first parameter is the society filter

            # add keyword_sql + order by newest first
            sql = base_sql + keyword_sql + " ORDER BY e.eventID DESC"
            c.execute(sql, params + keyword_params)

            # store list of rows for this society name
            results_by_soc[s["name"]] = c.fetchall()

    # CASE 2: Search in a SINGLE society
    # selected_society is a societyID string coming from the dropdown
    else:
        # find the society name (for table heading)
        soc_name = None
        for s in societies:
            if str(s["societyID"]) == selected_society:
                soc_name = s["name"]
                break

        base_sql = """
            SELECT DISTINCT e.eventID, e.name, e.time_date, e.description, e.fee
            FROM events e
            JOIN event_societies es ON e.eventID = es.eventID
            JOIN societies s ON s.societyID = es.societyID
            WHERE es.societyID = ?
        """

        # run query for that society + keywords
        sql = base_sql + keyword_sql + " ORDER BY e.eventID DESC"
        c.execute(sql, [selected_society] + keyword_params)

        # store results under that one society name
        results_by_soc[soc_name] = c.fetchall()

    # close DB
    conn.close()

    # render results page (same template)
    return render_template(
        "search.html",
        user=user,
        societies=societies,
        results_by_soc=results_by_soc,
        keyword_text=keyword_text,
        selected_society=selected_society,
        error=None
    )

# ###### SEARCH(search.html) - END #################


# ################# EVENT DETAIL - START ###################
@app.route("/event/<int:event_id>")
def event_detail(event_id):
    # show event detail page for a single event
    # anyone can open it (logged in or not)
    user = current_user()

    conn = connect_db()
    c = conn.cursor()

    # get the event by id
    c.execute("SELECT eventID, name, time_date, description, fee FROM events WHERE eventID=?", (event_id,))
    event = c.fetchone()

    # if event doesn't exist, go back to home
    if not event:
        conn.close()
        return redirect(url_for("index"))

    # get societies related to this event (many-to-many)
    c.execute("""
        SELECT s.name
        FROM societies s
        JOIN event_societies es ON s.societyID = es.societyID
        WHERE es.eventID=?
        ORDER BY s.name
    """, (event_id,))
    socs = [r["name"] for r in c.fetchall()]

    conn.close()

    # send event + societies list to template
    return render_template("event_detail.html", user=user, event=event, societies=socs)

# ################# EVENT DETAIL - END ###################


if __name__ == "__main__":
    app.run()

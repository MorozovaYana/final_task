import psycopg2
from flask import Flask, render_template, current_app, g, request
import random
from datetime import datetime
import pytz
from psycopg2.extras import RealDictCursor
from flask import current_app

### Make the flask app
app = Flask(__name__)

### Routes
@app.route('/')
def index():
    return "Hello, world!"  # Whatever is returned from the function is sent to the browser and displayed.

@app.route("/time")
def time():
    now = datetime.now().astimezone(pytz.timezone("US/Central"))
    timestring = now.strftime("%Y-%m-%d %H:%M:%S")  # format the time as a easy-to-read string
    beginning = "<html><body><b>The current time is: "
    ending = "</b></body></html>"
    return render_template("time.html", timestring=timestring)

@app.route("/testyourself")
def test_yourself():
    answers = ["Yana", "Morozova", "ISD31"]
    return random.choice(answers)

@app.route("/random_number")
def random_number():
    n = random.randint(1, 10)
    return render_template("random.html", number=n)

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host="localhost",
            database="practice",
            user="postgres",
            password="1234",
            cursor_factory = RealDictCursor,
        )
    return g.db


@app.cli.command("init")
def init_db():
    """Clear existing data and create new tables."""
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("schema.sql") as file: # open the file
        alltext = file.read() # read all the text
        cur.execute(alltext) # execute all the SQL in the file
    conn.commit()
    print("Initialized the database and cleared tables.")


@app.cli.command('populate')
def populate_db():
    conn = get_db()
    cur = conn.cursor()

    with current_app.open_resource("populate.sql") as file:
        sql = file.read().decode("utf-8")  # важливо!
        cur.execute(sql)

    conn.commit()
    print("Populated database with sample data.")

def debug(msg):
    from flask import current_app
    current_app.logger.debug(msg)

@app.route("/dump")
def dump_entries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    output = ""
    for r in rows:
        debug(str(r))
        output += str(r) + "\n"
    return "Should see database dump here:\n<pre>" + output + "</pre>"

@app.route("/browse")
def browse():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rowlist = cursor.fetchall()
    return render_template('browse.html', entries=rowlist)


@app.route("/flights")
def flights():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM flights ORDER BY id")
    flights = cur.fetchall()
    return render_template("flights.html", flights=flights)

@app.route("/book", methods=["POST"])
def book_flight():
    name = request.form.get("name")
    flight_id = request.form.get("flight_id")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("CALL make_booking(%s, %s)", (name, flight_id))
        conn.commit()
        msg = "Booking successful!"
    except Exception as e:
        conn.commit()
        msg = f"Error: {str(e)}"

    return render_template("booking_result.html", message=msg)

@app.route("/logs")
def logs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cur.fetchall()
    return render_template("logs.html", logs=logs)

### Start flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

@app.before_request
def create_tables():
    db.create_all()

fetch_count = 0

# DB Model
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(500))

# API function
def get_data():
    res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    return res.json()

@app.route("/", methods=["GET"])
def home():
    return '''
    <form action="/echo" method="post">
        <input name="user_input">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route("/health")
def health():
    return "OK", 200

@app.route("/fetch")
def fetch():
    global fetch_count
    fetch_count += 1

    data = get_data()

    entry = Data(value=str(data))
    db.session.add(entry)
    db.session.commit()

    return "Data fetched and saved!"

@app.route("/metrics")
def metrics():
    count = Data.query.count()
    return f"Total records stored: {count}"

@app.route("/echo", methods=["POST"])
def echo():
    user_input = request.form.get("user_input", "")
    return f"You entered: {user_input}"

@app.route("/price")
def price():
    data = get_data()
    price = data["bitcoin"]["usd"]
    return f"Bitcoin price is: ${price}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
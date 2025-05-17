from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask with Gunicorn!"

if __name__ == "__main__":
    app.run()

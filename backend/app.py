from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "¡Hola! Estás detrás del WAF."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)

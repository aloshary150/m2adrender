from flask import Flask, render_template, request, redirect, send_from_directory, flash
import os
import httpx

app = Flask(__name__)
app.secret_key = "secret_key_here"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BOT_TOKEN = "8366818255:AAFcG_h7OzidDuUHWkLdpGFbbtXuvWFYJl0"  # غيره بتوكنك
CHAT_ID = "8492067756"

PASSWORD = "aloshary150"

def send_file_to_telegram(filepath, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(filepath, "rb") as f:
        files = {"document": (filename, f)}
        data = {"chat_id": CHAT_ID}
        with httpx.Client() as client:
            response = client.post(url, data=data, files=files)
    return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                save_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(save_path)

                telegram_response = send_file_to_telegram(save_path, file.filename)
                if telegram_response.get("ok"):
                    flash("File uploaded and sent to Telegram successfully!", "success")
                else:
                    flash("File uploaded but failed to send to Telegram.", "error")

                return redirect("/")
        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = os.listdir(UPLOAD_FOLDER)
                return render_template("files.html", files=files)
            else:
                flash("Incorrect password!", "error")
    return render_template("index.html")

@app.route("/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Deleted file: {filename}", "success")
    else:
        flash("File not found.", "error")
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/main")
def main():
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PASSWORD = "aloshary150"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return redirect("/")
        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = os.listdir(UPLOAD_FOLDER)
                return render_template("files.html", files=files)
    return render_template("index.html")

@app.route("/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect("/")

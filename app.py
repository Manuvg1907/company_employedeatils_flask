import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# --- Setup ---
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///employees.db"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["SECRET_KEY"] = "supersecret"

db = SQLAlchemy(app)

# --- Model ---
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    salary = db.Column(db.String(50))
    logo = db.Column(db.String(200))  # relative path like uploads/filename.png


# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    layout = request.args.get("layout", "ltr")
    employees = Employee.query.all()
    return render_template("template.html", layout=layout, employees=employees)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    age = request.form.get("age")
    qualification = request.form.get("qualification")
    salary = request.form.get("salary")

    logo_path = None
    if "logo" in request.files:
        logo = request.files["logo"]
        if logo and logo.filename != "":
            filename = secure_filename(logo.filename)
            upload_dir = app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            logo.save(filepath)
            logo_path = f"uploads/{filename}"  # store relative path

    new_employee = Employee(
        name=name,
        age=age,
        qualification=qualification,
        salary=salary,
        logo=logo_path
    )
    db.session.add(new_employee)
    db.session.commit()

    current_layout = request.form.get("current_layout", "ltr")
    return redirect(url_for("index", layout=current_layout))


@app.route("/edit/<int:emp_id>", methods=["POST"])
def edit(emp_id):
    employee = Employee.query.get_or_404(emp_id)

    employee.name = request.form.get("name")
    employee.age = request.form.get("age")
    employee.qualification = request.form.get("qualification")
    employee.salary = request.form.get("salary")

    if "logo" in request.files:
        logo = request.files["logo"]
        if logo and logo.filename != "":
            filename = secure_filename(logo.filename)
            upload_dir = app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            logo.save(filepath)
            employee.logo = f"uploads/{filename}"

    db.session.commit()

    current_layout = request.form.get("current_layout", "ltr")
    return redirect(url_for("index", layout=current_layout))


@app.route("/delete/<int:emp_id>", methods=["POST"])
def delete(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    db.session.delete(employee)
    db.session.commit()
    current_layout = request.form.get("current_layout", "ltr")
    return redirect(url_for("index", layout=current_layout))


# --- Run ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

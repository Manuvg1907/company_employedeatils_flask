import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# In-memory storage
employees = {}
emp_id_counter = 1


@app.route("/", methods=["GET"])
def index():
    header_layout = request.args.get("header_layout", "center")
    logo_layout = request.args.get("logo_layout", "center")
    layout = request.args.get("layout", "ltr")

    return render_template(
        "template.html",
        employees=employees.values(),
        header_layout=header_layout,
        logo_layout=logo_layout,
        layout=layout,
    )


@app.route("/add_employee", methods=["POST"])
def add_employee():
    global emp_id_counter
    name = request.form["name"]
    age = request.form["age"]
    qualification = request.form["qualification"]
    salary = request.form["salary"]

    file = request.files.get("logo")
    photo_filename = None
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        photo_filename = f"{emp_id_counter}_{filename}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

    employees[emp_id_counter] = {
        "id": emp_id_counter,
        "name": name,
        "age": age,
        "qualification": qualification,
        "salary": salary,
        "photo": f"uploads/{photo_filename}" if photo_filename else None,
    }
    emp_id_counter += 1
    return redirect(url_for("index"))


@app.route("/edit/<int:emp_id>", methods=["POST"])
def edit(emp_id):
    if emp_id not in employees:
        return "Employee not found", 404

    name = request.form["name"]
    age = request.form["age"]
    qualification = request.form["qualification"]
    salary = request.form["salary"]

    file = request.files.get("logo")
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        photo_filename = f"{emp_id}_{filename}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
        employees[emp_id]["photo"] = f"uploads/{photo_filename}"

    employees[emp_id].update({
        "name": name,
        "age": age,
        "qualification": qualification,
        "salary": salary,
    })

    return redirect(url_for("index"))


@app.route("/delete/<int:emp_id>", methods=["POST"])
def delete(emp_id):
    if emp_id in employees:
        employees.pop(emp_id)
    return redirect(url_for("index"))


@app.route("/employee_pdf/<int:emp_id>")
def employee_pdf(emp_id):
    if emp_id not in employees:
        return "Employee not found", 404

    emp = employees[emp_id]
    pdf_filename = f"employee_{emp_id}.pdf"
    pdf_path = os.path.join("static", pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add image FIRST
    if emp["photo"]:
        image_path = os.path.join("static", emp["photo"])
        if os.path.exists(image_path):
            story.append(Image(image_path, width=200, height=200))
            story.append(Spacer(1, 20))

    # Add details
    story.append(Paragraph("<b>Employee Details</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Name: {emp['name']}", styles["Normal"]))
    story.append(Paragraph(f"Age: {emp['age']}", styles["Normal"]))
    story.append(Paragraph(f"Qualification: {emp['qualification']}", styles["Normal"]))
    story.append(Paragraph(f"Salary: {emp['salary']}", styles["Normal"]))

    doc.build(story)
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

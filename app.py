from flask import Flask,  render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    duedate = db.Column(db.DateTime, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")


# If id password matched, redirect to dashboard.html
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "Student" and password == "Student":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Username Or Password"

    return redirect(url_for("index"))


@app.route("/signout")
def signout():
    session.pop("user", None)
    return redirect(url_for("index"))


#To make a new task and add it to database and redirect to dashboard.html
@app.route("/add-task", methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect(url_for("index"))
    task_text = request.form.get("task")
    duedate_str = request.form.get("duedate")

    duedate = datetime.strptime(duedate_str, "%Y-%m-%d")

    new_task = Task(
        task=task_text,
        status="Pending",
        duedate=duedate
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for("dashboard"))


#This is to update the same task to dashboard frontend
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("index"))

    tasks = Task.query.all()
    return render_template("dashboard.html", tasks=tasks)


#To delete a task
@app.route("/delete/<int:id>")
def delete_task(id):
    if "user" not in session:
        return redirect(url_for("index"))
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard"))


#Redirect to edit.html for editing
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    if "user" not in session:
        return redirect(url_for("index"))
    task = Task.query.get_or_404(id)
    return render_template("edit.html", task=task)


#Edit the task and redirect back to dashboard
@app.route("/update/<int:id>", methods={"POST"})
def update_task(id):
    if "user" not in session:
        return redirect(url_for("index"))
    task = Task.query.get_or_404(id)
    task.task = request.form.get("task") 
    duedate_str = request.form.get("duedate")
    task.duedate = datetime.strptime(duedate_str, "%Y-%m-%d")
    db.session.commit()
    return redirect(url_for("dashboard"))


#Route to check status of a task(if checked then status: done)
@app.route("/check-status/<int:id>", methods={"POST"})
def check_status(id):
    if "user" not in session:
        return redirect(url_for("index"))
    task = Task.query.get_or_404(id)

    if request.form.get("status"):
        task.status = "Done"
    else:
        task.status = "Pending"

    db.session.commit()
    return redirect(url_for("dashboard"))


# To run the app
if __name__ == "__main__":
    app.run(debug=True)
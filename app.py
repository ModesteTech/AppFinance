from flask import Flask,render_template,url_for

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/add_transaction")
def add_transaction():
    return render_template("add_transaction.html")

@app.route("/transactions")
def transactions():
    return render_template("transactions.html")

@app.route("/statistics")
def statitics():
    return render_template("statistics.html")

@app.route("/revenues")
def revenues():
    return render_template("revenues.html")

@app.route("/expenses")
def expenses():
    return render_template("expenses.html")

@app.route("/budgets")
def budgets():
    return render_template("budgets.html")

@app.route("/goals")
def goals():
    return render_template("goals.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")








if __name__=="__main__":
    app.run(debug=True)
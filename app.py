from flask import Flask,render_template,url_for,request,redirect,session
from database import get_connection
from dotenv import load_dotenv
import sqlite3,os

app=Flask(__name__)

load_dotenv()

app.secret_key=os.environ["SECRET_KEY"]

@app.route("/")
def index():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("fullname").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not name or not email:
            erreur = "Nom et email obligatoire !"
            return render_template("register.html", erreur=erreur)
        if len(password)<8:
            erreur="Le mot de passe doit contenir au moins 8 caracteres."
            return render_template("register.html", erreur=erreur)
        if password != confirm_password:
            erreur = "Les mots de passe ne correspondent pas !"
            return render_template("register.html", erreur=erreur)

        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO utilisateurs (name, email, password)
                    VALUES (?, ?, ?)
                """, (name, email, password))

                user=conn.execute("""
                SELECT id,name FROM utilisateurs
                WHERE email=?
                """,(email,)).fetchone()

                session["utilisateur_id"]=user[0]
                session["name"]=user[1]

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            erreur = "Cette adresse e-mail est déjà utilisée."
            return render_template("register.html", erreur=erreur)

        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        conn=get_connection()

        user=conn.execute("""
            SELECT id,name,password FROM utilisateurs
            WHERE email=?
        """,(email,)).fetchone()

        conn.close()

        if user is None:
            erreur="Email ou mot de passe incorrect."
            return render_template("login.html",erreur=erreur)

        if password != user[2]:
            erreur="Email ou mot de passe incorrect."
            return render_template("login.html",erreur=erreur)

        session["utilisateur_id"]=user[0]
        session["name"]=user[1]

        return redirect(url_for("index"))
            
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "utilisateur_id" not in session:
            return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/help")
def help():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("help.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/add_transaction", methods=["GET","POST"])
def add_transaction():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        check = request.form.get("type")
        description=request.form.get("description")
        montant=request.form.get("amount")
        categorie=request.form.get("category")
        date=request.form.get("date")
        note=request.form.get("note","")

        conn=get_connection()

        if check=="revenu":
            conn.execute("""
                    INSERT INTO revenues (utilisateur_id,montant,description,note,date_revenu)
                    VALUES(?,?,?,?,?)
                """,(session["utilisateur_id"],montant,description,note,date))
    
            conn.execute("""
                    INSERT INTO categories (utilisateur_id,nom,type)
                    VALUES(?,?,?)
                """,(session["utilisateur_id"],categorie,"revenu"))
            conn.commit()

        elif check=="expense":
            conn.execute("""
                    INSERT INTO depenses (utilisateur_id,montant,description,note,date_depense)
                    VALUES(?,?,?,?,?)
            """,(session["utilisateur_id"],montant,description,note,date))

            conn.execute("""
                        INSERT INTO categories (utilisateur_id,nom,type)
                        VALUES(?,?,?)
                    """,(session["utilisateur_id"],categorie,"depense"))
                    
            conn.commit()
        
        conn.close()

        
    return render_template("add_transaction.html")

@app.route("/transactions")
def transactions():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("transactions.html")

@app.route("/statistics")
def statistics():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("statistics.html")

@app.route("/revenues")
def revenues():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("revenues.html")

@app.route("/expenses")
def expenses():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("expenses.html")

@app.route("/budgets")
def budgets():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("budgets.html")

@app.route("/goals")
def goals():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("goals.html")

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    conn=get_connection()

    if request.method=="POST":
        nom_complet=request.form.get("name").strip()
        email=request.form.get("email").strip().lower()

        if email=="":
            email=conn.execute("""SELECT email FROM utilisateurs WHERE id=?""",(session["utilisateur_id"],)).fetchone()[0]
        if nom_complet=="":
            nom_complet=session["name"]

        conn.execute("""
            UPDATE utilisateurs
            SET name=?, email=?
            WHERE id=?
        """,(nom_complet,email,session["utilisateur_id"],))

        conn.commit()

    user=conn.execute("""
        SELECT name,email,date_creation
        FROM utilisateurs
        WHERE id=?
    """,(session["utilisateur_id"],)).fetchone()

    nom_complet=user[0]
    email=user[1]
    date_creation=user[2].split(" ")[0]

    conn.close()

    return render_template("profile.html",
                            nom_complet=nom_complet,
                            email=email,
                            date_creation=date_creation)

@app.route("/notifications")
def notifications():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("notifications.html")

@app.route("/settings")
def settings():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("settings.html")

@app.route("/add_revenue", methods=["GET","POST"])
def add_revenue():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        description=request.form.get("description")
        montant=request.form.get("amount")
        categorie=request.form.get("category")
        date=request.form.get("date")
        note=request.form.get("note","")

        conn=get_connection()
    
        conn.execute("""
                    INSERT INTO revenues (utilisateur_id,montant,description,note,date_revenu)
                    VALUES(?,?,?,?,?)
                """,(session["utilisateur_id"],montant,description,note,date))
    
        conn.execute("""
                    INSERT INTO categories (utilisateur_id,nom,type)
                    VALUES(?,?,?)
                """,(session["utilisateur_id"],categorie,"revenu"))
                    
        conn.commit()

        conn.close()

    return render_template("add_revenue.html")

@app.route("/add_expense", methods=["GET","POST"])
def add_expense():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        description=request.form.get("description")
        montant=request.form.get("amount")
        categorie=request.form.get("category")
        date=request.form.get("date")
        note=request.form.get("note","")

        conn=get_connection()

        conn.execute("""
            INSERT INTO depenses (utilisateur_id,montant,description,note,date_depense)
            VALUES(?,?,?,?,?)
        """,(session["utilisateur_id"],montant,description,note,date))

        conn.execute("""
                    INSERT INTO categories (utilisateur_id,nom,type)
                    VALUES(?,?,?)
                """,(session["utilisateur_id"],categorie,"depense"))
                
        conn.commit()

        conn.close()

    
    return render_template("add_expense.html")

@app.route("/create_budget")
def create_budget():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("create_budget.html")

@app.route("/create_goal")
def create_goal():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("create_goal.html")

@app.route("/security", methods=["GET","POST"])
def security():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        current=request.form.get("current")
        new_password=request.form.get("new-password")
        confirm=request.form.get("confirm")

        conn=get_connection()

        verified=conn.execute("""
            SELECT password FROM utilisateurs
            WHERE id= ?
        """,(session["utilisateur_id"],)).fetchone()[0]

        if verified==current:
            if len(new_password)>8:
                same=1
                if new_password==confirm:
                    conn.execute("""
                        UPDATE utilisateurs
                        SET password = ?
                        WHERE id = ?
                    """,(new_password,session["utilisateur_id"],))

                    conn.commit()
                    conn.close()

                    
                    succes="Mot de passe modifie avec succes"
                    return render_template("security.html",message=succes,same=same)
                else:
                    same=2
                    erreur="Les mots de passes ne correspondent pas"
                    return render_template("security.html",message=erreur,same=same)
            else:
                        same=3
                        erreur="Le mot de passe doit avoir au moins 8 caracteres"
                        return render_template("security.html",message=erreur,same=same)
        else:
            same=0
            erreur="Mauvais mot de passe"
            return render_template("security.html",message=erreur,same=same)
    
    return render_template("security.html")

@app.route("/about")
def about():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("about.html")

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("login"))

@app.route("/budget_detail")
def budget_detail():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("budget_detail.html")


@app.route("/goal_detail")
def goal_detail():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("goal_detail.html")



if __name__=="__main__":
    app.run(debug=True)
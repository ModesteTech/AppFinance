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

    conn=get_connection()
    
    depenses_enregis=conn.execute("""
        SELECT montant,description,date_depense FROM depenses
        WHERE utilisateur_id= ?
    """,(session["utilisateur_id"],)).fetchall()
    
    revenues_enregis=conn.execute("""
            SELECT montant,description,date_revenu FROM revenues
            WHERE utilisateur_id= ?
        """,(session["utilisateur_id"],)).fetchall()
    
    transactions=[]
    
    depenses=0
    revenues=0
    for i in depenses_enregis:
        transactions.append((*i,"Depense"))
        depenses+=i[0]
    for j in revenues_enregis:
        transactions.append((*j,"Revenu"))
        revenues+=j[0]
    
    transactions.sort(key=lambda x: x[2], reverse=True)
    
    conn.close()

    return render_template("dashboard.html",transactions=transactions,revenues=revenues,depenses=depenses)


@app.route("/transactions")
def transactions():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    conn=get_connection()

    depenses=conn.execute("""
        SELECT montant,description,category,date_depense FROM depenses
        WHERE utilisateur_id= ?
    """,(session["utilisateur_id"],)).fetchall()

    revenues=conn.execute("""
            SELECT montant,description,category,date_revenu FROM revenues
            WHERE utilisateur_id= ?
        """,(session["utilisateur_id"],)).fetchall()

    transactions=[]

    for depense in depenses:
        transactions.append((*depense,"Depense"))
    for revenu in revenues:
        transactions.append((*revenu,"Revenu"))

    transactions.sort(key=lambda x: x[3], reverse=True)

    conn.close()

    return render_template("transactions.html",depenses=depenses,revenues=revenues,transactions=transactions)

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
                    INSERT INTO revenues (utilisateur_id,montant,description,note,date_revenu,category)
                    VALUES(?,?,?,?,?,?)
                """,(session["utilisateur_id"],montant,description,note,date,categorie))
    
            conn.execute("""
                    INSERT INTO categories (utilisateur_id,nom,type)
                    VALUES(?,?,?)
                """,(session["utilisateur_id"],categorie,"revenu"))
            conn.commit()

        elif check=="expense":
            conn.execute("""
                    INSERT INTO depenses (utilisateur_id,montant,description,note,date_depense,category)
                    VALUES(?,?,?,?,?,?)
            """,(session["utilisateur_id"],montant,description,note,date,categorie))

            conn.execute("""
                        INSERT INTO categories (utilisateur_id,nom,type)
                        VALUES(?,?,?)
                    """,(session["utilisateur_id"],categorie,"depense"))
                    
            conn.commit()
        
        conn.close()

        return redirect(url_for("transactions"))

        
    return render_template("add_transaction.html")

@app.route("/revenues")
def revenues():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    conn=get_connection()
    
    revenues=conn.execute("""
            SELECT description,montant,date_revenu,category FROM revenues
            WHERE utilisateur_id= ?
    """,(session["utilisateur_id"],)).fetchall()

    argent=conn.execute("""
                SELECT montant FROM revenues
                WHERE utilisateur_id= ?
        """,(session["utilisateur_id"],)).fetchall()

    nbr_revenu=len(argent)

    somme=0
    for i in range(nbr_revenu):
        somme=somme+argent[i][0]
    

    if nbr_revenu==0:
        revenu_moyen=0
    else:
        revenu_moyen=somme/nbr_revenu

    revenu_moyen=round(revenu_moyen,2)

    revenues.sort(key= lambda t:t[2],reverse=True)

    conn.close()

    return render_template("revenues.html",revenues=revenues,somme=somme,nbr_revenu=nbr_revenu,revenu_moyen=revenu_moyen)

@app.route("/add_revenue", methods=["GET", "POST"])
def add_revenue():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        description = request.form.get("description")
        montant = request.form.get("amount")
        categorie = request.form.get("category")
        date = request.form.get("date")
        note = request.form.get("note", "")

        conn = get_connection()

        conn.execute("""
                    INSERT INTO revenues
                    (utilisateur_id, montant, description, note, date_revenu, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                session["utilisateur_id"],
                montant,
                description,
                note,
                date,
                categorie
            ))

        conn.execute("""
                    INSERT INTO categories (utilisateur_id, nom, type)
                    VALUES (?, ?, ?)
                """, (
                session["utilisateur_id"],
                categorie,
                "revenu"
            ))

        conn.commit()
        conn.close()

        return redirect(url_for("revenues"))

    return render_template("add_revenue.html")

@app.route("/expenses")
def expenses():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))

    conn=get_connection()
    
    depenses=conn.execute("""
            SELECT description,montant,date_depense,category FROM depenses
            WHERE utilisateur_id= ?
    """,(session["utilisateur_id"],)).fetchall()

    argent=conn.execute("""
                SELECT montant FROM depenses
                WHERE utilisateur_id= ?
        """,(session["utilisateur_id"],)).fetchall()

    nbr_depense=len(argent)

    somme=0
    for i in range(nbr_depense):
        somme=somme+argent[i][0]
    

    if nbr_depense==0:
        depense_moyen=0
    else:
        depense_moyen=somme/nbr_depense

    depense_moyen=round(depense_moyen,2)

    depenses.sort(key=lambda t: t[2],reverse=True)

    conn.close()

    return render_template("expenses.html",depenses=depenses,somme=somme,nbr_depense=nbr_depense,depense_moyen=depense_moyen)

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
            INSERT INTO depenses (utilisateur_id,montant,description,note,date_depense,category)
            VALUES(?,?,?,?,?,?)
        """,(session["utilisateur_id"],montant,description,note,date,categorie))

        conn.execute("""
                    INSERT INTO categories (utilisateur_id,nom,type)
                    VALUES(?,?,?)
                """,(session["utilisateur_id"],categorie,"depense"))
                
        conn.commit()
        conn.close()

        return redirect(url_for("expenses"))

    
    return render_template("add_expense.html")


@app.route("/budgets")
def budgets():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("budgets.html")

@app.route("/create_budget")
def create_budget():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("create_budget.html")

@app.route("/budget_detail")
def budget_detail():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("budget_detail.html")

@app.route("/goals")
def goals():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("goals.html")

@app.route("/create_goal")
def create_goal():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("create_goal.html")

@app.route("/goal_detail")
def goal_detail():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("goal_detail.html")

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
            SET name=?,
            email=?
            WHERE id=?
        """,(nom_complet,email,session["utilisateur_id"],))
        if nom_complet != "":
            session["name"]=nom_complet

        conn.commit()

        return redirect(url_for("dashboard"))

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

@app.route("/statistics")
def statistics():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("statistics.html")

@app.route("/notifications")
def notifications():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("notifications.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/settings")
def settings():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("settings.html")

@app.route("/help")
def help():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("help.html")

@app.route("/about")
def about():
    if "utilisateur_id" not in session:
        return redirect(url_for("login"))
    return render_template("about.html")

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)
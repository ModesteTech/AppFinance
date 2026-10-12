from database import get_connection

def init_db():
    connection=get_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS utilisateurs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS revenues(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            montant REAL NOT NULL CHECK(montant > 0),
            description TEXT NOT NULL,
            note TEXT,
            date_revenu DATE NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id)
            ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS depenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            montant REAL NOT NULL CHECK(montant > 0),
            description TEXT NOT NULL,
            note TEXT,
            date_depense DATE NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id)
            ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            nom TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('revenu','depense')),
            FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id)
            ON DELETE CASCADE,
            UNIQUE (utilisateur_id,nom,type)
        );

    """)

    connection.commit()
    connection.close()
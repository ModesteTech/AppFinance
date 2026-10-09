from database import get_connection

with open("schema.sql","r",encoding="utf-8") as fichier :
    schema=fichier.read()

with get_connection() as connection:
    with connection.cursor() as curseur:
        curseur.execute(schema)
        print("Table cree avec succes")
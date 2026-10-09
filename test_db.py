from database import get_connection

try:
    connection=get_connection()
    print("conexion reussi")
    connection.close()
except Exception as erreur:
    print("connexion echoue:",erreur)
import sqlite3

def get_connection():
    connection = sqlite3.connect("wandji_finance.db")

    connection.row_factory=sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")

    return connection

import sqlite3

conn = sqlite3.connect('artistsStored.db')
c = conn.cursor()

lyrics = [triple[2] for triple in c.execute('SELECT * FROM Lyrics').fetchall()]

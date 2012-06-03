import sqlite3
import time
conn = sqlite3.connect('/tmp/mud-testing')

(lambda c:
	c.executescript("""
BEGIN;
CREATE TABLE IF NOT EXISTS globalevents (id INTEGER PRIMARY KEY, type, text, time);
CREATE TABLE IF NOT EXISTS roomevents (id INTEGER PRIMARY KEY, type, text, time);
CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, name, description, owner);
CREATE TABLE IF NOT EXISTS exits (id INTEGER PRIMARY KEY, src, dest, name, description);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name UNIQUE, pass);
COMMIT;
""")
)(conn.cursor())

while True:
	time.sleep(10)
	c=conn.cursor()
	print "Inserting tone, "+time.asctime()
	c.execute("INSERT INTO globalevents (type, text, time) VALUES ('time',?,datetime('now'));",("At the tone, the time will be: "+time.asctime(),))
	c.close()
	conn.commit()

#!/usr/bin/env python2.6
from __future__ import print_function
import sqlite3
import readline
import signal
import sys
import time
from getpass import getpass
from hashlib import sha256
conn = sqlite3.connect('mud-testing.db')

globalid = 0
player = None

pollrate = 2


PROMPT = '> '

def process(sig,stack):
	global globalid
	if sig != signal.SIGALRM:
		print("Something's up. Expected signal",signal.SIGALRM,"but got",sig)
		raise
	c = conn.cursor()
	c.execute("SELECT id,type,text,strftime('%s',time) FROM globalevents WHERE id > ?",(globalid,))
	result = c.fetchone()
	if result == None:
		signal.alarm(pollrate)
		return
	print()
	while result != None:
		globalid = result[0]
		print("[%s] Event type '%s': '%s'"%(time.ctime(float(result[3])),result[1],result[2]))
		result = c.fetchone()
	signal.alarm(pollrate)
	print(PROMPT, readline.get_line_buffer(), sep='', end='')
	sys.stdout.flush()
	c.close()

def globalevent(type,text):
	c = conn.cursor()
	c.execute("INSERT INTO globalevents (type, text, time) VALUES (?,?,datetime('now'))",(type,text,))
	conn.commit()
	c.close()

def command(text):
	global player
	c = conn.cursor()
	
	c.close()

c = conn.cursor()
while player == None:
	username = raw_input("Username: ")
	if username == "new":
		username = raw_input("New username: ")
		c.execute("SELECT name FROM users WHERE name = ?",(username,))
		if c.fetchone() != None:
			print("Sorry, that username is taken.")
			continue
		passhash = sha256(getpass("New password: ")).hexdigest()
		if passhash != sha256(getpass("Confirm password: ")).hexdigest():
			print("Passwords didn't match.")
			continue
		try:
			c.execute("INSERT INTO users (name,pass) VALUES (?,?)",(username,passhash,))
		except IntegrityError:
			print("Database collision... Someone snuck in and grabbed it while you were typing?")
			continue
	passhash = sha256(getpass("Password: ")).hexdigest()
	print("Logging in as",username,"with password",passhash)
	c.execute("SELECT id,name,pass FROM users WHERE name = ? AND pass = ?",(username,passhash,))
	result = c.fetchone()
	if result == None:
		print("Sorry, that's not a valid login.")
		print("If you want to make an account, log in as 'new'")
		continue
	player = dict(zip(("id","name","pass"),result))
globalevent('login',"%s logged in"%player['name'])
conn.commit()
c.close()
print(player)

while True:
	try:
		signal.alarm(pollrate)
		signal.signal(signal.SIGALRM,process)
		x = str(raw_input(PROMPT))
		print("Got back a value: ",x)
	except EOFError:
		print()
		print("Got end of file. Goodbye!")
		sys.exit(0)
	except KeyboardInterrupt:
		print()
		print("Got ^C. To exit, ^D.")
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise

#!/usr/bin/env python2.6
from __future__ import print_function
import sqlite3
import readline
import signal
import sys
conn = sqlite3.connect('/tmp/mud-testing')
c=conn.cursor()
globalid = 0
pollrate = 2

PROMPT = '> '

def process(sig,stack):
	global globalid
	if sig != signal.SIGALRM:
		print("Something's up. Expected signal",signal.SIGALRM,"but got",sig)
		raise
	c.execute("SELECT id,type,text FROM globalevents WHERE id > ?",(globalid,))
	result = c.fetchone()
	if result == None:
		signal.alarm(pollrate)
		return
	print()
	while result != None:
		globalid = result[0]
		print("Event type '%s': '%s'"%(result[1],result[2]))
		result = c.fetchone()
	signal.alarm(pollrate)
	print(PROMPT, readline.get_line_buffer(), sep='', end='')
	sys.stdout.flush()

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

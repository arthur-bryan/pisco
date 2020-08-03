from telnetlib import Telnet
from time import sleep

tl = Telnet("10.0.0.10")
tl.set_debuglevel(1)
tl.read_until(b"Username:", 1)
tl.write("admin\n".encode('ascii'))
sleep(1)
tl.read_until(b"Password:", 1)
tl.write("admin\n".encode('ascii'))
sleep(1)

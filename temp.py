import sys


[sys.stdout.buffer.write(b'Hello!\n') for _ in range(100000)]

sys.stdout.flush()
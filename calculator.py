import time

i = 0
while True:
    with open('/tmp/bus', 'w') as f:
        f.write(str(i))
    i = i + 1
    time.sleep(0.5)
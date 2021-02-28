import time

i = 0
while True:
    with open('/tmp/calculatorToInterfaceA429', 'w') as f:
        f.write(str(i))
    i = i + 1
    time.sleep(1)
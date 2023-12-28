
import random
import time

while True:
    with open("./statFile","w") as f:
        n = random.random()
        f.write(str(n))
        f.close
    time.sleep(1)

import random, time


# print('Username:', input('Username: '))

while (data := input('-> ')) != 'quit':
    for _ in range(random.randrange(10)):
        time.sleep(0.5)
        print(data)
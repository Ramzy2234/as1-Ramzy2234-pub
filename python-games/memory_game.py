import random
import time

sequence = []
round_num = 1

while True:
    print(f"\nRound {round_num}")
    sequence.append(random.randint(1, 9))

    print("Memorise:")
    for num in sequence:
        print(num, end=" ", flush=True)
        time.sleep(0.7)

    time.sleep(1)
    print("\n" * 20)

    guess = input("Enter sequence (space separated): ")
    guess_list = list(map(int, guess.split()))

    if guess_list != sequence:
        print("Wrong sequence!")
        break

    round_num += 1

print("You reached round", round_num)
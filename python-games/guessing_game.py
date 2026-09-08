import random

level = 1
score = 0

while True:
    max_number = level * 20
    secret = random.randint(1, max_number)
    lives = 5

    print(f"\nLEVEL {level}")
    print(f"Guess a number between 1 and {max_number}")

    while lives > 0:
        guess = input("Your guess: ")

        if not guess.isdigit():
            print("Enter a number.")
            continue

        guess = int(guess)
        lives -= 1

        diff = abs(secret - guess)

        if guess == secret:
            print("Correct!")
            score += lives * 10
            break
        elif diff <= 3:
            print("🔥 Very hot")
        elif diff <= 7:
            print("Warm")
        else:
            print("Cold")

        print(f"Lives left: {lives}")

    if lives == 0:
        print("Game over!")
        print("The number was:", secret)
        break

    level += 1

print("Final score:", score)

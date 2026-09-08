"""
Program Description:
This program demonstrates "three doors" game show problem, where a contestant wildly picks 
one of three doors, one has a car in one door, while the two doors have goats. 
The simulation is run many times, counting the total amount of times the contestant's random choice 
matches the winning door.

Steps:
1. For each trial, randomly select a winning door and the contestant's door choice.
2. Check if the contestant's choice matches the winning door.
3. Count the number of wins.
4. After all trials, calculate and display the win percentage, which should be close to 33%.

"""

import random

def simulate_game_show(trials):
    """Simulate the game show and return the winning percentage after the specified number of trials."""
    wins = sum(1 for _ in range(trials) if random.randint(1, 3) == random.randint(1, 3))
    return (wins / trials) * 100

def main():
    trials = 100000  # Define the number of trials to get an accurate win percentage
    winning_percentage = simulate_game_show(trials)
    print(f"Winning percentage after {trials} trials: {winning_percentage:.2f}%")

if __name__ == "__main__":
    main()


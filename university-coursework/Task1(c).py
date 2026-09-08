# Top-Down Algorithm Design:
# 1. Begin the program.
# 2. Prompt the user to press a string of single-digit numbers.
# 3. Start a variable total_sum to 0.
# 4. For every character in the string:
#    a. Change and convert the character to an integer.
#    b. Add the integer to total_sum.
# 5. After inputting all digits, print the total_sum.
# 6. Finish the program.

def sum_of_digits_in_string():
    # Step 2: Ask the user for input
    user_input = input("Enter a series of single-digit numbers: ")

    # Step 3: Start total_sum to 0
    total_sum = 0

    # Step 4: Loop through every character in the string
    for char in user_input:
        # Convert the character to an integer and add to the total_sum
        total_sum += int(char)
    
    # Step 5: Show the sum of the digits
    print(f"The sum of the digits is: {total_sum}")

# Recall the function to Begin the program
sum_of_digits_in_string()

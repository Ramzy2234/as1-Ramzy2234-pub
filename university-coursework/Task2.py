# Collecting user input
name = input("Enter your name: ")
weight_kg = float(input("Enter your weight in kg: "))
height_cm = float(input("Enter your height in cm: "))

# Calculating BMI
height_m = height_cm / 100  # Convert cm to metres
bmi = round(weight_kg / (height_m ** 2), 2)  # Calculate and round BMI to 2 decimal places

# Determining BMI categories
if bmi < 18.5:
    category = "underweight"
elif 18.5 <= bmi < 25.0:
    category = "healthy"
elif 25.0 <= bmi < 30.0:
    category = "overweight"
else:
    category = "obese"

# Save the result to a file
filename = "bmi.csv"
file = open(filename, "a")  # Open file within append mode
file.write(f"{name}, {height_cm}, {weight_kg}, {bmi}, {category}\n")  # Write data in a different format
file.close()  # Close down the file

# Output the result to user interference for console 
print(f"{name}, Height: {height_cm} cm, Weight: {weight_kg} kg, BMI: {bmi}, Category: {category}")


# Convert the factor from light-years to kilometres
LY_to_KM = 9.461e12  # 1 lightyear = 9.461 trillion kilometers

# Loop to continuously asking for user input
while True:
    try:
        # Get the main input value within lightyears
        ly_value = float(input("Enter the value in lightyears (LY) to convert to kilometers (KM): "))
        
        # Convert lightyears to kilometers
        km_value = ly_value * LY_to_KM
        
        # Show the whole result
        print(f"{ly_value} lightyears is approximately {km_value:.2f} kilometers.")
        
    except ValueError:
        print("Please enter a valid numeric value.")
        continue
    
    # Ask if the user wants to complete one other conversion
    repeat = input("Would you like to convert another value? (yes/no): ").strip().lower()
    
    # Leave loop if the user does not want to carry on
    if repeat != "yes":
        print("Goodbye!")
        break

password = input("Enter password: ")

score = 0

if len(password) >= 8:
    score += 1
if any(c.isupper() for c in password):
    score += 1
if any(c.isdigit() for c in password):
    score += 1
if any(not c.isalnum() for c in password):
    score += 1

levels = ["Weak", "Medium", "Strong", "Very Strong"]
print("Strength:", levels[score-1])

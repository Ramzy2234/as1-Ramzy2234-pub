students = {}

while True:
    name = input("Student name (or exit): ")
    if name == "exit":
        break

    marks = list(map(int, input("Enter marks: ").split()))
    avg = sum(marks) / len(marks)

    if avg >= 70:
        grade = "A"
    elif avg >= 60:
        grade = "B"
    elif avg >= 50:
        grade = "C"
    else:
        grade = "Fail"

    students[name] = {"average": avg, "grade": grade}

for s, data in students.items():
    print(s, data)

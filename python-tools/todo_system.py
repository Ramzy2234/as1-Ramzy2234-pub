import json

FILE_NAME = "tasks.json"

try:
    with open(FILE_NAME, "r") as file:
        tasks = json.load(file)
except FileNotFoundError:
    tasks = []

def save_tasks():
    with open(FILE_NAME, "w") as file:
        json.dump(tasks, file, indent=4)

while True:
    print("\n1. Add Task")
    print("2. View Tasks")
    print("3. Complete Task")
    print("4. Exit")

    choice = input("> ")

    if choice == "1":
        name = input("Task name: ")
        priority = input("Priority (low/medium/high): ")
        tasks.append({"name": name, "priority": priority, "done": False})
        save_tasks()

    elif choice == "2":
        for i, task in enumerate(tasks):
            status = "✔" if task["done"] else "✘"
            print(i, task["name"], task["priority"], status)

    elif choice == "3":
        index = int(input("Task index: "))
        tasks[index]["done"] = True
        save_tasks()

    elif choice == "4":
        break

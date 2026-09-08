import json
import time
from datetime import datetime

FILE_NAME = "accounts.json"
LOCK_TIME = 10


class Account:
    def __init__(self, acc_no, name, pin, balance=0):
        self.acc_no = acc_no
        self.name = name
        self.pin = pin
        self.balance = balance
        self.transactions = []
        self.failed_attempts = 0
        self.locked_until = 0

    def is_locked(self):
        return time.time() < self.locked_until

    def log(self, action, amount=0):
        self.transactions.append({
            "action": action,
            "amount": amount,
            "balance": self.balance,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def to_dict(self):
        return {
            "acc_no": self.acc_no,
            "name": self.name,
            "pin": self.pin,
            "balance": self.balance,
            "transactions": self.transactions,
            "failed_attempts": self.failed_attempts,
            "locked_until": self.locked_until
        }


class Bank:
    def __init__(self):
        self.accounts = self.load_accounts()

    def load_accounts(self):
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
                accounts = {}
                for acc_no, info in data.items():
                    acc = Account(
                        acc_no,
                        info["name"],
                        info["pin"],
                        info["balance"]
                    )
                    acc.transactions = info["transactions"]
                    acc.failed_attempts = info["failed_attempts"]
                    acc.locked_until = info["locked_until"]
                    accounts[acc_no] = acc
                return accounts
        except FileNotFoundError:
            return {}

    def save_accounts(self):
        with open(FILE_NAME, "w") as f:
            json.dump(
                {k: v.to_dict() for k, v in self.accounts.items()},
                f,
                indent=4
            )

    # 🔐 ACCOUNT CREATION (PIN IS CREATED HERE)
    def create_account(self, acc_no, name, pin):
        if acc_no in self.accounts:
            raise ValueError("Account already exists")
        self.accounts[acc_no] = Account(acc_no, name, pin)
        self.save_accounts()

    # 🔐 LOGIN (PIN ENFORCED)
    def authenticate(self, acc_no, pin):
        acc = self.accounts.get(acc_no)

        if not acc:
            raise ValueError("Account not found")

        if acc.is_locked():
            remaining = int(acc.locked_until - time.time())
            raise ValueError(f"Account locked. Try again in {remaining}s")

        if pin == acc.pin:
            acc.failed_attempts = 0
            self.save_accounts()
            return acc

        acc.failed_attempts += 1

        if acc.failed_attempts >= 3:
            acc.locked_until = time.time() + LOCK_TIME
            acc.failed_attempts = 0
            self.save_accounts()
            raise ValueError("Too many attempts. Locked for 10 seconds")

        self.save_accounts()
        raise ValueError("Incorrect PIN")

    # 💰 BANKING ACTIONS (ONLY AFTER LOGIN)
    def deposit(self, acc, amount):
        acc.balance += amount
        acc.log("Deposit", amount)
        self.save_accounts()

    def withdraw(self, acc, amount):
        if amount > acc.balance:
            raise ValueError("Insufficient funds")
        acc.balance -= amount
        acc.log("Withdraw", amount)
        self.save_accounts()

    def change_pin(self, acc, old_pin, new_pin):
        if acc.pin != old_pin:
            raise ValueError("Old PIN incorrect")
        acc.pin = new_pin
        self.save_accounts()

    def reset_pin(self, acc_no, new_pin):
        acc = self.accounts.get(acc_no)
        if not acc:
            raise ValueError("Account not found")
        acc.pin = new_pin
        acc.failed_attempts = 0
        acc.locked_until = 0
        self.save_accounts()


def main():
    bank = Bank()

    while True:
        print("\n--- BANK MENU ---")
        print("1. Create Account")
        print("2. Login")
        print("3. Reset PIN (Forgot)")
        print("4. Exit")

        choice = input("> ")

        if choice == "1":
            try:
                bank.create_account(
                    input("Account Number: "),
                    input("Name: "),
                    input("Create PIN: ")
                )
                print("Account created successfully")
            except ValueError as e:
                print(e)

        elif choice == "2":
            try:
                acc = bank.authenticate(
                    input("Account Number: "),
                    input("PIN: ")
                )
                print(f"Welcome {acc.name}")

                # 🔐 LOGGED-IN SESSION
                while True:
                    print("\n--- ACCOUNT MENU ---")
                    print("1. Deposit")
                    print("2. Withdraw")
                    print("3. Check Balance")
                    print("4. Transaction History")
                    print("5. Change PIN")
                    print("6. Logout")

                    opt = input("> ")

                    if opt == "1":
                        bank.deposit(acc, float(input("Amount: ")))

                    elif opt == "2":
                        try:
                            bank.withdraw(acc, float(input("Amount: ")))
                        except ValueError as e:
                            print(e)

                    elif opt == "3":
                        print("Balance:", acc.balance)

                    elif opt == "4":
                        for t in acc.transactions:
                            print(t)

                    elif opt == "5":
                        try:
                            bank.change_pin(
                                acc,
                                input("Old PIN: "),
                                input("New PIN: ")
                            )
                            print("PIN changed")
                        except ValueError as e:
                            print(e)

                    elif opt == "6":
                        break

            except ValueError as e:
                print(e)

        elif choice == "3":
            try:
                bank.reset_pin(
                    input("Account Number: "),
                    input("New PIN: ")
                )
                print("PIN reset successful")
            except ValueError as e:
                print(e)

        elif choice == "4":
            break


if __name__ == "__main__":
    main()

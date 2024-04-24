from datetime import datetime
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

class Transaction:
    def __init__(self, amount, transaction_type, timestamp):
        self.amount = amount
        self.transaction_type = transaction_type
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_dict(cls, data):
        timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S")
        return cls(data['amount'], data['transaction_type'], timestamp)


class Account:
    def __init__(self, account_number, owner, balance=0):
        self.account_number = account_number
        self.owner = owner
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        self.balance += amount
        self.transactions.append(Transaction(amount, "deposit", datetime.now()))

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.transactions.append(Transaction(-amount, "withdrawal", datetime.now()))
        else:
            print("Insufficient funds.")

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions


class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}
        self.key = get_random_bytes(32)  # Generate encryption key

    def encrypt_data(self, data):
        serialized_data = json.dumps(data, default=lambda x: x.to_dict()).encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(self.pad(serialized_data))
        return b64encode(encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data):
        ciphertext = b64decode(encrypted_data)
        cipher = AES.new(self.key, AES.MODE_CBC)
        decrypted_data = cipher.decrypt(ciphertext)
        unpadded_data = self.unpad(decrypted_data)
        data = json.loads(unpadded_data.decode('utf-8'), object_hook=lambda x: Transaction.from_dict(x))
        return data

    def create_account(self, account_number, owner, initial_balance=0):
        if account_number not in self.accounts:
            self.accounts[account_number] = Account(account_number, owner, initial_balance)
        else:
            print("Account number already exists.")

    def get_account(self, account_number):
        if account_number in self.accounts:
            return self.accounts[account_number]
        else:
            print("Account not found.")

    def transfer(self, from_account_number, to_account_number, amount):
        from_account = self.get_account(from_account_number)
        to_account = self.get_account(to_account_number)

        if from_account and to_account:
            if from_account.balance >= amount:
                from_account.withdraw(amount)
                to_account.deposit(amount)
                print("Transfer successful.")
            else:
                print("Insufficient funds in the sender's account.")
        else:
            print("One or both accounts not found.")

    def pad(self, data):
        block_size = AES.block_size
        padding_length = block_size - len(data) % block_size
        padding = bytes([padding_length]) * padding_length
        return data + padding

    def unpad(self, data):
        padding_length = data[-1]
        return data[:-padding_length]

def display_menu():
    print("Welcome to the Banking System")
    print("1. Create Account")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transfer")
    print("5. Check Balance")
    print("6. Exit")

def create_account(bank):
    account_number = input("Enter account number: ")
    owner = input("Enter account owner: ")
    initial_balance = float(input("Enter initial balance: "))
    bank.create_account(account_number, owner, initial_balance)
    print("Account created successfully.")

def deposit(bank):
    account_number = input("Enter account number: ")
    amount = float(input("Enter amount to deposit: "))
    account = bank.get_account(account_number)
    if account:
        account.deposit(amount)
        print("Deposit successful. Current balance:", account.get_balance())

def withdraw(bank):
    account_number = input("Enter account number: ")
    amount = float(input("Enter amount to withdraw: "))
    account = bank.get_account(account_number)
    if account:
        account.withdraw(amount)
        print("Withdrawal successful. Current balance:", account.get_balance())

def transfer(bank):
    from_account_number = input("Enter sender's account number: ")
    to_account_number = input("Enter recipient's account number: ")
    amount = float(input("Enter amount to transfer: "))
    bank.transfer(from_account_number, to_account_number, amount)

def check_balance(bank):
    account_number = input("Enter account number: ")
    account = bank.get_account(account_number)
    if account:
        print("Account balance:", account.get_balance())

def main():
    my_bank = Bank("My Bank")
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            create_account(my_bank)
        elif choice == "2":
            deposit(my_bank)
        elif choice == "3":
            withdraw(my_bank)
        elif choice == "4":
            transfer(my_bank)
        elif choice == "5":
            check_balance(my_bank)
        elif choice == "6":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox, simpledialog

class ATM:
    def __init__(self, root):
        # Initialize user details
        self.user_pin = "1234"
        self.user_balance = 500.00

        # Configure the root window
        self.root = root
        self.root.title("ATM System")
        self.root.geometry("400x300")

        # Welcome label
        self.welcome_label = tk.Label(self.root, text="Welcome to the ATM", font=("Helvetica", 16))
        self.welcome_label.pack(pady=20)

        # PIN entry section
        self.pin_label = tk.Label(self.root, text="Enter PIN:", font=("Helvetica", 12))
        self.pin_label.pack(pady=5)

        self.pin_entry = tk.Entry(self.root, show="*", font=("Helvetica", 12), width=20, justify="center")
        self.pin_entry.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Submit", font=("Helvetica", 12), command=self.verify_pin)
        self.submit_button.pack(pady=10)

        # Menu frame (hidden initially)
        self.menu_frame = tk.Frame(self.root)

        self.balance_button = tk.Button(self.menu_frame, text="Check Balance", font=("Helvetica", 12), command=self.check_balance)
        self.balance_button.pack(pady=5)

        self.deposit_button = tk.Button(self.menu_frame, text="Deposit Money", font=("Helvetica", 12), command=self.deposit_money)
        self.deposit_button.pack(pady=5)

        self.withdraw_button = tk.Button(self.menu_frame, text="Withdraw Money", font=("Helvetica", 12), command=self.withdraw_money)
        self.withdraw_button.pack(pady=5)

        self.exit_button = tk.Button(self.menu_frame, text="Exit", font=("Helvetica", 12), command=self.exit_atm)
        self.exit_button.pack(pady=5)

    # Verify PIN
    def verify_pin(self):
        entered_pin = self.pin_entry.get()
        if entered_pin == self.user_pin:
            messagebox.showinfo("Access Granted", "PIN verified successfully!")
            self.show_menu()
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN. Please try again.")

    # Show menu
    def show_menu(self):
        self.welcome_label.config(text="Main Menu")
        self.pin_label.pack_forget()
        self.pin_entry.pack_forget()
        self.submit_button.pack_forget()
        self.menu_frame.pack(pady=10)

    # Check balance
    def check_balance(self):
        messagebox.showinfo("Balance", f"Your current balance is: ${self.user_balance:.2f}")

    # Deposit money
    def deposit_money(self):
        amount = self.prompt_user("Deposit Money", "Enter the amount to deposit:")
        if amount:
            try:
                amount = float(amount)
                if amount > 0:
                    self.user_balance += amount
                    messagebox.showinfo("Success", f"${amount:.2f} deposited successfully.")
                else:
                    messagebox.showerror("Error", "Deposit amount must be greater than $0.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a valid amount.")

    # Withdraw money
    def withdraw_money(self):
        amount = self.prompt_user("Withdraw Money", "Enter the amount to withdraw:")
        if amount:
            try:
                amount = float(amount)
                if amount > 0:
                    if amount <= self.user_balance:
                        self.user_balance -= amount
                        messagebox.showinfo("Success", f"${amount:.2f} withdrawn successfully.")
                    else:
                        messagebox.showerror("Error", "Insufficient balance.")
                else:
                    messagebox.showerror("Error", "Withdrawal amount must be greater than $0.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a valid amount.")

    # Prompt user for input
    def prompt_user(self, title, message):
        return simpledialog.askstring(title, message)

    # Exit the ATM
    def exit_atm(self):
        self.root.destroy()

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()

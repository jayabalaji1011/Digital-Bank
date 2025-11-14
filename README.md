# Banking Management System

A web-based banking system designed to manage customers, transactions, and bank balances efficiently. Built using Django and Python with a responsive frontend.

## Features

### Customer Management
- Add, update, and view customer information.
- Unique account numbers are generated automatically.
- Tracks customer balance in real-time.

### Transaction Management
- Supports **Deposit**, **Withdraw**, and **Transfer** operations.
- Transaction history for each customer.
- Transfers between customers are logged with sender and receiver details.
- Bank balance updates automatically with transactions.

### Security
- Passwords are hashed using Django's `make_password` method.
- Robust validation for transactions and account management.

### Staff Access
- Only staff can access customer details and perform transactions.
- Session-based staff authentication.


## Models

- **Bank**: Holds bank details like name, IFSC, branch, balance.
- **Customer**: Stores customer details, linked to a bank.
- **Transaction**: Records deposits, withdrawals, and transfers.
- **BankTransaction**: Logs bank-level transactions for tracking.

 
## Technologies Used

- **Backend:** Django, Python
- **Frontend:** HTML, CSS, Bootstrap, Javascript
- **Database:** SQLite (default for Django)




## Installation 1. **Clone the repository**
bash
git clone https://github.com/jayabalaji1011/Digital-Bank.git
cd Digital-Bank

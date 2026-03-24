# Inventory Manager

A CLI-based inventory and account management system built in Python.

## Features

| Command       | Description                                      |
|---------------|--------------------------------------------------|
| `balance`     | Add or subtract from the account balance         |
| `sale`        | Record a product sale (updates account + stock)  |
| `purchase`    | Record a product purchase (validates funds)       |
| `account`     | Display current account balance                  |
| `list`        | Display full warehouse inventory                 |
| `warehouse`   | Look up a specific product's status              |
| `review`      | Review operation history (supports index range)  |
| `end`         | Exit the program                                 |

## Usage

```bash
python inventory_manager.py
```

## Business Rules

- **Purchases** are rejected if the account balance would go negative.
- **Sales** are rejected if warehouse stock is insufficient.
- **Review** supports index-based range queries with out-of-range clamping.
- All operations are logged and reviewable via the `review` command.

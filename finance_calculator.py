import sys
import json
import logging
import os
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout, QMessageBox, QComboBox, QCalendarWidget, QStackedWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from functools import partial

logging.basicConfig(
    filename='ravuss_error_log.txt',  # Log will be saved in error_log.txt
    level=logging.ERROR,        # Only errors and above will be logged
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DATA_FILE = "finances.json"
CATEGORY_FILE = "categories.json"

class FinanceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Personal Finance Manager")
        self.setGeometry(300, 300, 800, 600)

        self.finances = {"income": 0, "expenses": 0, "events": []}
        self.categories = []

        self.strings = {
            "currency": "$",
            "statistics": "Statistics",
            "add_income_expenses": "Add income/expenses",
            "chronology": "Chronology",
            "category": "Category",
            "categories": "Categories",
            "type": "Type",
            "action": "Action",
            "add_category": "Add category",
            "add_category_name": "Add category name",
            "category_name": "Category name",
            "income": "Income",
            "incomes": "Incomes",
            "expense": "Expense",
            "expenses": "Expenses",
            "category_manager": "Category management",
            "add": "Add",
            "delete": "Delete",
            "total_balance": "Total balance",
            "enter_an_amount": "Enter an amount",
            "exit": "Exit",
            "date": "Date",
            "reason": "Reason",
            "amount": "Amount",
            "income_added": "Income added!",
            "please_enter_valid_amount": "Please enter a valid amount!",
            "expense_added": "Expense added!",
            "error": "Error",
            "success": "Success",
            "save_changes": "Save changes"
        }


        

        self.load_categories()
        self.load_data()
        self.reason_combo = QComboBox()

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()

        self.button_layout = QHBoxLayout()
        self.add_nav_buttons()

        self.stacked_widget = QStackedWidget(self)

        self.stat_screen = QWidget()
        self.create_stat_screen()

        self.input_screen = QWidget()
        self.create_input_screen()

        self.history_screen = QWidget()
        self.create_history_screen()

        self.categories_screen = QWidget()
        self.create_categories_screen()

        self.stacked_widget.addWidget(self.stat_screen)
        self.stacked_widget.addWidget(self.input_screen)
        self.stacked_widget.addWidget(self.history_screen)
        self.stacked_widget.addWidget(self.categories_screen) 

        layout.addLayout(self.button_layout)
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #f4f4f4;")

    def getString(self, key):
        return self.strings.get(key, f"Translation not found for {key}")

    def add_nav_buttons(self):
        stat_button = QPushButton(self.getString("statistics"))
        stat_button.setStyleSheet("font-size: 16px; padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;")
        stat_button.clicked.connect(self.show_stat_screen)
        
        input_button = QPushButton(self.getString("add_income_expenses"))
        input_button.setStyleSheet("font-size: 16px; padding: 10px 20px; background-color: #FF9800; color: white; border: none; border-radius: 5px;")
        input_button.clicked.connect(self.show_input_screen)

        history_button = QPushButton(self.getString("chronology"))
        history_button.setStyleSheet("font-size: 16px; padding: 10px 20px; background-color: #2196F3; color: white; border: none; border-radius: 5px;")
        history_button.clicked.connect(self.show_history_screen)

        categories_button = QPushButton(self.getString("categories"))
        categories_button.setStyleSheet("font-size: 16px; padding: 10px 20px; background-color: #9C27B0; color: white; border: none; border-radius: 5px;")
        categories_button.clicked.connect(self.show_categories_screen)

        self.button_layout.addWidget(stat_button)
        self.button_layout.addWidget(input_button)
        self.button_layout.addWidget(history_button)
        self.button_layout.addWidget(categories_button)

    def create_categories_screen(self):
        categories_layout = QVBoxLayout()

        title_label = QLabel(self.getString("category_manager"))
        title_label.setFont(QFont("Arial", 18))
        categories_layout.addWidget(title_label)

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels([(self.getString("category")), (self.getString("type")), (self.getString("action"))])
        self.categories_table.setEditTriggers(QTableWidget.NoEditTriggers) 

        self.categories_table.horizontalHeader().setStretchLastSection(True)

        categories_layout.addWidget(self.categories_table)

        add_button = QPushButton(self.getString("add_category"))
        add_button.clicked.connect(self.add_category)
        categories_layout.addWidget(add_button)

        # save_button = QPushButton(self.getString("save_changes"))
        # save_button.clicked.connect(self.save_category)
        # categories_layout.addWidget(save_button)

        self.categories_screen.setLayout(categories_layout)

    def add_category(self):
        category_dialog = QDialog(self)
        category_dialog.setWindowTitle(self.getString("add_category"))

        layout = QVBoxLayout()
        category_name_input = QLineEdit(category_dialog)
        category_name_input.setPlaceholderText(self.getString("add_category_name"))

        category_type_combo = QComboBox(category_dialog)
        category_type_combo.addItems([self.getString("income"), self.getString("expense")])

        add_button = QPushButton(self.getString("add"), category_dialog)
        add_button.clicked.connect(lambda: self.save_category(category_dialog, category_name_input, category_type_combo))

        layout.addWidget(QLabel(self.getString("category_name")+":"))
        layout.addWidget(category_name_input)
        layout.addWidget(QLabel(self.getString("type")+":"))
        layout.addWidget(category_type_combo)
        layout.addWidget(add_button)

        category_dialog.setLayout(layout)
        self.load_categories()
        category_dialog.exec_()

    def load_categories(self):

        try:
            if not os.path.exists("categories.json"):
                raise FileNotFoundError("categories.json file not found. Creating a new one.")
            
            with open("categories.json", "r", encoding="utf-8") as f:
                self.categories = json.load(f)
        except FileNotFoundError:
            logging.error("categories.json file not found. Creating a new one.")
            self.categories = []
            self.save_categories() 
        except json.JSONDecodeError as e:
            logging.error("Error loading JSON")
            self.categories = []  

    def load_categories_into_table(self):
        self.categories_table.setRowCount(0)

        # if not self.categories:
        #     self.show_error("No category data") 

        for row, category in enumerate(self.categories):
            name_item = QTableWidgetItem(category["name"])
            type_item = QTableWidgetItem(category["type"])

            self.categories_table.setItem(row, 0, name_item)
            self.categories_table.setItem(row, 1, type_item)

            delete_button = QPushButton(self.getString("delete"))
            delete_button.clicked.connect(partial(self.delete_category, row))
            self.update_categories_table()
            self.categories_table.setCellWidget(row, 2, delete_button)

    def update_categories_table(self):
        self.categories_table.setRowCount(0)

        for category in self.categories:
            row_position = self.categories_table.rowCount()
            self.categories_table.insertRow(row_position)

            self.categories_table.setItem(row_position, 0, QTableWidgetItem(category["name"]))
            self.categories_table.setItem(row_position, 1, QTableWidgetItem(category["type"]))

            delete_button = QPushButton(self.getString("delete"))
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_category(row))
            self.categories_table.setCellWidget(row_position, 2, delete_button)


    def save_categories(self):
        with open(CATEGORY_FILE, "w", encoding="utf-8") as file:
            json.dump(self.categories, file, ensure_ascii=False, indent=4)

    def delete_category(self, row):
        del self.categories[row]
        self.save_categories()
        self.load_categories_into_table()

    def save_category(self, category_dialog, category_name_input, category_type_combo):
        category_name = category_name_input.text()
        category_type = category_type_combo.currentText()

        self.categories.append({"name": category_name, "type": category_type})

        self.save_categories()

        self.update_categories_table()
        category_dialog.accept()

    def create_stat_screen(self):
        stat_layout = QVBoxLayout()

        self.income_label = QLabel(f"{self.getString('income')}: {self.finances['income']} {self.getString('currency')}")
        self.income_label.setFont(QFont("Arial", 14))
        stat_layout.addWidget(self.income_label)

        self.expenses_label = QLabel(f"{self.getString('expenses')}: {self.finances['expenses']} {self.getString('currency')}")
        self.expenses_label.setFont(QFont("Arial", 14))
        stat_layout.addWidget(self.expenses_label)

        self.balance_label = QLabel(f"{self.getString('total_balance')}: {self.finances['income'] - self.finances['expenses']} {self.getString('currency')}")
        self.balance_label.setFont(QFont("Arial", 14))
        stat_layout.addWidget(self.balance_label)

        self.canvas = FigureCanvas(plt.figure(figsize=(6, 4)))
        stat_layout.addWidget(self.canvas)
        self.plot_charts() 

        self.stat_screen.setLayout(stat_layout)

    def load_categories_adding(self):
        self.reason_combo.clear()
        try:
            with open('categories.json', 'r', encoding='utf-8') as file:
                categories = json.load(file)
                for category in categories:
                    self.reason_combo.addItem(category["name"])
        except FileNotFoundError:
            logging.error("Categories file not found.")
        except json.JSONDecodeError:
            logging.error("Error reading the categories file.")

    def create_input_screen(self):
        input_layout = QVBoxLayout()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(self.getString('enter_an_amount'))
        self.amount_input.setFont(QFont("Arial", 12))
        self.amount_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        input_layout.addWidget(self.amount_input)

        self.reason_combo.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        input_layout.addWidget(self.reason_combo)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
        QCalendarWidget QWidget{
            background-color:gray;
            color: white;
        }
        QCalendarWidget QToolButton{
            background-color:gray;
            color: white;
        }
        QCalendarWidget QAbstractItemView:enabled{
            background-color: white;
            color: black;
        }
        """)
        input_layout.addWidget(self.calendar)

        self.add_button = QPushButton(self.getString('add'))
        self.add_button.setStyleSheet("background-color: #388E3C; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        self.add_button.clicked.connect(self.add_income_or_expense)
        input_layout.addWidget(self.add_button)

        exit_button = QPushButton(self.getString('exit'))
        exit_button.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        exit_button.clicked.connect(self.close)
        input_layout.addWidget(exit_button)

        self.input_screen.setLayout(input_layout)

    def create_history_screen(self):
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([self.getString('date'), self.getString('reason'), self.getString('amount'), self.getString('delete')])

        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        history_layout.addWidget(self.history_table)
        
        self.history_screen.setLayout(history_layout)

    def show_stat_screen(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_input_screen(self):
        self.load_categories_adding()
        self.stacked_widget.setCurrentIndex(1)

    def show_history_screen(self):
        self.stacked_widget.setCurrentIndex(2)
        self.load_history()

    def show_categories_screen(self):
        self.stacked_widget.setCurrentIndex(3)
        self.load_categories_into_table()

    def add_income_or_expense(self):
        selected_category = self.reason_combo.currentText()
        
        amount = self.amount_input.text()
        
        if not amount:
            print("Please, enter amount.")
            return

        category_type = None
        for category in self.categories:
            if category['name'] == selected_category:
                category_type = category['type']
                break

        if category_type is None:
            print(f"Category {selected_category} not valid.")
            return

        if category_type == self.getString('income'):
            self.add_income()
            print(f"Added income: {selected_category}, {self.getString('amount')}: {amount}")
        elif category_type == self.getString('expense'):
            self.add_expenses()
            print(f"Expense added: {selected_category}, {self.getString('amount')}: {amount}")
        else:
            print(f"Invalid category: {category_type}")

    def add_income(self):
        try:
            amount = float(self.amount_input.text())
            reason = self.reason_combo.currentText()
            date = self.calendar.selectedDate().toString("dd.MM.yyyy")
            self.finances["income"] += amount
            self.finances["events"].append({"type": "income", "amount": amount, "reason": reason, "date": date})
            self.update_labels()
            self.amount_input.clear()
            self.save_data()
            self.show_success(self.getString('income_added'))
        
        except ValueError:
            self.show_error(self.getString('please_enter_valid_amount'))

    def add_expenses(self):
        try:
            amount = float(self.amount_input.text())
            reason = self.reason_combo.currentText()
            date = self.calendar.selectedDate().toString("dd.MM.yyyy")
            self.finances["expenses"] += amount
            self.finances["events"].append({"type": "expense", "amount": amount, "reason": reason, "date": date})
            self.update_labels()
            self.amount_input.clear()
            self.save_data()
            self.show_success(self.getString('expense_added'))
        
        except ValueError:
            self.show_error(self.getString('please_enter_valid_amount'))

    def load_history(self):
        self.history_table.setRowCount(len(self.finances["events"]))
        
        for row, event in enumerate(self.finances["events"]):
            date_item = QTableWidgetItem(event["date"])
            reason_item = QTableWidgetItem(event["reason"])

            amount_item = QLineEdit(f"{event['amount']} {self.getString('currency')}")
            amount_item.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
            amount_item.textChanged.connect(lambda text, idx=row: self.update_amount(text, idx))

            if event["type"] == "expense":
                amount_item.setStyleSheet("color: red; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
            elif event["type"] == "income":
                amount_item.setStyleSheet("color: #388E3C; padding: 5px; border: 1px solid #ccc; border-radius: 5px;")

            self.history_table.setItem(row, 0, date_item)
            self.history_table.setItem(row, 1, reason_item)
            self.history_table.setCellWidget(row, 2, amount_item)

            delete_button = QPushButton(self.getString('delete'))
            delete_button.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
            # delete_button.clicked.connect(partial(self.delete_event, idx=row))
            delete_button.clicked.connect(partial(self.delete_event, row))
            self.history_table.setCellWidget(row, 3, delete_button)

        self.update_labels()

    def delete_event(self, idx):
        del self.finances["events"][idx]
        self.load_history()
        self.save_data()


    def update_amount(self, text, idx):
        try:
            new_amount = float(text.replace(" {self.getString('currency')}", "").strip())

            self.finances["events"][idx]["amount"] = new_amount
            self.save_data()

            item = self.history_table.item(idx, 2)
            if item is None:
                item = QTableWidgetItem(f"{new_amount} {self.getString('currency')}")
                self.history_table.setItem(idx, 2, item)
            else:
                item.setText(f"{new_amount} {self.getString('currency')}")

            self.update_labels()

        except ValueError:
            pass

    def update_labels(self):
        income = sum(event['amount'] for event in self.finances["events"] if event['type'] == 'income')
        expenses = sum(event['amount'] for event in self.finances["events"] if event['type'] == 'expense')

        self.income_label.setText(f"{self.getString('income')}: {income} {self.getString('currency')}")
        self.expenses_label.setText(f"{self.getString('expenses')}: {expenses} {self.getString('currency')}")
        self.balance_label.setText(f"{self.getString('total_balance')}: {income - expenses} {self.getString('currency')}")

        self.finances["income"] = income
        self.finances["expenses"] = expenses

        self.plot_charts()

    def plot_charts(self):
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)

        income = sum(event['amount'] for event in self.finances["events"] if event['type'] == 'income')
        expenses = sum(event['amount'] for event in self.finances["events"] if event['type'] == 'expense')

        if income == 0 and expenses == 0:
            self.canvas.draw() 
            return

        labels = [self.getString('incomes'), self.getString('expenses')]
        values = [income, expenses]

        ax.pie(values, labels=labels, autopct="%1.1f%%", colors=["#4CAF50", "#F44336"], startangle=90)
        ax.axis("equal")
        self.canvas.draw()

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.finances, f)

    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                self.finances = json.load(f)
        except FileNotFoundError:
            self.finances = {"income": 0, "expenses": 0, "events": []}

    def show_error(self, message):
        QMessageBox.critical(self, self.getString('error'), message)

    def show_success(self, message):
        QMessageBox.information(self, self.getString('success'), message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec_())

import sys
import json
from platform import system

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QFileDialog
)
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and PyInstaller """
    if getattr(sys, 'frozen', False):  # Check if running as compiled .exe
        base_path = sys._MEIPASS  # Temporary directory used by PyInstaller
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class LethalData(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("LethalData v1.1")
        self.setGeometry(100, 100, 650, 500)
        self.setFixedSize(720, 550)  # Set fixed window size (width, height)

        # State tracking
        self.quota_number = 1  # Current quota number
        self.day_number = 1  # Current quota number
        self.quota_data = {}  # Dictionary to store input data for each quota

        # Set up the main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.set_dark_theme(self)
        self.setWindowIcon(QIcon(resource_path('icon.ico')))

        # Add the tabs
        self.add_tabs()

    def add_tabs(self):
        self.quotas_tab = self.create_quotas_tab()
        self.calc_tab = self.create_calc_tab()
        self.tabs.addTab(self.quotas_tab, "Quotas")
        self.tabs.addTab(self.calc_tab, "Calculator")

    def create_calc_tab(self):
        # Load the OTF font
        font_id = QFontDatabase.addApplicationFont(resource_path("3270-Regular.otf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Create the main widget for the tab
        calc_tab = QWidget()
        self.layout = QVBoxLayout()

        # Apply dark theme
        self.set_dark_theme(calc_tab)

        # Title
        self.calc_label = QLabel(f"Sell Calculator")
        self.calc_label.setFont(QFont(font_family, 50))
        self.calc_label.setAlignment(Qt.AlignLeft)
        self.calc_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Create grid layout for the table
        self.calc_inputs = {}
        self.grid = QGridLayout()

        calc_labels = ["Initial Terminal:", "Quota:", "Desired Terminal:", "Scrap to Sell:"]
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align grid to the top-left
        self.grid.setHorizontalSpacing(10)  # Add some spacing between columns
        self.grid.setVerticalSpacing(15)  # Add spacing between rows

        # Loop through day labels
        for i, day_label in enumerate(calc_labels, start=1):
            # Create a label
            label = QLabel(day_label)
            label.setFont(QFont(font_family, 17))
            label.setStyleSheet("color: rgb(253, 85, 0);")
            label.setFixedWidth(250)  # Set a fixed width to stop labels from expanding
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align label to the right

            # Create an input field
            input_field = QLineEdit()
            input_field.setFont(QFont(font_family, 12))
            input_field.setPlaceholderText("####")
            input_field.setFixedWidth(80)
            input_field.setStyleSheet("color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
            input_field.textChanged.connect(self.calculate_scrap)

            # Use a horizontal layout for each row
            row_layout = QHBoxLayout()
            row_layout.addWidget(label)  # Add label to the row
            row_layout.addWidget(input_field)  # Add input to the row
            row_layout.addStretch()  # Add a stretch to push everything to the left

            # Add the horizontal layout to the grid
            self.grid.addLayout(row_layout, i, 0)  # Add row to grid layout

            # Store the input field reference
            self.calc_inputs[day_label] = input_field

        # Total Ship Scrap Display
        self.overtime_label = QLabel("Overtime: No Overtime")
        self.overtime_label.setFont(QFont(font_family, 14))
        self.overtime_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Assemble layout
        self.layout.addWidget(self.calc_label)
        self.layout.addLayout(self.grid)
        self.layout.addWidget(self.overtime_label)  # Add total scrap label
        calc_tab.setLayout(self.layout)

        return calc_tab

    def create_quotas_tab(self):
        # Load the OTF font
        font_id = QFontDatabase.addApplicationFont(resource_path("3270-Regular.otf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Create the main widget for the tab
        tab = QWidget()
        self.layout = QVBoxLayout()

        # Apply dark theme
        self.set_dark_theme(tab)

        # Title
        self.title_label = QLabel(f"Quota {self.quota_number}")
        self.title_label.setFont(QFont(font_family, 60))
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Create grid layout for the table
        self.quota_inputs = {}
        self.quota_checkboxes = {}
        self.name_inputs = []  # Holds QLineEdit widgets for player names
        self.grid = QGridLayout()

        # Assuming 4 players, with 4 rows (including "Sold Scrap", but no players on that row)
        for j in range(4):  # Assuming 4 players
            name_input = QLineEdit()
            name_input.setFont(QFont(font_family, 12))
            name_input.setFixedWidth(90)
            name_input.setPlaceholderText(f"Player {j + 1} Name")
            name_input.setStyleSheet(
                "color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
            name_input.textChanged.connect(self.update_column_labels)  # Update column checkboxes when name changes
            self.name_inputs.append(name_input)
            self.grid.addWidget(name_input, 0, j + 4)  # Place in the first row, one for each column

        # Add rows for days and "Sold Scrap" (without player checkboxes)
        day_labels = ["Day 1", "Day 2", "Day 3", "Sell"]
        for i, day_label in enumerate(day_labels, start=1):  # Start from the second row
            # Day labels and input fields
            label = QLabel(day_label)
            label.setFont(QFont(font_family, 12))
            label.setStyleSheet("color: rgb(253, 85, 0);")
            label.setFixedWidth(45)
            input_field = QLineEdit()
            input_field.setFont(QFont(font_family, 12))
            input_field.setPlaceholderText("####")
            input_field.setFixedWidth(55)  # Adjust size of text boxes
            input_field.setContentsMargins(10, 0, 0, 0)
            input_field.textChanged.connect(self.update_sums)
            input_field.setStyleSheet(
                "color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
            if day_label != "Sell":
                slash = QLabel("/")
                slash.setFixedWidth(5)
                slash.setContentsMargins(0, 0, 0, 0)
                bottom_line = QLineEdit()
                bottom_line.setFont(QFont(font_family, 12))
                bottom_line.setPlaceholderText("####")
                bottom_line.setFixedWidth(65)  # Adjust size of text boxes
                bottom_line.setContentsMargins(0, 0, 20, 0)
                bottom_line.textChanged.connect(self.update_sums)
                bottom_line.setStyleSheet(
                    "color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
                self.grid.addWidget(slash, i, 2)
                self.grid.addWidget(bottom_line, i, 3)
            else:
                input_field.setContentsMargins(0, 0, 0, 0)
                input_field.setFixedWidth(55)
                input_field.setPlaceholderText("#####")
            self.grid.addWidget(label, i, 0)
            self.grid.addWidget(input_field, i, 1)
            self.quota_inputs[day_label] = input_field
            self.quota_inputs[day_label + "_BL"] = bottom_line

            # Add Notes column
            notes_input = QLineEdit()
            notes_input.setFont(QFont(font_family, 12))
            notes_input.setFixedWidth(100)  # Set width for the Notes column
            notes_input.setPlaceholderText("Add Notes")
            notes_input.setAlignment(Qt.AlignLeft)
            notes_input.setStyleSheet(
                "color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
            self.grid.addWidget(notes_input, i, 8)  # Place the notes input field in the new column
            self.quota_inputs[day_label + "_Note"] = notes_input

            # For "Sold Scrap", don't add player checkboxes
            if day_label != "Sell":
                # Add player death checkboxes for this day
                for j in range(4):  # Assuming 4 players
                    checkbox = QCheckBox(f"Player {j + 1} Death")
                    checkbox.setStyleSheet("""
                        QCheckBox {
                            color: rgb(253, 85, 0);
                            padding: 2px;
                            border: 2px solid transparent;
                            background-color: transparent;
                        }
                        QCheckBox::indicator {
                            width: 0px; /* Remove the actual checkbox indicator */
                            height: 0px;
                        }
                        QCheckBox:checked {
                            border: 2px solid rgb(253, 85, 0);
                            background-color: rgba(53, 25, 0, 0.2);
                        }
                    """)
                    checkbox.stateChanged.connect(self.update_sums)
                    self.quota_checkboxes[f"{day_label}_Player{j + 1}"] = checkbox
                    self.grid.addWidget(checkbox, i, j + 4)

        # Total Ship Scrap Display
        self.total_scrap_label = QLabel("Quota Profit: 0")
        self.total_scrap_label.setFont(QFont(font_family, 14))
        self.total_scrap_label.setStyleSheet("color: rgb(253, 85, 0);")

        self.avg_scrap_label = QLabel("Quota Average: 0")
        self.avg_scrap_label.setFont(QFont(font_family, 14))
        self.avg_scrap_label.setStyleSheet("color: rgb(253, 85, 0);")

        self.avg_label = QLabel("Overall Average: 0")
        self.avg_label.setFont(QFont(font_family, 14))
        self.avg_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Total Ship Scrap for all quotas
        self.total_all_quota_scrap_label = QLabel("Total Ship Scrap for All Quotas: 0")
        self.total_all_quota_scrap_label.setFont(QFont(font_family, 14))
        self.total_all_quota_scrap_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Profit Quota
        profit_quota_label = QLabel("Profit Quota:")
        profit_quota_label.setFont(QFont(font_family, 12))
        profit_quota_label.setStyleSheet("color: rgb(253, 85, 0);")

        self.profit_quota_input = QLineEdit()
        self.profit_quota_input.setFont(QFont(font_family, 12))
        self.profit_quota_input.setPlaceholderText("130")
        self.profit_quota_input.setFixedWidth(55)
        self.profit_quota_input.setText(f"{130:.0f}")
        self.profit_quota_input.setStyleSheet(
            "color: rgb(253, 85, 0); background-color: #000000; border: 1px solid rgb(253, 85, 0);")
        self.profit_quota_input.textChanged.connect(self.update_sums)  # Update sums on change

        self.roll_label = QLabel("Roll: 0.50")
        self.roll_label.setFont(QFont(font_family, 12))
        self.roll_label.setStyleSheet("color: rgb(253, 85, 0);")

        # Create a horizontal layout for the profit quota
        self.profit_quota_layout = QHBoxLayout()
        self.profit_quota_layout.setSpacing(10)  # Set the distance between elements (e.g., 10 pixels)
        self.profit_quota_layout.setContentsMargins(0, 10, 0, 0)  # Optional: Remove extra margins

        # Add the label and input to the layout
        self.profit_quota_layout.addWidget(profit_quota_label)
        self.profit_quota_layout.addWidget(self.profit_quota_input)

        # Add a stretch to push the items to the left (optional)
        self.profit_quota_layout.addStretch()

        # Navigation Buttons
        self.nav_buttons = QHBoxLayout()
        self.navigate_left = QPushButton("< Navigate")
        self.navigate_right = QPushButton("Navigate >")

        for button in [self.navigate_left, self.navigate_right]:
            button.setStyleSheet("""
            QPushButton {
                color: rgb(253, 85, 0);
                background-color: #111111;
                border: 1px solid rgb(253, 85, 0);
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
            QPushButton:pressed {
                background-color: #333233;
            }
        """)
            button.setFont(QFont(font_family, 15))
            button.setFixedWidth(120)

        self.nav_buttons.addWidget(self.navigate_left)
        self.nav_buttons.addWidget(self.navigate_right)

        # Connect buttons to their respective actions
        self.navigate_left.clicked.connect(self.navigate_left_action)
        self.navigate_right.clicked.connect(self.navigate_right_action)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Set a small spacing between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins

        # Save Button
        self.save_button = QPushButton("Save")
        self.save_button.setFont(QFont(font_family, 15))
        self.save_button.setFixedWidth(60)
        self.save_button.setStyleSheet("""
            QPushButton {
                color: rgb(253, 85, 0);
                background-color: #111111;
                border: 1px solid rgb(253, 85, 0);
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
            QPushButton:pressed {
                background-color: #333233;
            }
        """)
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_file)

        # Load Button
        self.load_button = QPushButton("Load")
        self.load_button.setFont(QFont(font_family, 15))
        self.load_button.setFixedWidth(60)
        self.load_button.setStyleSheet("""
            QPushButton {
                color: rgb(253, 85, 0);
                background-color: #111111;
                border: 1px solid rgb(253, 85, 0);
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
            QPushButton:pressed {
                background-color: #333233;
            }
        """)
        button_layout.addWidget(self.load_button)
        self.load_button.clicked.connect(self.load_quota_data_from_file)

        # Align buttons to the left
        button_layout.addStretch()  # Push everything to the left

        # Add the button layout to the main layout
        self.layout.addLayout(button_layout)

        # Assemble layout
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.profit_quota_layout)
        self.layout.addWidget(self.roll_label)
        self.layout.addLayout(self.grid)
        self.layout.addWidget(self.total_scrap_label)  # Add total scrap label
        self.layout.addWidget(self.avg_scrap_label)
        self.layout.addWidget(self.avg_label)
        self.layout.addWidget(self.total_all_quota_scrap_label)  # Add total scrap for all quotas label
        self.layout.addLayout(self.nav_buttons)
        tab.setLayout(self.layout)

        # Initialize sum
        self.sum_quota()
        self.sum_all_quotas()
        self.avg_quota()

        return tab

    def calculate_scrap(self):
        # Create the dictionary
        quota = {str(key): field.text() for key, field in self.calc_inputs.items()}

        # Extract the first, second, and third items safely
        items = list(quota.items())  # Convert to a list of tuples to access by index

        i_term = items[0][1]  # Value of the first key-value pair
        f_term = items[2][1]  # Value of the second key-value pair
        scrap = items[3][1]  # Value of the third key-value pair
        quota = items[1][1]

        try:
            if items[0][1] != "" and items[1][1] != "" and items[2][1] != "":
                WantedCredits = int(f_term) - int(i_term)
                Sell = (5 * WantedCredits + int(quota) + 75) / 6
                if (Sell - int(quota)) > 75:
                    self.calc_inputs["Scrap to Sell:"].setText(f"{Sell + 1:.0f}")
                    self.overtime_label.setText(f"Overtime: {(WantedCredits - Sell):.0f}")
                else:
                    if WantedCredits > int(quota):
                        self.overtime_label.setText("Overtime: No Overtime")
                        self.calc_inputs["Scrap to Sell:"].setText(f"{WantedCredits:.0f}")
                    else:
                        self.overtime_label.setText("Overtime: No Overtime")
                        self.calc_inputs["Scrap to Sell:"].setText(f"{int(quota):.0f}")
            else:
                self.calc_inputs["Scrap to Sell:"].setText("")
        except:
            self.calc_inputs["Initial Terminal:"].setText("")
            self.calc_inputs["Quota:"].setText("")
            self.calc_inputs["Desired Terminal:"].setText("")
            self.calc_inputs["Scrap to Sell:"].setText("")
            pass


    def save_quota_data(self):
        current_data = {str(key): field.text() for key, field in self.quota_inputs.items()}
        current_data.update({str(key): checkbox.isChecked() for key, checkbox in self.quota_checkboxes.items()})
        current_data['Profit Quota'] = self.profit_quota_input.text()  # Save Profit Quota
        # Save player names
        current_data['Player Names'] = [name_input.text() for name_input in self.name_inputs]
        self.quota_data[str(self.quota_number)] = current_data

    def save_file(self):
        self.save_quota_data()

        # Open a save file dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",  # Dialog title
            "",  # Default directory
            "LDS Files (*.lds);;All Files (*)",  # File type filters
            options=options
        )
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.quota_data, file, indent=4)

    def load_quota_data(self):
        try:
            # Check if the current quota has data
            if str(self.quota_number) in self.quota_data:
                data = self.quota_data[str(self.quota_number)]
                for key, field in self.quota_inputs.items():
                    field.setText(data.get(str(key), ""))
                for key, checkbox in self.quota_checkboxes.items():
                    checkbox.setChecked(data.get(str(key), False))
                self.profit_quota_input.setText(data.get('Profit Quota', ""))  # Load Profit Quota

                # Load player names or fallback to previous quota's names
                player_names = data.get('Player Names', [])
                for name_input, name in zip(self.name_inputs, player_names):
                    name_input.setText(name)
            else:
                # If no data for the current quota, clear inputs but keep names
                for field in self.quota_inputs.values():
                    field.clear()
                for checkbox in self.quota_checkboxes.values():
                    checkbox.setChecked(False)
                self.profit_quota_input.clear()

                # Carry over player names from the previous quota
                previous_quota = str(self.quota_number - 1)
                if previous_quota in self.quota_data:
                    player_names = self.quota_data[previous_quota].get('Player Names', [])
                    for name_input, name in zip(self.name_inputs, player_names):
                        name_input.setText(name)
        except Exception as e:
            pass

    def load_quota_data_from_file(self):
        # Open a file dialog to select a JSON file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Quota Data File", "",
                                                   "LDS Files (*.lds);;All Files (*)", options=options)

        if file_path:
            # Load the JSON data from the file
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                self.quota_data = data  # Assuming the file contains data for multiple quotas

                self.quota_data = data
                self.load_quota_data()

            except Exception as e:
                pass

    def update_column_labels(self):
        """Update the checkbox labels based on the name inputs."""
        for j, name_input in enumerate(self.name_inputs, start=1):  # Iterate over each player column
            name = name_input.text().strip()
            for key, checkbox in self.quota_checkboxes.items():
                if f"Player{j}" in key:  # Update only checkboxes for the current player
                    day_label = key.split('_')[0]  # Extract day label
                    checkbox.setText(f"{name} Death" if name else f"Player {j} Death")

    def set_dark_theme(self, widget):
        # Dark mode for the widget and its children
        widget.setStyleSheet("""
            background-color: #111111;
            color: rgb(253, 85, 0);
        """)

        # Apply dark theme for QTabWidget (the tab container)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #000000;
                border: none;
            }

            QTabBar::tab {
                background-color: #000000;
                color: rgb(253, 85, 0);
                padding: 5px;
            }

            QTabBar::tab:selected {
                background-color: #2a2a2a;
            }

            QTabBar::tab:hover {
                background-color: #2a2a2a;
            }
        """)

    def update_sums(self):
        self.sum_quota()
        self.sum_all_quotas()
        self.avg_quota()
        self.all_quota_average()
        self.calc_roll()


    def calc_roll(self):
        # Get the previous quota's profit quota value
        previous_quota = self.quota_number - 1
        previous_profit_quota = 130  # Default starting value for the first quota

        if str(previous_quota) in self.quota_data and 'Profit Quota' in self.quota_data[str(previous_quota)]:
            try:
                previous_profit_quota = int(self.quota_data[str(previous_quota)]['Profit Quota'])
            except ValueError:
                pass  # Fall back to default if the value is invalid


        try:
            if int(self.quota_number) != 1:
                Fufilled = self.quota_number -1
                current = int(self.profit_quota_input.text())
                TimeMultiplier = 1 + ((Fufilled ** 2) / 16)
                Diff = current - int(previous_profit_quota)
                Roll = ((Diff / 100) / TimeMultiplier) - 0.5
                self.roll_label.setText("Roll: " + f"{Roll:.2f}")
            else:
                self.roll_label.setText("Roll: 0.50")

        except:
            self.roll_label.setText("Roll: 0.50")



    def sum_quota(self):
        total_day = 0
        total_sold_scrap = 0
        for day_label, field in self.quota_inputs.items():
            try:
                value = float(field.text())
                if day_label == "Sell":
                    total_sold_scrap = value
                elif "_" not in day_label:
                    total_day += value
            except ValueError:
                pass
        total_ship_scrap = total_day - total_sold_scrap
        self.total_scrap_label.setText(f"Quota Profit: {total_ship_scrap:.0f}")

    def avg_quota(self):
        total_day = 0
        count = 0
        for day_label, field in self.quota_inputs.items():
            try:
                value = field.text()
                if value and day_label != "Sell" and "_" not in day_label:
                    total_day += int(value)
                    count += 1
            except ValueError:
                pass
        average = (total_day / count) if count > 0 else 0
        self.avg_scrap_label.setText(f"Quota Average: {average:.0f}")

    def all_quota_average(self):
        # Combine data from inputs and checkboxes
        current_data = {str(key): field.text() for key, field in self.quota_inputs.items()}
        current_data.update({str(key): checkbox.isChecked() for key, checkbox in self.quota_checkboxes.items()})
        all_data = {**self.quota_data, str(self.quota_number): current_data}

        total_day = 0
        count = 0
        i = "1"

        # Calculate the current maximum quota index
        for i in self.quota_data:
            i = str(int(i) + 1)
        if int(i) > 1:
            i = str(int(i) - 1)

        # Iterate through all quota data and calculate totals
        for quota in all_data.values():
            for key, value in quota.items():
                if "Player" in key or "_" in key:
                    continue  # Skip checkboxes and invalid fields
                if value:
                    try:
                        value = int(value)
                        if key != "Profit Quota" and key != "Sell":
                            total_day += value
                            count += 1
                    except ValueError:
                        pass

        # Calculate the average, avoiding division by zero
        average = (total_day / count) if count > 0 else 0
        self.avg_label.setText(f"Overall Average: {average:.0f}")

    def sum_all_quotas(self):
        current_data = {str(key): field.text() for key, field in self.quota_inputs.items()}
        current_data.update({str(key): checkbox.isChecked() for key, checkbox in self.quota_checkboxes.items()})
        all_data = {**self.quota_data, str(self.quota_number): current_data}

        total_all_scrap = 0
        for quota in all_data.values():
            total_day = 0
            total_sold_scrap = 0
            for key, value in quota.items():
                if "Player" in key or "_" in key:
                    continue  # Skip checkboxes in calculations
                try:
                    value = float(value)
                    if key == "Sell":
                        total_sold_scrap = value
                    elif key != "Profit Quota":
                        total_day += value
                except ValueError:
                    pass
            total_all_scrap += (total_day - total_sold_scrap)
        self.total_all_quota_scrap_label.setText(f"Total Ship Scrap for All Quotas: {total_all_scrap:.0f}")

    def calculate_quota(self):
        if str(self.quota_number) in self.quota_data and 'Profit Quota' in self.quota_data[str(self.quota_number)]:
            # Leave the data alone if a saved value exists
            return

        # Get the previous quota's profit quota value
        previous_quota = self.quota_number - 1
        previous_profit_quota = 130  # Default starting value for the first quota

        if str(previous_quota) in self.quota_data and 'Profit Quota' in self.quota_data[str(previous_quota)]:
            try:
                previous_profit_quota = float(self.quota_data[str(previous_quota)]['Profit Quota'])
            except ValueError:
                pass  # Fall back to default if the value is invalid

        Fufilled = int(self.title_label.text().split(" ")[1]) - 1
        TimeMultiplier = 1 + ((Fufilled ** 2) / 16)
        RandomizerOffset = 100 * TimeMultiplier
        new_profit_quota = previous_profit_quota + RandomizerOffset
        self.profit_quota_input.setText(f"{new_profit_quota:.0f}")
        # Save this calculated value for the current quota
        if str(self.quota_number) not in self.quota_data:
            self.quota_data[str(self.quota_number)] = {}
        self.quota_data[str(self.quota_number)]['Profit Quota'] = f"{new_profit_quota:.0f}"

    def update_quota_title(self):
        self.title_label.setText(f"Quota {self.quota_number}")

    def navigate_left_action(self):
        self.save_quota_data()
        if self.quota_number > 1:
            self.quota_number -= 1
            self.load_quota_data()
            self.update_quota_title()
            self.calculate_quota()  # Ensure profit quota is calculated
            self.sum_quota()
            self.sum_all_quotas()
            self.all_quota_average()

    def navigate_right_action(self):
        self.save_quota_data()
        self.quota_number += 1
        # Pre-fill names for a new quota
        if str(self.quota_number) not in self.quota_data:
            self.quota_data[str(self.quota_number)] = {}
            previous_quota = str(self.quota_number - 1)
            if previous_quota in self.quota_data:
                self.quota_data[str(self.quota_number)]['Player Names'] = self.quota_data[previous_quota].get(
                    'Player Names', [])
        self.load_quota_data()
        self.update_quota_title()
        self.calculate_quota()  # Ensure profit quota is calculated
        self.sum_quota()
        self.sum_all_quotas()
        self.all_quota_average()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LethalData()
    window.show()
    sys.exit(app.exec_())

import sys
import json
import os
import csv
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QTabWidget, QFileDialog
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QCalendarWidget, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QGroupBox, QGridLayout
import sqlite3

def create_connection(db_file):
    """Create a database connection or return an existing one."""
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except sqlite3.Error as e:
        print(e)
    return None

def create_calendar_table(connection):
    """Create the Calendar table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Calendar (
        Date TEXT PRIMARY KEY,
        Notes TEXT
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()
    except sqlite3.Error as e:
        print(e)

# Use these functions to create a connection and initialize the Calendar table
db_connection = create_connection("calendar.db")
if db_connection:
    create_calendar_table(db_connection)
    
def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install required dependencies.")
        sys.exit(1)

def check_dependencies():
    try:
        import PyQt5
        import reportlab
    except ImportError:
        return False
    return True

class ContractorLeadsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contractor Leads Database by REA")
        self.setGeometry(100, 100, 1600, 800)

        if not check_dependencies():
            install_dependencies()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Initialize the database connection
        db_connection = sqlite3.connect('leads_database.db')

        self.setup_ui(db_connection)  # Pass self.leads and db_connection
        
    def setup_ui(self, db_connection):
        self.tabs = TabWidget(self,  db_connection)  # Pass leads_list and db_connecti
        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap("logo.png")
        self.logo_pixmap = self.logo_pixmap.scaledToWidth(150, Qt.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)

        self.set_dark_theme()

    def set_dark_theme(self):
        app = QApplication.instance()
        app.setStyle("Fusion")

        # Dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, Qt.black)
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(dark_palette)

        # Set the font for all widgets to improve readability
        app_font = QFont("Arial", 10)
        app.setFont(app_font)

    def closeEvent(self, event):
        self.save_leads_data()
        event.accept()

class TabWidget(QWidget):
    def __init__(self, parent, db_connection):
        super().__init__()

        self.db_connection = db_connection

        self.tabs = QTabWidget(self)

        self.contractor_input_tab = ContractorInputTab(self, self.db_connection)
        self.leads_table_tab = LeadsTableTab(self.db_connection)
        self.calendar_tab = CalendarTab(self.db_connection)
        self.calls_tab = ComingSoonTab()
        self.email_tab = QTabWidget()
        self.email_gmail_tab = ComingSoonTab()
        self.email_smtp_tab = ComingSoonTab()
        self.messaging_tab = QTabWidget()
        self.messaging_twilio_tab = ComingSoonTab()
        self.forms_tab = QTabWidget()
        self.forms_my_forms_tab = ComingSoonTab()
        self.forms_create_tab = ComingSoonTab()
        self.forms_embed_tab = ComingSoonTab()
        self.forms_settings_tab = ComingSoonTab()
        self.integrations_tab = IntegrationsTab()
        self.integratoins_twilio_tab = TwilioIntegrationTab()
        self.settings_tab = ComingSoonTab()

        self.email_tab.addTab(self.email_gmail_tab, "Gmail")
        self.email_tab.addTab(self.email_smtp_tab, "SMTP")

        self.messaging_tab.addTab(self.messaging_twilio_tab, "Twilio")

        self.forms_tab.addTab(self.forms_my_forms_tab, "My Forms")
        self.forms_tab.addTab(self.forms_create_tab, "Create")
        self.forms_tab.addTab(self.forms_embed_tab, "Embed")
        self.forms_tab.addTab(self.forms_settings_tab, "Settings")

        self.tabs.addTab(self.contractor_input_tab, "Contractor Leads Input")
        self.tabs.addTab(self.leads_table_tab, "Leads Table View")
        self.tabs.addTab(self.calendar_tab, "Calendar")
        self.tabs.addTab(self.calls_tab, "Calls")
        self.tabs.addTab(self.email_tab, "Email")
        self.tabs.addTab(self.messaging_tab, "Messaging")
        self.tabs.addTab(self.forms_tab, "Forms")

        self.tabs.addTab(self.integrations_tab, "Integrations")


        self.tabs.addTab(self.settings_tab, "Settings")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

class ContractorInputTab(QWidget):
    def __init__(self, db_connection, parent):
        super().__init__()

        self.db_connection = db_connection
        self.parent = parent

        self.first_name_label = QLabel("First Name:")
        self.first_name_input = QLineEdit()

        self.last_name_label = QLabel("Last Name:")
        self.last_name_input = QLineEdit()

        self.address_line1_label = QLabel("Address Line 1:")
        self.address_line1_input = QLineEdit()

        self.address_line2_label = QLabel("Address Line 2:")
        self.address_line2_input = QLineEdit()

        self.city_label = QLabel("City:")
        self.city_input = QLineEdit()

        self.state_label = QLabel("State:")
        self.state_input = QLineEdit()

        self.zipcode_label = QLabel("Zipcode:")
        self.zipcode_input = QLineEdit()

        self.phone_label = QLabel("Phone Number:")
        self.phone_input = QLineEdit()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        self.notes_label = QLabel("Notes:")
        self.notes_input = QTextEdit()

        self.referred_by_label = QLabel("Referred By:")
        self.referred_by_input = QLineEdit()
        
        self.job_type_label = QLabel("Job Type:")
        self.job_type_dropdown = QComboBox()
        self.job_type_dropdown.addItems(["Residential", "Commercial", "Unknown"])
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_lead)  # Connect to the add_lead method

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.first_name_input)
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.last_name_input)
        layout.addWidget(self.address_line1_label)
        layout.addWidget(self.address_line1_input)
        layout.addWidget(self.address_line2_label)
        layout.addWidget(self.address_line2_input)
        layout.addWidget(self.city_label)
        layout.addWidget(self.city_input)
        layout.addWidget(self.state_label)
        layout.addWidget(self.state_input)
        layout.addWidget(self.zipcode_label)
        layout.addWidget(self.zipcode_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.notes_label)
        layout.addWidget(self.notes_input)
        layout.addWidget(self.referred_by_label)
        layout.addWidget(self.referred_by_input)
        layout.addWidget(self.job_type_label)
        layout.addWidget(self.job_type_dropdown)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        # Create the central widget and layout
        self.central_widget = QWidget(self)

        self.setup_ui()

        # Initialize and connect to the SQLite database
        self.connection = sqlite3.connect('leads_database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                phone TEXT,
                email TEXT,
                notes TEXT,
                referred_by TEXT,
                job_type TEXT,
                lead_status TEXT
            )
        ''')
        self.connection.commit()

    def add_lead(self):
        # Collect data from input fields
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        address_line1 = self.address_line1_input.text()
        address_line2 = self.address_line2_input.text()
        city = self.city_input.text()
        state = self.state_input.text()
        zipcode = self.zipcode_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        notes = self.notes_input.toPlainText()
        referred_by = self.referred_by_input.text()
        job_type = self.job_type_dropdown.currentText()

        # Insert data into the SQLite database
        self.cursor.execute('''
            INSERT INTO leads (first_name, last_name, address_line1, address_line2, city, state, zipcode, phone, email, notes, referred_by, job_type, lead_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, address_line1, address_line2, city, state, zipcode, phone, email, notes, referred_by, job_type, "In System"))
        self.connection.commit()

        # Clear input fields after adding the lead
        self.clear_input_fields()

        # Refresh the leads table in the parent TabWidget
        self.parent.leads_table_tab.populate_table()

    def clear_input_fields(self):
        # Clear all input fields
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.address_line1_input.clear()
        self.address_line2_input.clear()
        self.city_input.clear()
        self.state_input.clear()
        self.zipcode_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.notes_input.clear()
        self.referred_by_input.clear()
        self.job_type_dropdown.setCurrentIndex(0)

class CustomDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.editingFinished.connect(lambda: self.commitData.emit(editor))
        elif isinstance(editor, QComboBox):
            editor.currentIndexChanged.connect(lambda: self.commitData.emit(editor))
        return editor
        
class LeadsTableTab(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection  # Store the db_connection

        self.table = QTableWidget(self)
        self.table.setColumnCount(15)  # Adjusted to accommodate the new columns
        self.table.setHorizontalHeaderLabels(
            ["Lead Status", "First Name", "Last Name", "Address Line 1", "Address Line 2", "City", "State", "Zipcode",
             "Phone", "Email", "Notes", "Job Type", "Referred By", "Referred To", "Actions"])  # Adjusted headers
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


        # Apply custom delegate to handle editing of cell widgets
        delegate = CustomDelegate()
        self.table.setItemDelegate(delegate)
        
        # Create the refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.populate_table)

        # Create the export buttons
        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.export_pdf_button = QPushButton("Export to PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.export_txt_button = QPushButton("Export to TXT")
        self.export_txt_button.clicked.connect(self.export_to_txt)

        # Create the toggle edit mode button
        self.toggle_edit_button = QPushButton("Toggle Edit Mode")
        self.toggle_edit_button.clicked.connect(self.toggle_edit_mode)

        # Modify the button sizes here
        button_width = 120
        button_height = 30

        # Set fixed sizes for the buttons
        self.refresh_button.setFixedSize(button_width, button_height)
        self.export_csv_button.setFixedSize(button_width, button_height)
        self.export_pdf_button.setFixedSize(button_width, button_height)
        self.export_txt_button.setFixedSize(button_width, button_height)
        self.toggle_edit_button.setFixedSize(button_width, button_height)

        # Create a layout for the export buttons
        export_button_layout = QVBoxLayout()
        export_button_layout.addWidget(self.export_csv_button)
        export_button_layout.addWidget(self.export_pdf_button)
        export_button_layout.addWidget(self.export_txt_button)

        # Create a layout for the buttons and set alignment
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addLayout(export_button_layout)
        button_layout.addWidget(self.toggle_edit_button)
        button_layout.setAlignment(Qt.AlignCenter)  # Center-align the buttons vertically

        # Create the main layout for the tab
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)  # Add the button layout to the main layout

        self.setLayout(layout)

        self.populate_table()


    def toggle_edit_mode(self):
        self.edit_mode = not getattr(self, "edit_mode", False)
        
        for row in range(self.table.rowCount()):
            for col in range(1, self.table.columnCount() - 1):
                item = self.table.cellWidget(row, col)
                if isinstance(item, QLineEdit):
                    item.setReadOnly(not self.edit_mode)
        
        self.toggle_edit_button.setText("Editing Enabled" if self.edit_mode else "Editing Disabled")

    def createEditor(self, parent, option, index):
        if not self.edit_mode:
            QMessageBox.warning(self, "Editing Mode Off", "Editing must be enabled to edit cell data.")
            return None

        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.editingFinished.connect(lambda: self.commitData.emit(editor))
        elif isinstance(editor, QComboBox):
            editor.currentIndexChanged.connect(lambda: self.commitData.emit(editor))
        return editor

    def populate_table(self):
        # Create the mapping of status indices to status strings
        status_mapping = {
            0: "In System",
            1: "Good Lead",
            2: "Contact Later",
            3: "Bad Lead",
            4: "Passed Along",
            5: "Closed"
        }

        # Fetch leads data from the SQLite database using self.db_connection
        self.cursor = self.db_connection.cursor()
        self.cursor.execute("SELECT * FROM leads")
        leads_data = self.cursor.fetchall()

        for row, lead in enumerate(leads_data):
            # Status Combo Box
            status_combo = QComboBox()
            status_combo.addItems(status_mapping.values())
            current_status_index = lead[0]  # Replace 0 with the actual index of "Lead Status" field
            current_status = status_mapping.get(current_status_index, "Unknown Status")
            status_combo.setCurrentText(current_status)

            # First Name, Last Name
            first_name_input = QLineEdit(lead.get("First Name", ""))
            first_name_input.editingFinished.connect(lambda r=row, input_field=first_name_input: self.first_name_changed(r, input_field.text()))
            self.table.setCellWidget(row, 1, first_name_input)

            last_name_input = QLineEdit(lead.get("Last Name", ""))
            last_name_input.editingFinished.connect(lambda r=row, input_field=last_name_input: self.last_name_changed(r, input_field.text()))
            self.table.setCellWidget(row, 2, last_name_input)

            # Address Inputs
            address_line1_input = QLineEdit(lead.get("Address Line 1", ""))
            address_line1_input.editingFinished.connect(lambda r=row, input_field=address_line1_input: self.address_line1_changed(r, input_field.text()))
            self.table.setCellWidget(row, 3, address_line1_input)

            address_line2_input = QLineEdit(lead.get("Address Line 2", ""))
            address_line2_input.editingFinished.connect(lambda r=row, input_field=address_line2_input: self.address_line2_changed(r, input_field.text()))
            self.table.setCellWidget(row, 4, address_line2_input)

            city_input = QLineEdit(lead.get("City", ""))
            city_input.editingFinished.connect(lambda r=row, input_field=city_input: self.city_changed(r, input_field.text()))
            self.table.setCellWidget(row, 5, city_input)

            state_input = QLineEdit(lead.get("State", ""))
            state_input.editingFinished.connect(lambda r=row, input_field=state_input: self.state_changed(r, input_field.text()))
            self.table.setCellWidget(row, 6, state_input)

            zipcode_input = QLineEdit(lead.get("Zipcode", ""))
            zipcode_input.editingFinished.connect(lambda r=row, input_field=zipcode_input: self.zipcode_changed(r, input_field.text()))
            self.table.setCellWidget(row, 7, zipcode_input)

            phone_input = QLineEdit(lead["Phone"])
            phone_input.editingFinished.connect(lambda r=row, input_field=phone_input: self.input_field_changed(r, "Phone", input_field.text()))
            self.table.setCellWidget(row, 8, phone_input)

            email_input = QLineEdit(lead["Email"])
            email_input.editingFinished.connect(lambda r=row, input_field=email_input: self.input_field_changed(r, "Email", input_field.text()))
            self.table.setCellWidget(row, 9, email_input)
            
            # Notes
            notes_input = QLineEdit(lead["Notes"])
            self.table.setCellWidget(row, 10, notes_input)

            #Type, Referred to/by
            self.table.setItem(row, 11, QTableWidgetItem(lead["Job Type"]))
            self.table.setItem(row, 12, QTableWidgetItem(lead["Referred By"]))
            self.table.setItem(row, 13, QTableWidgetItem(lead.get("Referred To", "")))

            # Job Type Combo Box
            job_type_combo = QComboBox()
            job_type_combo.addItems(["Residential", "Commercial", "Other"])
            current_job_type = lead["other"]  # Replace <index_of_job_type_field> with the actual index of "Job Type" field
            job_type_combo.setCurrentText(current_job_type)
            job_type_combo.currentTextChanged.connect(lambda text, r=row: self.job_type_changed(r, text))
            self.table.setCellWidget(row, 11, job_type_combo)

            # Referred By, Referred To
            referred_by_input = QLineEdit(lead.get("Referred By", ""))
            referred_by_input.textChanged.connect(lambda text, r=row: self.referred_by_changed(r, text))
            self.table.setCellWidget(row, 12, referred_by_input)
            referred_to_input = QLineEdit(lead.get("Referred To", ""))
            referred_to_input.textChanged.connect(lambda text, r=row: self.referred_to_changed(r, text))
            self.table.setCellWidget(row, 13, referred_to_input)

            # Delete Button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, r=row: self.delete_lead(r))
            self.table.setCellWidget(row, 14, delete_button)

            # Connect input field changes to corresponding functions
            referred_by_input.textChanged.connect(lambda text, r=row: self.input_field_changed(r, "Referred By", text))
            referred_to_input.textChanged.connect(lambda text, r=row: self.input_field_changed(r, "Referred To", text))
                
    def input_field_changed(self, row, field_name, new_value):
        self.leads_list[row][field_name] = new_value

    def status_changed(self, row, text):
        self.leads_list[row]["Lead Status"] = text

    def first_name_changed(self, row, text):
        self.leads_list[row]["First Name"] = text

    def last_name_changed(self, row, text):
        self.leads_list[row]["Last Name"] = text
        
    def address_changed(self, row, text):
        self.leads_list[row]["Address"] = text
        
    def phone_changed(self, row, text):
        self.leads_list[row]["Phone"] = text
        
    def email_changed(self, row, text):
        self.leads_list[row]["Email"] = text
        
    def notes_changed(self, row, text):
        self.leads_list[row]["Notes"] = text
        
    def referred_by_changed(self, row, text):
        self.leads_list[row]["Referred By"] = text

    def referred_to_changed(self, row, text):
        self.leads_list[row]["Referred To"] = text
        
    def export_to_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Write the header
                writer.writerow(["Name", "Address", "Phone", "Email", "Notes", "Job Type"])
                # Write the data
                for lead in self.leads_list:
                    writer.writerow([lead["Name"], lead["Address"], lead["Phone"], lead["Email"], lead["Notes"], lead["Job Type"]])

    def export_to_pdf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Export to PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            doc = SimpleDocTemplate(file_name, pagesize=letter)
            elements = []
            data = [["Name", "Address", "Phone", "Email", "Notes", "Job Type"]]
            for lead in self.leads_list:
                data.append([lead["Name"], lead["Address"], lead["Phone"], lead["Email"], lead["Notes"], lead["Job Type"]])
            t = Table(data)
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            elements.append(t)
            doc.build(elements)

    def export_to_txt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Export to TXT", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "w") as file:
                for lead in self.leads_list:
                    file.write(f"Name: {lead['Name']}\n")
                    file.write(f"Address: {lead['Address']}\n")
                    file.write(f"Phone: {lead['Phone']}\n")
                    file.write(f"Email: {lead['Email']}\n")
                    file.write(f"Notes: {lead['Notes']}\n")
                    file.write(f"Job Type: {lead['Job Type']}\n")
                    file.write("\n")

    def delete_lead(self, row):
        confirmation = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this lead?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            del self.leads_list[row]
            self.populate_table()  # Refresh the table

    def job_type_changed(self, row, text):
        self.leads_list[row]["Job Type"] = text

class CalendarTab(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection

        self.tab_widget = QTabWidget(self)
        self.offline_calendar_tab = OfflineCalendarTab(self.db_connection)
        self.google_calendar_tab = GoogleCalendarTab()
        self.calendly_tab = CalendlyTab()
        
        self.tab_widget.addTab(self.offline_calendar_tab, "Offline Calendar")
        self.tab_widget.addTab(self.google_calendar_tab, "Google Calendar")
        self.tab_widget.addTab(self.calendly_tab, "Calendly")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

class OfflineCalendarTab(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection

        self.calendar = QCalendarWidget(self)
        self.calendar.selectionChanged.connect(self.populate_notes)

        self.notes_input = QTextEdit()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.populate_notes)

        self.save_button = QPushButton("Save Notes")
        self.save_button.clicked.connect(self.save_notes)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.notes_input)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.populate_notes()

    def populate_notes(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        notes = self.get_notes(selected_date)
        self.notes_input.setPlainText(notes)

    def get_notes(self, date):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT Notes FROM Calendar WHERE Date = ?", (date,))
            result = cursor.fetchone()
            return result[0] if result else ""
        except sqlite3.Error as e:
            print(e)
            return ""

    def save_notes(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        notes = self.notes_input.toPlainText()
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT OR REPLACE INTO Calendar (Date, Notes) VALUES (?, ?)", (selected_date, notes))
            self.db_connection.commit()
        except sqlite3.Error as e:
            print(e)

class GoogleCalendarTab(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Google Calendar - Coming Soon")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

class CalendlyTab(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Calendly - Coming Soon")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

class IntegrationsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = QTabWidget(self)

        self.twilio_integration_tab = TwilioIntegrationTab()
        self.google_integration_tab = GoogleIntegrationTab()  # Create a class for Google Integration
        self.zapier_integration_tab = ZapierIntegrationTab()  # Create a class for Zapier Integration

        self.tabs.addTab(self.twilio_integration_tab, "Twilio")
        self.tabs.addTab(self.google_integration_tab, "Google")
        self.tabs.addTab(self.zapier_integration_tab, "Zapier")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

class TwilioIntegrationTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create a group box for the Twilio integration section
        self.group_box = QGroupBox("Twilio Integration")
        
        self.twilio_sid_input = QLineEdit()
        self.twilio_auth_token_input = QLineEdit()
        self.load_twilio_credentials()

        self.save_button = QPushButton("Save Twilio Credentials")
        self.save_button.clicked.connect(self.save_twilio_credentials)

        # Create a grid layout for the group box
        layout = QGridLayout()
        layout.addWidget(QLabel("Twilio SID:"), 0, 0)
        layout.addWidget(self.twilio_sid_input, 0, 1)
        layout.addWidget(QLabel("Twilio Auth Token:"), 1, 0)
        layout.addWidget(self.twilio_auth_token_input, 1, 1)
        layout.addWidget(self.save_button, 2, 0, 1, 2, alignment=Qt.AlignCenter)
        
        self.group_box.setLayout(layout)
        
        # Create a layout for the whole tab
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def load_twilio_credentials(self):
        connection = create_connection("twilio_credentials.db")
        if connection:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TwilioCredentials (SID TEXT, AuthToken TEXT)")
            cursor.execute("SELECT * FROM TwilioCredentials LIMIT 1")
            result = cursor.fetchone()
            if result:
                self.twilio_sid_input.setText(result[0])
                self.twilio_auth_token_input.setText(result[1])
            connection.close()

    def save_twilio_credentials(self):
        twilio_sid = self.twilio_sid_input.text()
        twilio_auth_token = self.twilio_auth_token_input.text()
        self.save_credentials_to_database(twilio_sid, twilio_auth_token)

    def save_credentials_to_database(self, twilio_sid, twilio_auth_token):
        connection = create_connection("twilio_credentials.db")
        if connection:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TwilioCredentials (SID TEXT, AuthToken TEXT)")
            cursor.execute("DELETE FROM TwilioCredentials")
            cursor.execute("INSERT INTO TwilioCredentials (SID, AuthToken) VALUES (?, ?)", (twilio_sid, twilio_auth_token))
            connection.commit()
            connection.close()

class GoogleIntegrationTab(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Google Integration - Coming Soon")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

class ZapierIntegrationTab(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Zapier Integration - Coming Soon")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

class ComingSoonTab(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Coming Soon")
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_connection = sqlite3.connect('leads_database.db')
    window = ContractorLeadsApp()
    window.show()
    sys.exit(app.exec_())

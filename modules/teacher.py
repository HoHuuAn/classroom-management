from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCalendarWidget, QMessageBox, QTableWidgetItem, QHeaderView, QDialog, QErrorMessage, QLabel
from PyQt6 import uic, QtGui
from PyQt6.QtGui import QPixmap
import sqlite3
import uuid


class Teacher_Window(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/teacher.ui', self)

        # Set background image
        label = QLabel(self)
        pixmap = QPixmap("assets/window-background.jpg")
        label.setPixmap(pixmap)

        label_width = pixmap.width()
        label_height = pixmap.height()
        window_width = self.width()
        window_height = self.height()

        label.setGeometry(0, window_height - label_height, label_width, label_height)
        label.lower() 


        self.add_btn.clicked.connect(self.add)
        self.update_btn.clicked.connect(self.update)
        self.delete_btn.clicked.connect(self.delete)
        self.refresh_btn.clicked.connect(self.refresh_data)

        header = self.table_teacher.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.table_teacher.setColumnCount(3)
        self.table_teacher.setHorizontalHeaderLabels(
            ['Name', 'Description', 'ID'])
        self.table_teacher.setColumnHidden(2, True)

        self.refresh_data()

    def refresh_data(self):

        self.table_teacher.setStyleSheet("""
            QHeaderView::section {
                background-color: #1B3C2E;  
                color: white;              
                font-weight: bold;
                padding: 4px;
            }
        """)

        data = self.fetch_data()
        self.table_teacher.setRowCount(0)
        if data:
            for row_number, row_data in enumerate(data):
                self.table_teacher.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table_teacher.setItem(
                        row_number, column_number, QTableWidgetItem(str(data)))

        self.table_teacher.cellClicked.connect(self.cell_clicked)

    def fetch_data(self):
        conn = sqlite3.connect('classroom_management.db')
        cur = conn.cursor()
        cur.execute("SELECT name, description, id FROM teacher")
        data = cur.fetchall() or []
        conn.close()
        return data

    def cell_clicked(self, row, column):
        name_item = self.table_teacher.item(row, 0)
        description_item = self.table_teacher.item(row, 1)
        if name_item and description_item:
            name = name_item.text()
            description = description_item.text()

            self.name_teacher.setText(name)
            self.description_teacher.setText(description)

    def add(self):
        if self.name_teacher.text() == "":
            QMessageBox.critical(self, "Error", "Name is required")
        else:
            try:
                conn = sqlite3.connect('classroom_management.db')
                conn.cursor().execute("INSERT INTO teacher (id, name, description) VALUES (?, ?, ?)",
                                      (str(uuid.uuid4()),
                                       self.name_teacher.text(),
                                       self.description_teacher.text() or None))
                conn.commit()
                conn.close()

                self.name_teacher.clear()
                self.description_teacher.clear()

                QMessageBox.information(
                    self, "Success", "Teacher added successfully")

                self.refresh_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def update(self):
        selected_row = self.table_teacher.currentRow()
        selected_id = self.table_teacher.item(
            selected_row, 2).text()

        try:
            conn = sqlite3.connect('classroom_management.db')
            cur = conn.cursor()
            cur.execute("UPDATE teacher SET name=?, description=? WHERE id=?",
                        (self.name_teacher.text(), self.description_teacher.text(), selected_id))
            conn.commit()
            conn.close()

            self.name_teacher.clear()
            self.description_teacher.clear()

            QMessageBox.information(
                self, "Success", "Teacher updated successfully")

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def delete(self):
        selected_row = self.table_teacher.currentRow()
        selected_id = self.table_teacher.item(
            selected_row, 2).text()

        confirmation = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this booking?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('classroom_management.db')
                cur = conn.cursor()
                cur.execute("DELETE FROM teacher WHERE id=?", (selected_id,))
                conn.commit()
                conn.close()
                self.name_teacher.clear()
                self.description_teacher.clear()

                QMessageBox.information(
                    self, "Success", "Teacher deleted successfully")

                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

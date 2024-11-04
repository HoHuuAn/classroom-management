from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCalendarWidget, QMessageBox, QTableWidgetItem, QHeaderView, QDialog, QErrorMessage, QLabel
from PyQt6 import uic, QtGui
from PyQt6.QtGui import QPixmap
import sqlite3
import uuid


class Room_Window(QDialog):
    def __init__(self,):
        super().__init__()
        uic.loadUi('ui/room.ui', self)

        # Set background image
        label = QLabel(self)
        pixmap = QPixmap("assets/window-background.jpg")
        label.setPixmap(pixmap)

        label_width = pixmap.width()
        label_height = pixmap.height()
        window_width = self.width()
        window_height = self.height()

        label.setGeometry(0, window_height - label_height,
                          label_width, label_height)
        label.lower()

        # BUTTONS
        self.add_btn.clicked.connect(self.add)
        self.update_btn.clicked.connect(self.update)
        self.delete_btn.clicked.connect(self.delete)
        self.refresh_btn.clicked.connect(self.refresh_data)

        header = self.table_room.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table_room.setColumnCount(5)
        self.table_room.setHorizontalHeaderLabels(
            ['Name', 'Type', 'Floor', 'Status', 'ID'])
        self.table_room.setColumnHidden(4, True)

        self.refresh_data()

    def refresh_data(self):

        self.table_room.setStyleSheet("""
            QHeaderView::section {
                background-color: #1B3C2E;  
                color: white;              
                font-weight: bold;
                padding: 4px;
            }
        """)

        data = self.fetch_data()
        self.table_room.setRowCount(0)
        if data:
            for row_number, row_data in enumerate(data):
                self.table_room.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table_room.setItem(
                        row_number, column_number, QTableWidgetItem(str(data)))

        self.table_room.cellClicked.connect(self.cell_clicked)

    def fetch_data(self):
        conn = sqlite3.connect('classroom_management.db')
        cur = conn.cursor()
        cur.execute("SELECT name, type, floor, status, id FROM room")
        data = cur.fetchall() or []
        conn.close()
        return data

    def cell_clicked(self, row, column):
        name = self.table_room.item(row, 0).text()
        room_type = self.table_room.item(row, 1).text()
        floor = self.table_room.item(row, 2).text()
        status = self.table_room.item(row, 3).text()

        self.name_room.setText(name)

        self.type_room.setCurrentText(room_type)
        self.floor_room.setCurrentText(floor)
        self.status_room.setCurrentText(status)

    def add(self):
        conn = sqlite3.connect('classroom_management.db')
        error_msg = QErrorMessage(self)
        if self.name_room.text() == "" or self.type_room.currentText() == "" or self.floor_room.currentText() == "" or self.status_room.currentText() == "":
            QMessageBox.critical(
                self, "Error", "All fields are required")

        elif conn.cursor().execute("SELECT name FROM room where name=?", (self.name_room.text(),)).fetchone():
            QMessageBox.critical(
                self, "Error", "Room with this name already exists")
        else:
            try:
                conn.cursor().execute("INSERT INTO room (id, name, type, floor, status) VALUES (?, ?, ?, ?, ?)",
                                      (str(uuid.uuid4()),
                                       self.name_room.text(),
                                       self.type_room.currentText(),
                                       self.floor_room.currentText(),
                                       self.status_room.currentText()))
                conn.commit()
                conn.close()

                self.name_room.clear()
                self.type_room.setCurrentIndex(0)
                self.floor_room.setCurrentIndex(0)
                self.status_room.setCurrentIndex(0)

                QMessageBox.information(
                    self, "Success", "Room added successfully")

                self.refresh_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def update(self):
        selected_row = self.table_room.currentRow()
        selected_id = self.table_room.item(selected_row, 4).text()
        try:
            conn = sqlite3.connect('classroom_management.db')
            cur = conn.cursor()
            cur.execute("UPDATE room SET name=?, type=?, floor=?, status=? WHERE id=?",
                        (self.name_room.text(),
                         self.type_room.currentText(),
                         self.floor_room.currentText(),
                         self.status_room.currentText(),
                         selected_id))
            conn.commit()
            conn.close()

            self.name_room.clear()
            self.type_room.setCurrentIndex(0)
            self.floor_room.setCurrentIndex(0)
            self.status_room.setCurrentIndex(0)

            QMessageBox.information(
                self, "Success", "Room updated successfully")

            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def delete(self):
        selected_row = self.table_room.currentRow()
        selected_id = self.table_room.item(selected_row, 4).text()

        confirmation = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this room?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('classroom_management.db')
                cur = conn.cursor()
                cur.execute("DELETE FROM room WHERE id=?", (selected_id,))
                conn.commit()
                conn.close()

                self.name_room.clear()
                self.type_room.setCurrentIndex(0)
                self.floor_room.setCurrentIndex(0)
                self.status_room.setCurrentIndex(0)

                QMessageBox.information(
                    self, "Success", "Room deleted successfully")

                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

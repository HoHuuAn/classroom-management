from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QLabel
from PyQt6.QtCore import QTime, QDate, Qt
from PyQt6 import uic, QtGui
from PyQt6.QtGui import QPixmap
import sqlite3
import uuid
import database
from modules.room import Room_Window
from modules.teacher import Teacher_Window


class Booking_Window(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/booking.ui', self)

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

        # TEACHER
        self.teacher_window = Teacher_Window()
        self.teacher = self.teacher_window.fetch_data()
        self.teacher_booking.addItems([item[0] for item in self.teacher])

        # ROOM
        self.room_window = Room_Window()
        self.room = self.room_window.fetch_data()
        self.room_booking.addItems([item[0]
                                   for item in self.room if item[3] == 'OK'])

        # DATE
        self.date_booking.setDate(QDate.currentDate())
        self.date_booking.setCalendarPopup(True)

        # TIME
        self.time_start_booking.addItems(
            self.generate_time_options(QTime(6, 0)))
        self.time_end_booking.addItems(
            self.generate_time_options(QTime(6, 30)))
        self.time_start_booking.currentIndexChanged.connect(
            self.update_end_time_options)

        # BUTTONS
        self.add_btn.clicked.connect(self.add)
        self.update_btn.clicked.connect(self.update)
        self.delete_btn.clicked.connect(self.delete)
        self.refresh_btn.clicked.connect(self.refresh_data)

        # TABLE
        self.table_booking.setColumnCount(6)
        self.table_booking.setHorizontalHeaderLabels(
            ['Teacher', 'Room', 'Date', 'Start Time', 'End Time', 'ID']
        )

        header = self.table_booking.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        # Hide the ID column
        self.table_booking.setColumnHidden(5, True)

        # Refresh data and connect cellClicked event
        self.refresh_data()
        self.table_booking.cellClicked.connect(self.cell_clicked)

        # Variable to hold the currently selected booking ID
        self.current_booking_id = None

    def generate_time_options(self, start_time=QTime(6, 0)):
        times = []
        end_time = QTime(22, 30)
        current_time = start_time
        while current_time <= end_time:
            times.append(current_time.toString("HH:mm"))
            current_time = current_time.addSecs(30 * 60)
        return times

    def update_end_time_options(self):
        start_time_str = self.time_start_booking.currentText()
        start_time = QTime.fromString(start_time_str, "HH:mm")
        end_time_options = self.generate_time_options()
        self.time_end_booking.clear()
        for time_str in end_time_options:
            time = QTime.fromString(time_str, "HH:mm")
            if time > start_time:
                self.time_end_booking.addItem(time_str)

    def refresh_data(self):

        self.table_booking.setStyleSheet("""
            QHeaderView::section {
                background-color: #1B3C2E;  
                color: white;              
                font-weight: bold;
                padding: 4px;
            }
        """)

        data = self.fetch_data()
        self.table_booking.setRowCount(0)
        if data:
            for row_number, row_data in enumerate(data):
                self.table_booking.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table_booking.setItem(
                        row_number, column_number, QTableWidgetItem(str(data)))

        self.table_booking.cellClicked.connect(self.cell_clicked)

    def fetch_data(self):
        conn = sqlite3.connect('classroom_management.db')
        cur = conn.cursor()
        cur.execute(
            "SELECT teacher, room, date, start_time, end_time, id FROM booking")
        data = cur.fetchall() or []
        conn.close()
        return data

    def cell_clicked(self, row, column):
        self.current_booking_id = self.table_booking.item(
            row, 5).text()
        teacher = self.table_booking.item(row, 0).text()
        room = self.table_booking.item(row, 1).text()
        date = self.table_booking.item(row, 2).text()
        start_time = self.table_booking.item(row, 3).text()
        end_time = self.table_booking.item(row, 4).text()

        # Set form fields
        self.teacher_booking.setCurrentText(teacher)
        self.room_booking.setCurrentText(room)
        self.date_booking.setDate(QDate.fromString(date, "dd-MM-yyyy"))
        self.time_start_booking.setCurrentText(start_time)
        self.time_end_booking.setCurrentText(end_time)

    def add(self):
        teacher = self.teacher_booking.currentText()
        room = self.room_booking.currentText()
        date = self.date_booking.date().toString("dd-MM-yyyy")
        start_time = self.time_start_booking.currentText()
        end_time = self.time_end_booking.currentText()

        try:
            # Connect to the database
            conn = sqlite3.connect('classroom_management.db')
            cursor = conn.cursor()

            room_type = database.check_type_room(room) 

            # Check for overlapping bookings for the same room and date
            cursor.execute("""
                SELECT start_time, end_time FROM booking 
                WHERE room = ? AND date = ? AND (
                    (? > start_time AND ? < end_time) OR
                    (? > start_time AND ? < end_time) OR
                    (start_time >= ? AND start_time < ?) OR
                    (end_time > ? AND end_time <= ?)
                )
            """, (room, date, start_time, start_time, end_time, end_time, start_time, end_time, start_time, end_time))

            overlaps = cursor.fetchall()
            
            # Check based on room type
            if room_type == "Single" and overlaps:
                # Warn if any overlap is found for "Single" rooms
                QMessageBox.warning(
                    self, "Booking Conflict",
                    f"A booking for {room} on {date} conflicts with the selected time range {start_time} - {end_time}.\n"
                    f"Existing booking time: {overlaps[0][0]} - {overlaps[0][1]}"
                )
                conn.close()
                return  # Exit without adding the booking if there is a conflict

            elif room_type == "Double" and len(overlaps) >= 2:
                # Warn if more than two overlaps are found for "Double" rooms
                QMessageBox.warning(
                    self, "Booking Conflict",
                    f"Room {room} on {date} can only accommodate up to two overlapping bookings.\n"
                    f"Selected time range {start_time} - {end_time} conflicts with existing bookings."
                )
                conn.close()
                return  # Exit without adding the booking if there are already two overlaps

            # Insert the new booking if constraints are met
            cursor.execute(
                "INSERT INTO booking (id, teacher, room, date, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), teacher, room, date, start_time, end_time)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Booking Created", "The booking has been created successfully.")
            
            # Reset form selections
            self.teacher_booking.setCurrentIndex(0)
            self.room_booking.setCurrentIndex(0)
            self.time_start_booking.setCurrentIndex(0)
            self.time_end_booking.setCurrentIndex(0)

            # Refresh data to display the new booking
            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")


    def update(self):
        if not hasattr(self, 'current_booking_id'):
            QMessageBox.warning(self, "Update Error",
                                "Please select a booking to update.")
            return

        teacher = self.teacher_booking.currentText()
        room = self.room_booking.currentText()
        date = self.date_booking.date().toString("dd-MM-yyyy")
        start_time = self.time_start_booking.currentText()
        end_time = self.time_end_booking.currentText()

        try:
            conn = sqlite3.connect('classroom_management.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE booking SET teacher = ?, room = ?, date = ?, start_time = ?, end_time = ? WHERE id = ?",
                (teacher, room, date, start_time,
                 end_time, self.current_booking_id)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Booking Updated", "The booking has been updated successfully.")
            

            self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def delete(self):
        if not hasattr(self, 'current_booking_id'):
            QMessageBox.warning(self, "Delete Error",
                                "Please select a booking to delete.")
            return

        confirmation = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this booking?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('classroom_management.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM booking WHERE id = ?",
                               (self.current_booking_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(
                    self, "Booking Deleted", "The booking has been deleted successfully.")
                self.refresh_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

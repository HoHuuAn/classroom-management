import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCalendarWidget, QVBoxLayout, QDialog, QTableWidgetItem, QLabel, QSizePolicy
from PyQt6.QtCore import QTime, QDate, Qt
from PyQt6 import uic, QtGui
from PyQt6.QtGui import QColor, QBrush, QPixmap
import sys
from modules.teacher import Teacher_Window
from modules.room import Room_Window
from modules.booking import Booking_Window
import database


class ClassRoomManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main.ui', self)

        ### BACKGROUND IMAGE ###
        label = QLabel(self)
        label.setPixmap(QPixmap("assets/main-background.jpg"))
        # label.setScaledContents(True)
        label.setGeometry(self.rect())
        label.lower()

        self.show()

        database.Create_Databse()

        ### WINDOW OBJECTS ###
        self.room_window = Room_Window()
        self.teacher_window = Teacher_Window()
        self.booking_window = Booking_Window()

        self.calendar.selectionChanged.connect(self.get_selected_date)

        ### BUTTONS ###
        self.teacher_btn.clicked.connect(self.open_teacher_window)
        self.room_btn.clicked.connect(self.open_room_window)
        self.booking_btn.clicked.connect(self.open_booking_window)
        self.refresh_btn.clicked.connect(lambda: self.refresh_data(
            self.calendar.selectedDate().toString('dd-MM-yyyy')))

        self.refresh_data()

    def open_room_window(self):
        self.room_window.exec()

    def open_teacher_window(self):
        self.teacher_window.exec()

    def open_booking_window(self):
        self.booking_window.exec()

    def get_selected_date(self):
        date = self.calendar.selectedDate().toString('dd-MM-yyyy')
        self.refresh_data(date)

    def refresh_data(self, selected_date=QDate.currentDate().toString('dd-MM-yyyy')):
        room = self.room_window.fetch_data()
        self.time_table_dashboard.setShowGrid(False)

        self.time_table_dashboard.setStyleSheet("""
            QHeaderView::section {
                background-color: #1B3C2E;  
                color: white;              
                font-weight: bold;
                padding: 4px;
            }
        """)

        # Set Horizontal Headers
        first_elements = [item[0] for item in room if item[3] == 'OK']
        self.time_table_dashboard.setColumnCount(len(first_elements))
        self.time_table_dashboard.setHorizontalHeaderLabels(first_elements)

        # Set Vertical Headers for time slots
        self.time_table_dashboard.setRowCount(34)
        time = QTime(6, 0)
        time_labels = []
        for _ in range(self.time_table_dashboard.rowCount()):
            time_str = time.toString("hh:mm")
            time_labels.append(time_str)
            time = time.addSecs(1800)
            if time.hour() >= 23 and time.minute() >= 0:
                break
        self.time_table_dashboard.setVerticalHeaderLabels(time_labels)

        self.time_table_dashboard.clearContents()

        # Fetch bookings for the selected date
        if selected_date:
            bookings = database.fetch_data_booking_with_selected_date(selected_date)
            for booking in bookings:
                booking_id, teacher, room_id, date, start_time, end_time = booking

                start_row = time_labels.index(start_time)
                end_row = time_labels.index(end_time)

                try:
                    col = first_elements.index(room_id)
                except ValueError:
                    continue

                self.time_table_dashboard.setSpan(start_row, col, end_row - start_row, 1)

                # Set the teacher name and time
                item = QTableWidgetItem(f"{teacher}\n{start_time} - {end_time}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.time_table_dashboard.setItem(start_row, col, item)

                # Color the cells
                random_color = QColor(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
                item.setBackground(QBrush(random_color))

                # Automatically resize column and row to fit the content
                self.time_table_dashboard.resizeRowToContents(start_row)
    # def refresh_data(self, selected_date=QDate.currentDate().toString('dd-MM-yyyy')):
    #     room = self.room_window.fetch_data()
    #     self.time_table_dashboard.setShowGrid(False)

    #     self.time_table_dashboard.setStyleSheet("""
    #         QHeaderView::section {
    #             background-color: #1B3C2E;  
    #             color: white;              
    #             font-weight: bold;
    #             padding: 4px;
    #         }
    #     """)

    #     # Set Horizontal Headers
    #     first_elements = [item[0] for item in room if item[3] == 'OK']
    #     self.time_table_dashboard.setColumnCount(len(first_elements))
    #     self.time_table_dashboard.setHorizontalHeaderLabels(first_elements)

    #     # Set Vertical Headers for time slots
    #     self.time_table_dashboard.setRowCount(34)
    #     time = QTime(6, 0)
    #     time_labels = []
    #     for _ in range(self.time_table_dashboard.rowCount()):
    #         time_str = time.toString("hh:mm")
    #         time_labels.append(time_str)
    #         time = time.addSecs(1800)
    #         if time.hour() >= 23 and time.minute() >= 0:
    #             break
    #     self.time_table_dashboard.setVerticalHeaderLabels(time_labels)

    #     self.time_table_dashboard.clearContents()

    #     # Fetch bookings for the selected date
    #     if selected_date:
    #         bookings = database.fetch_data_booking_with_selected_date(selected_date)
    #         booking_slots = {room_id: [] for room_id in first_elements}

    #         for booking in bookings:
    #             booking_id, teacher, room_id, date, start_time, end_time = booking
    #             start_row = time_labels.index(start_time)
    #             end_row = time_labels.index(end_time)

    #             # Check if the room is in the header list
    #             try:
    #                 col = first_elements.index(room_id)
    #             except ValueError:
    #                 continue

    #             # Check if the room type is "Double"
    #             room_type = database.check_type_room(room_id)

    #             if room_type == "Double":
    #                 booking_slots[room_id].append((start_row, end_row, teacher, start_time, end_time))
    #             else:
    #                 # Single rooms are displayed as one block
    #                 self.time_table_dashboard.setSpan(start_row, col, end_row - start_row, 1)
    #                 item = QTableWidgetItem(f"{teacher}\n{start_time} - {end_time}")
    #                 item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                 random_color = QColor(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
    #                 item.setBackground(QBrush(random_color))
    #                 self.time_table_dashboard.setItem(start_row, col, item)
    #                 self.time_table_dashboard.resizeRowToContents(start_row)

    #         # Handle overlapping bookings for "Double" rooms
    #         for room_id, bookings in booking_slots.items():
    #             if len(bookings) > 1:
    #                 bookings.sort(key=lambda x: x[0])  # Sort bookings by start_row for easier placement
    #                 col = first_elements.index(room_id)
    #                 for i, (start_row, end_row, teacher, start_time, end_time) in enumerate(bookings[:2]):
    #                     span_rows = end_row - start_row
    #                     item = QTableWidgetItem(f"{teacher}\n{start_time} - {end_time}")
    #                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                     random_color = QColor(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
    #                     item.setBackground(QBrush(random_color))
                        
    #                     # Place items side-by-side within the same time range column
    #                     self.time_table_dashboard.setItem(start_row, col + i, item)
    #                     self.time_table_dashboard.setSpan(start_row, col + i, span_rows, 1)
    #                     self.time_table_dashboard.resizeRowToContents(start_row)
    #             else:
    #                 # Single booking in a "Double" room
    #                 for start_row, end_row, teacher, start_time, end_time in bookings:
    #                     item = QTableWidgetItem(f"{teacher}\n{start_time} - {end_time}")
    #                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                     random_color = QColor(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
    #                     item.setBackground(QBrush(random_color))
    #                     self.time_table_dashboard.setItem(start_row, col, item)
    #                     self.time_table_dashboard.setSpan(start_row, col, end_row - start_row, 1)
    #                     self.time_table_dashboard.resizeRowToContents(start_row)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
    obj = ClassRoomManagementSystem()
    app.exec()

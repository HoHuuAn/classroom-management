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

        # Connect finished signals to refresh_data
        self.room_window.finished.connect(lambda: self.refresh_data())
        self.teacher_window.finished.connect(lambda: self.refresh_data())
        self.booking_window.finished.connect(lambda: self.refresh_data())

        ### BUTTONS ###
        self.teacher_btn.clicked.connect(self.open_teacher_window)
        self.room_btn.clicked.connect(self.open_room_window)
        self.booking_btn.clicked.connect(self.open_booking_window)
        self.refresh_btn.clicked.connect(lambda: self.refresh_data(
            self.calendar.selectedDate().toString('dd-MM-yyyy')))
        
        ### CALENDAR ###
        self.calendar.selectionChanged.connect(self.get_selected_date)
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled
            {
                selection-background-color: #1B3C2E; 
                selection-color: white;
                color: #1B3C2E;
            }
        """)

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
            QHeaderView::vertical::section {
                background-color: #1B3C2E;
            }
            QHeaderView::section {
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)

        # Set Horizontal Headers
        double_rooms = [item[0] for item in room if item[1] ==
                        'Double' and item[3] == 'OK']
        single_rooms = [item[0] for item in room if item[1] ==
                        'Single' and item[3] == 'OK']
        room_columns = sum([[f"{room}_1", f"{room}_2"]
                           for room in double_rooms], []) + single_rooms

        # Update column count and headers
        self.time_table_dashboard.setColumnCount(len(room_columns))
        self.time_table_dashboard.setHorizontalHeaderLabels(room_columns)

        # Customize header background color for double rooms
        header = self.time_table_dashboard.horizontalHeader()
        for col, room_name in enumerate(room_columns):
            header_item = self.time_table_dashboard.horizontalHeaderItem(col)
            if any(room_name.startswith(double_room) for double_room in double_rooms):
                header_item.setBackground(QBrush(QColor("red")))
            else:
                header_item.setBackground(QBrush(QColor("#1B3C2E")))

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

        # Clear the table
        self.time_table_dashboard.clearContents()
        self.time_table_dashboard.clearSpans()

        # Fetch bookings for the selected date
        if selected_date:
            bookings = database.fetch_data_booking_with_selected_date(
                selected_date)
            for booking in bookings:
                booking_id, teacher, room_id, date, start_time, end_time = booking

                start_row = time_labels.index(start_time)
                end_row = time_labels.index(end_time)

                # Determine the column index, accounting for room type
                if room_id in double_rooms:
                    # Check if the first sub-column is available
                    col_base = room_columns.index(f"{room_id}_1")
                    if not self.time_table_dashboard.item(start_row, col_base):
                        col = col_base
                    else:
                        col = room_columns.index(f"{room_id}_2")
                else:
                    try:
                        col = room_columns.index(room_id)
                    except Exception as e:
                        print(e)
                        continue

                self.time_table_dashboard.setSpan(
                    start_row, col, end_row - start_row, 1)

                # Set the teacher name and time
                item = QTableWidgetItem(
                    f"{teacher}\n{start_time} - {end_time}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.time_table_dashboard.setItem(start_row, col, item)

                # Color the cells
                random_color = QColor(random.randint(150, 255), random.randint(
                    150, 255), random.randint(150, 255))
                item.setBackground(QBrush(random_color))

                # Automatically resize column and row to fit the content
                self.time_table_dashboard.resizeRowToContents(start_row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
    obj = ClassRoomManagementSystem()
    app.exec()

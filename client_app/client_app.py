import sys
import os
import threading
import requests
import socketio

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QStackedWidget,
    QComboBox,
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QDateTime,
    QTime,
    pyqtSignal
)

from PyQt5.QtGui import (
    QColor,
    QPixmap
)


# ============================================================
# SERVER CONFIGURATION
# ============================================================

SERVER_URL = os.environ.get(
    "LAB_SERVER_URL",
    "https://ksrce-lab-attendance.onrender.com"
)
sio = socketio.Client(reconnection=True)
# ============================================================
# CUSTOM LINE EDIT
# ============================================================

class CustomLineEdit(QLineEdit):

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder

        self.setPlaceholderText(
            self.placeholder_text
        )

    def focusInEvent(self, event):

        self.setPlaceholderText("")

        super().focusInEvent(event)

    def focusOutEvent(self, event):

        if not self.text():

            self.setPlaceholderText(
                self.placeholder_text
            )

        super().focusOutEvent(event)


# ============================================================
# MAIN APPLICATION
# ============================================================

class LabApp(QWidget):

    admin_exit_signal = pyqtSignal()

    def __init__(self):

        super().__init__()

        # Session variables
        self.session_id = None

        self.user_role = "STUDENT"

        self.elapsed_seconds = 0

        self.entry_time_str = ""

        self.entry_datetime = None

        self.session_started = False

        self.exit_completed = False

        self.admin_exit_signal.connect(
            self.handle_admin_force_exit
        )

        self.initUI()


    # ========================================================
    # WINDOW CLOSE PROTECTION
    # ========================================================

    def show_message(
        self,
        title,
        message,
        icon=QMessageBox.Information
    ):

        box = QMessageBox(self)

        box.setWindowTitle(
            title
        )

        box.setText(
            message
        )

        box.setIcon(
            icon
        )

        box.setStandardButtons(
            QMessageBox.Ok
        )

        box.setStyleSheet(
            """
            QMessageBox {
                background-color: #ffffff;
                color: #111111;
            }

            QMessageBox QLabel {
                color: #111111;
                background-color: #ffffff;
                font-family: "Segoe UI";
                font-size: 14px;
                font-weight: 600;
                padding: 10px;
            }

            QMessageBox QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 7px 22px;
                min-width: 70px;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: bold;
            }

            QMessageBox QPushButton:hover {
                background-color: #005a9e;
            }
            """
        )

        return box.exec()


    def closeEvent(self, event):

        # If active session is running,
        # prevent closing with X button
        if self.session_started and not self.exit_completed:

            self.show_message(
                "Active Lab Session",
                "Your lab session is still active.\n\n"
                "Please use the EXIT SESSION button "
                "to complete your attendance.",
                QMessageBox.Warning
            )

            event.ignore()

        else:

            event.accept()


    # ========================================================
    # INITIAL UI
    # ========================================================

    def initUI(self):

        # Normal Windows title bar
        # Allows Minimize / Maximize / X
        self.setWindowTitle(
            "K.S.R. College of Engineering - Lab Attendance"
        )

        self.resize(1100, 1100)

        self.setMinimumSize(
            1000,
            900
        )

        # Keep application above other windows
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )

        self.setStyleSheet(
            """
            QWidget {
                background-color: #030a16;
            }

            QMessageBox {
                background-color: #071426;
            }

            QMessageBox QLabel {
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 15px;
                font-weight: bold;
            }

            QMessageBox QPushButton {
                background-color: #00a2ff;
                color: #ffffff;
                border: 1px solid #00d9ff;
                border-radius: 5px;
                padding: 8px 25px;
                min-width: 70px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-weight: bold;
            }

            QMessageBox QPushButton:hover {
                background-color: #007acc;
            }

            QMessageBox QPushButton:pressed {
                background-color: #005f99;
            }
            """
        )


        # ====================================================
        # MAIN OUTER LAYOUT
        # ====================================================

        outer_layout = QVBoxLayout()

        outer_layout.setAlignment(
            Qt.AlignCenter
        )

        outer_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )


        # ====================================================
        # OUTER BORDER
        # ====================================================

        self.outer_border_frame = QFrame()

        self.outer_border_frame.setObjectName(
            "OuterFrame"
        )

        self.outer_border_frame.setMinimumWidth(
            900
        )

        self.outer_border_frame.setMaximumWidth(
            1100
        )

        self.outer_border_frame.setStyleSheet(
            """
            QFrame#OuterFrame {

                background-color: #050d1d;

                border: 3px solid #00f0ff;

                border-radius: 18px;

                padding: 12px;
            }
            """
        )


        # ====================================================
        # GLOW EFFECT
        # ====================================================

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(
            35
        )

        shadow.setColor(
            QColor(
                0,
                240,
                255,
                180
            )
        )

        shadow.setOffset(
            0,
            0
        )

        self.outer_border_frame.setGraphicsEffect(
            shadow
        )


        # ====================================================
        # INNER CARD
        # ====================================================

        self.card = QFrame()

        self.card.setStyleSheet(
            """
            QFrame {

                background-color: #061327;

                border: 2px solid #00a2ff;

                border-radius: 12px;

                padding: 20px 30px;
            }

            QLabel {

                color: #ffffff;

                font-family:
                    'Consolas',
                    'Courier New',
                    monospace;

                font-weight: bold;

                font-size: 16px;
            }

            QLineEdit,
            QComboBox {

                background-color: #ffffff;

                color: #000000;

                border: 1.5px solid #00d2ff;

                border-radius: 6px;

                padding: 10px 14px;

                font-family:
                    'Consolas',
                    'Courier New',
                    monospace;

                font-weight: bold;

                font-size: 16px;

                min-height: 20px;
            }

            QLineEdit:hover,
            QComboBox:hover {

                border: 2px solid #00ffff;

                background-color: #f0f9ff;
            }

            QLineEdit:focus,
            QComboBox:focus {

                border: 2.5px solid #0052d4;

                background-color: #ffffff;
            }

            QComboBox QAbstractItemView {

                background-color: #ffffff;

                color: #000000;

                selection-background-color: #00d2ff;

                selection-color: #000000;

                font-size: 16px;
            }

            QLineEdit::placeholder {

                color: #555555;
            }

            QComboBox:disabled {

                background-color: #dddddd;

                color: #555555;
            }
            """
        )


        # ====================================================
        # CARD LAYOUT
        # ====================================================

        card_layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()


        # ====================================================
        # ENTRY PAGE
        # ====================================================

        self.entry_page = QWidget()

        self.init_entry_page()

        self.stacked_widget.addWidget(
            self.entry_page
        )


        # ====================================================
        # ACTIVE PAGE
        # ====================================================

        self.active_page = QWidget()

        self.init_active_page()

        self.stacked_widget.addWidget(
            self.active_page
        )


        # ====================================================
        # EXIT PAGE
        # ====================================================

        self.exit_page = QWidget()

        self.init_exit_page()

        self.stacked_widget.addWidget(
            self.exit_page
        )


        card_layout.addWidget(
            self.stacked_widget
        )

        self.card.setLayout(
            card_layout
        )


        # ====================================================
        # OUTER LAYOUT
        # ====================================================

        border_inner_layout = QVBoxLayout()

        border_inner_layout.addWidget(
            self.card
        )

        self.outer_border_frame.setLayout(
            border_inner_layout
        )

        outer_layout.addWidget(
            self.outer_border_frame
        )

        self.setLayout(
            outer_layout
        )


        # ====================================================
        # SESSION TIMER
        # ====================================================

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_timer
        )


    # ========================================================
    # ENTRY PAGE
    # ========================================================

    def init_entry_page(self):

        layout = QVBoxLayout()


        # ====================================================
        # LOGO
        # ====================================================

        logo_label = QLabel()

        logo_label.setAlignment(
            Qt.AlignCenter
        )

        logo_label.setStyleSheet(
            """
            border: none;
            margin-bottom: 5px;
            """
        )


        script_dir = getattr(
            sys,
            "_MEIPASS",
            os.path.dirname(os.path.abspath(__file__))
        )

        logo_path = os.path.join(
            script_dir,
            "logo.png"
        )

        pixmap = QPixmap(
            logo_path
        )


        if not pixmap.isNull():

            logo_label.setPixmap(
                pixmap.scaled(
                    130,
                    130,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        else:

            logo_label.setText(
                "[ LOGO NOT FOUND - PLACE logo.png IN FOLDER ]"
            )

            logo_label.setStyleSheet(
                """
                color: #ff3366;
                font-weight: bold;
                border: none;
                margin-bottom: 10px;
                """
            )


        layout.addWidget(
            logo_label
        )


        # ====================================================
        # COLLEGE TITLE
        # ====================================================

        title1 = QLabel(
            "K.S.R. COLLEGE OF ENGINEERING "
            "(Autonomous) - TIRUCHENGODE"
        )

        title1.setAlignment(
            Qt.AlignCenter
        )

        title1.setStyleSheet(
            """
            font-size: 19px;
            color: #ffffff;
            font-weight: bold;
            border: none;
            margin-bottom: 2px;
            """
        )

        layout.addWidget(
            title1
        )


        # ====================================================
        # PAGE TITLE
        # ====================================================

        title2 = QLabel(
            "STUDENT LAB ENTRY PAGE"
        )

        title2.setAlignment(
            Qt.AlignCenter
        )

        title2.setStyleSheet(
            """
            font-size: 22px;
            color: #ffffff;
            font-weight: bold;
            border: none;
            margin-bottom: 15px;
            """
        )

        layout.addWidget(
            title2
        )


        # ====================================================
        # FORM
        # ====================================================

        form_layout = QVBoxLayout()

        form_layout.setSpacing(
            10
        )


        # ====================================================
        # SYSTEM NUMBER
        # ====================================================

        self.input_sys = QLineEdit()

        self.input_sys.setPlaceholderText(
            "System Number"
        )

        self.input_sys.setReadOnly(False)

        self.input_sys.setStyleSheet(
            """
            QLineEdit {

                background-color: #e8e8e8;

                color: #111111;

                border: 1.5px solid #00d2ff;

                border-radius: 6px;

                padding: 10px 14px;

                font-family:
                    'Consolas',
                    'Courier New',
                    monospace;

                font-weight: bold;

                font-size: 16px;
            }
            """
        )

        form_layout.addWidget(
            self.input_sys
        )


        # ====================================================
        # REGISTER + NAME
        # ====================================================

        row2 = QHBoxLayout()

        self.input_id = CustomLineEdit(
            "Register Number"
        )

        self.input_name = CustomLineEdit(
            "Student Name"
        )

        row2.addWidget(
            self.input_id
        )

        row2.addWidget(
            self.input_name
        )

        form_layout.addLayout(
            row2
        )


        # ====================================================
        # DEPARTMENT
        # ====================================================

        self.combo_dept = QComboBox()

        self.combo_dept.addItems(
            ["Select Department",
                "CSE",
                "IT",
                "ECE",
                "EEE",
                "MECH",
                "CIVIL",
                "AIDS",
                "CSE(Cyber Security)",
                "SFE",
                "BME",
                "IOT",
                "CSD"
            ]
        )

        form_layout.addWidget(
            self.combo_dept
        )


        # ====================================================
        # YEAR + SECTION
        # ====================================================

        row4 = QHBoxLayout()


        self.combo_year = QComboBox()

        self.combo_year.addItems(
            [
                "Year of Studying",
                "I Year",
                "II Year",
                "III Year",
                "IV Year"
            ]
        )


        self.combo_sec = QComboBox()

        self.combo_sec.addItems(
            [
                "Section",
                "Section A",
                "Section B",
                "Section C",
                "Section D",
                "Section E"
            ]
        )


        row4.addWidget(
            self.combo_year
        )

        row4.addWidget(
            self.combo_sec
        )

        form_layout.addLayout(
            row4
        )


        # ====================================================
        # SUBJECT + FACULTY
        # ====================================================

        row5 = QHBoxLayout()


        self.input_subject = CustomLineEdit(
            "Lab Practical Topic / Subject Name"
        )

        self.input_faculty = CustomLineEdit(
            "Faculty Name"
        )


        row5.addWidget(
            self.input_subject
        )

        row5.addWidget(
            self.input_faculty
        )


        form_layout.addLayout(
            row5
        )


        # ====================================================
        # LAB SELECTION
        # ====================================================

        row_lab = QHBoxLayout()


        lbl_lab = QLabel(
            "Lab Selection:"
        )

        lbl_lab.setAlignment(
            Qt.AlignCenter
        )

        lbl_lab.setStyleSheet(
            """
            border: 1.5px solid #00d2ff;

            background-color: #ffffff;

            color: #000000;

            border-radius: 6px;

            padding: 10px;
            """
        )


        self.combo_lab = QComboBox()


        self.combo_lab.addItems(
            [
                "Select Lab",
                "CSE Lab A Block",
                "CSE Lab B Block",
                "Virtusa Lab C Block",
                "MCA NET Lab C Block",
                "R2S Lab F Block",
                "Future Tech F Block",
                "Data Spere Laboratory F Block"
            ]
        )


        row_lab.addWidget(
            lbl_lab,
            stretch=2
        )

        row_lab.addWidget(
            self.combo_lab,
            stretch=8
        )


        form_layout.addLayout(
            row_lab
        )


        # ====================================================
        # TIME SLOTS
        # ====================================================

        row_times = QHBoxLayout()


        time_slots = []

        slot_time = QTime(9, 0)
        final_slot_time = QTime(16, 30)

        while slot_time <= final_slot_time:

            time_slots.append(
                slot_time.toString("hh:mm AP")
            )

            slot_time = slot_time.addSecs(5 * 60)


        self.combo_start = QComboBox()

        self.combo_start.addItems(
            time_slots
        )


        self.combo_end = QComboBox()

        self.combo_end.addItems(
            time_slots
        )


        lbl_slot = QLabel(
            "Lab Slot:"
        )

        lbl_slot.setAlignment(
            Qt.AlignCenter
        )

        lbl_slot.setStyleSheet(
            """
            border: 1.5px solid #00d2ff;

            background-color: #ffffff;

            color: #000000;

            border-radius: 6px;

            padding: 10px;
            """
        )


        lbl_to = QLabel(
            "to"
        )

        lbl_to.setAlignment(
            Qt.AlignCenter
        )

        lbl_to.setStyleSheet(
            """
            border: 1.5px solid #00d2ff;

            background-color: #ffffff;

            color: #000000;

            border-radius: 6px;

            padding: 10px;
            """
        )


        row_times.addWidget(
            lbl_slot,
            stretch=2
        )

        row_times.addWidget(
            self.combo_start,
            stretch=3
        )

        row_times.addWidget(
            lbl_to,
            stretch=2
        )

        row_times.addWidget(
            self.combo_end,
            stretch=3
        )


        form_layout.addLayout(
            row_times
        )


        layout.addLayout(
            form_layout
        )


        layout.addSpacing(
            15
        )


        # ====================================================
        # SUBMIT BUTTON
        # ====================================================

        self.btn_submit = QPushButton(
            "[  SUBMIT   START LAB  ]"
        )

        self.btn_submit.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_submit.setStyleSheet(
            """
            QPushButton {

                background-color: #0b6623;

                color: #ffffff;

                font-family:
                    'Consolas',
                    'Courier New',
                    monospace;

                font-weight: bold;

                font-size: 18px;

                padding: 12px;

                border: 2px solid #228b22;

                border-radius: 6px;
            }

            QPushButton:hover {

                background-color: #0e812d;

                border: 2px solid #00ff00;
            }

            QPushButton:pressed {

                background-color: #064d1a;
            }
            """
        )


        self.btn_submit.clicked.connect(
            self.submit_data
        )


        layout.addWidget(
            self.btn_submit
        )


        # ====================================================
        # STATUS
        # ====================================================

        self.lbl_status = QLabel(
            f"Status: Ready. Connecting to Admin Server "
            
        )

        self.lbl_status.setAlignment(
            Qt.AlignCenter
        )

        self.lbl_status.setStyleSheet(
            """
            font-size: 13px;

            color: #719bbd;

            border: none;

            margin-top: 10px;
            """
        )

        layout.addWidget(
            self.lbl_status
        )


        self.entry_page.setLayout(
            layout
        )


    # ========================================================
    # ACTIVE PAGE
    # ========================================================

    def init_active_page(self):

        layout = QVBoxLayout()


        title = QLabel(
            "[ 🟢 ACTIVE LAB SESSION RUNNING... ]"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size: 22px;

            color: #00ffcc;

            border: none;

            margin-bottom: 15px;
            """
        )

        layout.addWidget(
            title
        )


        self.lbl_active_info = QLabel()

        self.lbl_active_info.setStyleSheet(
            """
            border: none;

            font-size: 17px;

            color: #ffffff;
            """
        )

        layout.addWidget(
            self.lbl_active_info
        )


        # ====================================================
        # TIMER
        # ====================================================

        self.lbl_active_timer = QLabel(
            "Session Duration: 00:00:00"
        )

        self.lbl_active_timer.setAlignment(
            Qt.AlignCenter
        )

        self.lbl_active_timer.setStyleSheet(
            """
            border: none;

            font-size: 28px;

            color: #00ffcc;

            margin: 20px 0;
            """
        )

        layout.addWidget(
            self.lbl_active_timer
        )


        self.lbl_exit_countdown = QLabel(
            "EXIT ENABLES IN --:--:--"
        )

        self.lbl_exit_countdown.setAlignment(
            Qt.AlignCenter
        )

        self.lbl_exit_countdown.setStyleSheet(
            """
            QLabel {
                color: #ffaa00;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            self.lbl_exit_countdown
        )


        # ====================================================
        # EXIT BUTTON
        # ====================================================

        self.btn_exit = QPushButton(
            "[ EXIT & SHUTDOWN SESSION ]"
        )

        self.btn_exit.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_exit.setEnabled(
            False
        )

        self.btn_exit.setStyleSheet(
            """
            QPushButton {

                background-color: #ff3366;

                color: white;

                font-family: 'Consolas';

                font-weight: bold;

                font-size: 18px;

                padding: 12px;

                border: none;

                border-radius: 6px;
            }

            QPushButton:hover {

                background-color: #cc0033;
            }

            QPushButton:pressed {

                background-color: #990022;
            }

            QPushButton:disabled {

                background-color: #3a3a3a;

                color: #888888;

                border: 1px solid #555555;
            }
            """
        )


        self.btn_exit.clicked.connect(
            self.show_exit_summary
        )


        layout.addWidget(
            self.btn_exit
        )


        self.active_page.setLayout(
            layout
        )


    # ========================================================
    # EXIT PAGE
    # ========================================================

    def init_exit_page(self):

        layout = QVBoxLayout()


        title = QLabel(
            "[ 🔄 RECORDING SESSION EXIT... ]"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size: 22px;

            color: #00d2ff;

            border: none;

            margin-bottom: 20px;
            """
        )

        layout.addWidget(
            title
        )


        self.lbl_exit_summary = QLabel()

        self.lbl_exit_summary.setStyleSheet(
            """
            border: none;

            font-size: 18px;

            color: #ffffff;
            """
        )

        layout.addWidget(
            self.lbl_exit_summary
        )


        self.lbl_shutdown = QLabel(
            "Shutting down session in 3 seconds..."
        )

        self.lbl_shutdown.setStyleSheet(
            """
            font-size: 16px;

            color: #ff3366;

            border: none;

            margin-top: 15px;
            """
        )

        layout.addWidget(
            self.lbl_shutdown
        )


        self.exit_page.setLayout(
            layout
        )


    # ========================================================
    # SUBMIT / START SESSION
    # ========================================================

    def submit_data(self):

        # ----------------------------------------------------
        # Read values
        # ----------------------------------------------------

        register_number = (
            self.input_id.text().strip()
        )

        student_name = (
            self.input_name.text().strip()
        )

        subject_name = (
            self.input_subject.text().strip()
        )

        faculty_name = (
            self.input_faculty.text().strip()
        )

        system_number = (
            self.input_sys.text().strip()
        )

        department = (
            self.combo_dept.currentText()
        )

        year = (
            self.combo_year.currentText()
        )

        section = (
            self.combo_sec.currentText()
        )

        lab_name = (
            self.combo_lab.currentText()
        )

        lab_start_time = (
            self.combo_start.currentText()
        )

        lab_end_time = (
            self.combo_end.currentText()
        )


        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not register_number:

            self.show_message(
                "Warning",
                "Please enter Register Number.",
                QMessageBox.Warning
            )

            self.input_id.setFocus()

            return


        if not student_name:

            self.show_message(
                "Warning",
                "Please enter Student Name.",
                QMessageBox.Warning
            )

            self.input_name.setFocus()

            return


        if year == "Year of Studying":

            self.show_message(
                "Warning",
                "Please select Class / Batch.",
                QMessageBox.Warning
            )

            return


        if section == "Section":

            self.show_message(
                "Warning",
                "Please select Section.",
                QMessageBox.Warning
            )

            return


        if not subject_name:

            self.show_message(
                "Warning",
                "Please enter Lab Practical Topic / Subject Name.",
                QMessageBox.Warning
            )

            self.input_subject.setFocus()

            return


        if lab_name == "Select Lab":

            self.show_message(
                "Warning",
                "Please select the Lab.",
                QMessageBox.Warning
            )

            self.combo_lab.setFocus()

            return


        # ----------------------------------------------------
        # Entry Time
        # ----------------------------------------------------

        self.entry_datetime = (
            QDateTime.currentDateTime()
        )

        self.entry_time_str = (
            self.entry_datetime.toString(
                "hh:mm:ss AP"
            )
        )


        # ----------------------------------------------------
        # Reset timer
        # ----------------------------------------------------

        self.elapsed_seconds = 0


        # ----------------------------------------------------
        # Payload
        # ----------------------------------------------------

        payload = {

            "user_role":
                self.user_role,

            "user_id":
                register_number,

            "student_name":
                student_name,

            "department":
                department,

            "section":
                section,

            "year":
                year,

            "system_number":
                system_number,

            "subject_name":
                subject_name,

            "faculty_name":
                faculty_name,

            "lab_name":
                lab_name,

            "lab_start_time":
                lab_start_time,

            "lab_end_time":
                lab_end_time
        }


        # ----------------------------------------------------
        # Disable submit button
        # ----------------------------------------------------

        self.btn_submit.setEnabled(
            False
        )

        self.btn_submit.setText(
            "[  CONNECTING TO SERVER...  ]"
        )


        self.lbl_status.setText(
            "Status: Saving lab entry..."
        )


        QApplication.processEvents()


        # ====================================================
        # SEND ENTRY TO NODE SERVER
        # ====================================================

        try:

            response = requests.post(

                f"{SERVER_URL}/api/entry",

                json=payload,

                timeout=5
            )


            res = response.json()


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if res.get("success"):

                self.session_id = (
                    res.get("session_id")
                )

                threading.Thread(
                    target=self.listen_for_admin_exit,
                    args=(self.session_id,),
                    daemon=True
                ).start()

                self.lbl_status.setText(
                    "Status: Lab session started successfully."
                )

            else:

                self.show_message(
                    "Entry Failed",
                    res.get("message")
                    or res.get("error")
                    or "Unable to start lab session.",
                    QMessageBox.Warning
                )

                self.btn_submit.setEnabled(
                    True
                )

                self.btn_submit.setText(
                    "[  SUBMIT   START LAB  ]"
                )

                return


        # ====================================================
        # CONNECTION ERROR
        # ====================================================

        except requests.exceptions.ConnectionError:

            self.show_message(
                "Connection Error",
                "Cannot connect to the Lab Attendance Server.\n\n"
                "Please check your Internet Connection or Local Network.",
                QMessageBox.Critical
            )


            self.btn_submit.setEnabled(
                True
            )

            self.btn_submit.setText(
                "[  SUBMIT   START LAB  ]"
            )

            self.lbl_status.setText(
                "Status: Network connection failed."
            )

            return


        # ====================================================
        # TIMEOUT
        # ====================================================

        except requests.exceptions.Timeout:

            self.show_message(
                "Server Timeout",
                "The Admin Server did not respond "
                "within the allowed time.",
                QMessageBox.Critical
            )


            self.btn_submit.setEnabled(
                True
            )

            self.btn_submit.setText(
                "[  SUBMIT   START LAB  ]"
            )

            return


        # ====================================================
        # OTHER ERROR
        # ====================================================

        except Exception as e:

            self.show_message(
                "Error",
                f"Unexpected error:\n\n{str(e)}",
                QMessageBox.Critical
            )


            self.btn_submit.setEnabled(
                True
            )

            self.btn_submit.setText(
                "[  SUBMIT   START LAB  ]"
            )

            return


        # ====================================================
        # UPDATE ACTIVE SCREEN
        # ====================================================

        info_text = f"""

Student Register No : {register_number}

Student Name        : {student_name}

Department          : {department}

Class / Batch       : {year}

Section             : {section}

System Number       : {system_number}

Lab Name            : {lab_name}

Subject / Topic     : {subject_name}

Faculty In-Charge   : {faculty_name}

Lab Schedule        : {lab_start_time} to {lab_end_time}

Actual Entry Time   : {self.entry_time_str}

"""


        self.lbl_active_info.setText(
            info_text
        )


        # ====================================================
        # START SESSION
        # ====================================================

        self.session_started = True

        self.exit_completed = False

        self.btn_exit.setEnabled(
            False
        )

        self.update_exit_countdown()


        self.stacked_widget.setCurrentIndex(
            1
        )


        self.timer.start(
            1000
        )


    def listen_for_admin_exit(self, session_id):

        if not session_id:
            return

        sio.on(
            f"force_exit_{session_id}",
            lambda data: self.admin_exit_signal.emit()
        )

        try:
            sio.connect(SERVER_URL)
        except Exception as error:
            print("Socket connection error:", error)


    def handle_admin_force_exit(self):

        if self.session_started:
            self.show_exit_summary(forced=True)


    # ========================================================
    # TIMER UPDATE
    # ========================================================

    def update_timer(self):

        if self.entry_datetime is None:

            return


        # Calculate actual elapsed time
        # instead of simply adding 1 second
        current_datetime = (
            QDateTime.currentDateTime()
        )


        milliseconds = (
            self.entry_datetime.msecsTo(
                current_datetime
            )
        )


        self.elapsed_seconds = max(
            0,
            milliseconds // 1000
        )


        hours = (
            self.elapsed_seconds // 3600
        )

        minutes = (
            (self.elapsed_seconds % 3600)
            // 60
        )

        seconds = (
            self.elapsed_seconds % 60
        )


        time_str = (

            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


        self.lbl_active_timer.setText(

            f"Session Duration: "
            f"{time_str}"
        )

        self.update_exit_countdown()


    def get_exit_enable_datetime(self):

        end_time_text = (
            self.combo_end.currentText().strip()
        )

        end_time = QDateTime.fromString(
            end_time_text,
            "hh:mm AP"
        )

        if not end_time.isValid():

            return None

        now = QDateTime.currentDateTime()

        end_time.setDate(
            now.date()
        )

        return end_time.addSecs(
            -10 * 60
        )


    def update_exit_countdown(self):

        if not self.session_started:

            return

        enable_time = self.get_exit_enable_datetime()

        if enable_time is None:

            return

        now = QDateTime.currentDateTime()

        remaining_ms = now.msecsTo(
            enable_time
        )

        if remaining_ms <= 0:

            self.btn_exit.setEnabled(
                True
            )

            self.lbl_exit_countdown.setText(
                "EXIT SESSION IS NOW AVAILABLE"
            )

            self.lbl_exit_countdown.setStyleSheet(
                """
                QLabel {
                    color: #00ff66;
                    font-size: 17px;
                    font-weight: bold;
                    border: none;
                    padding: 8px;
                }
                """
            )

            return

        total_seconds = remaining_ms // 1000

        hours = total_seconds // 3600

        minutes = (
            (total_seconds % 3600) // 60
        )

        seconds = total_seconds % 60

        self.btn_exit.setEnabled(
            False
        )

        self.lbl_exit_countdown.setText(
            f"EXIT ENABLES IN "
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        self.lbl_exit_countdown.setStyleSheet(
            """
            QLabel {
                color: #ffaa00;
                font-size: 17px;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            """
        )


    # ========================================================
    # EXIT SESSION
    # ========================================================

    def show_exit_summary(self, forced=False):

        if not self.session_started:

            return


        # ----------------------------------------------------
        # Confirmation
        # ----------------------------------------------------

        if not forced:
            box = QMessageBox(self)

            box.setWindowTitle(
                "Confirm Exit"
            )

            box.setText(
                "Are you sure you want to exit "
                "the lab session?"
            )

            box.setIcon(
                QMessageBox.Question
            )

            box.setStandardButtons(
                QMessageBox.Yes |
                QMessageBox.No
            )

            box.setDefaultButton(
                QMessageBox.No
            )

            box.setStyleSheet(
                """
                QMessageBox {
                    background-color: #ffffff;
                }

                QMessageBox QLabel {
                    color: #111111;
                    background-color: #ffffff;
                    font-family: "Segoe UI";
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }

                QMessageBox QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 25px;
                    min-width: 70px;
                    font-family: "Segoe UI";
                    font-size: 13px;
                    font-weight: bold;
                }

                QMessageBox QPushButton:hover {
                    background-color: #005a9e;
                }
                """
            )

            reply = box.exec()


            if reply != QMessageBox.Yes:

                return


        # ----------------------------------------------------
        # Stop timer
        # ----------------------------------------------------

        self.timer.stop()


        # ----------------------------------------------------
        # Calculate exit time
        # ----------------------------------------------------

        exit_datetime = (
            QDateTime.currentDateTime()
        )

        exit_time_str = (
            exit_datetime.toString(
                "hh:mm:ss AP"
            )
        )


        # ----------------------------------------------------
        # Calculate duration
        # ----------------------------------------------------

        if self.entry_datetime is not None:

            milliseconds = (
                self.entry_datetime.msecsTo(
                    exit_datetime
                )
            )

            self.elapsed_seconds = max(
                0,
                milliseconds // 1000
            )


        hours = (
            self.elapsed_seconds // 3600
        )

        minutes = (
            (self.elapsed_seconds % 3600)
            // 60
        )

        seconds = (
            self.elapsed_seconds % 60
        )


        duration_str = (

            f"{hours} Hours "
            f"{minutes} Mins "
            f"{seconds} Secs"
        )


        # ====================================================
        # SEND EXIT TO SERVER
        # ====================================================

        exit_success = False


        if self.session_id:

            try:

                response = requests.post(

                    f"{SERVER_URL}/api/exit",

                    json={

                        "session_id":
                            self.session_id,

                        "duration":
                            duration_str
                    },

                    timeout=5
                )


                res = response.json()


                if res.get("success"):

                    exit_success = True


            except Exception as e:

                print(
                    "Exit API Error:",
                    e
                )


        # ====================================================
        # SUMMARY
        # ====================================================

        if forced:
            status_text = (
                "Session terminated by Admin. Data saved to Department Server."
                if exit_success
                else "Session terminated by Admin. Please verify server connection."
            )
        else:
            status_text = (
                "Data saved to Department Server."
                if exit_success
                else "Session completed locally. Please verify server connection."
            )


        summary_text = f"""

Student Register No : {self.input_id.text().strip()}

Student Name        : {self.input_name.text().strip()}

Department          : {self.combo_dept.currentText()}

Class / Batch       : {self.combo_year.currentText()}

Section             : {self.combo_sec.currentText()}

System Number       : {self.input_sys.text().strip()}

Lab Name            : {self.combo_lab.currentText()}

Subject / Topic     : {self.input_subject.text().strip()}

Faculty In-Charge   : {self.input_faculty.text().strip()}

Entry Time          : {self.entry_time_str}

Exit Time           : {exit_time_str}

Total Duration      : {duration_str}


Status: {status_text}
"""


        self.lbl_exit_summary.setText(
            summary_text
        )


        self.stacked_widget.setCurrentIndex(
            2
        )


        # ----------------------------------------------------
        # Mark session completed
        # ----------------------------------------------------

        self.session_started = False

        self.exit_completed = True


        # ----------------------------------------------------
        # Close application
        # ----------------------------------------------------

        QTimer.singleShot(
            3000,
            self.close_application
        )


    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(self):

        self.exit_completed = True

        QApplication.quit()


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    ex = LabApp()

    ex.show()

    sys.exit(
        app.exec_()
    )
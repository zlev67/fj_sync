from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from zlev.synchronize.Synchronize import Synchronize


class Worker(QObject):
    update_signal = Signal(str)  # Signal to send updates to the interface

    def __init__(self):
        super().__init__()
        self.running = False

    def start_work(self):
        self.running = True
        for i in range(5):  # Simulate background work
            if not self.running:
                break
            self.update_signal.emit(f"Update {i + 1}")  # Emit signal with update
            QThread.sleep(1)  # Simulate delay

    def stop_work(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window with Layouts")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        main_layout = QVBoxLayout()
        # Add common fields
        self.add_common_fields(main_layout)
        # Left and right layouts
        horizontal_layout = QHBoxLayout()

        # Left vertical layout
        self.left_layout = QVBoxLayout()
        self.left_widgets = dict()
        self.populate_left_layout()
        horizontal_layout.addLayout(self.left_layout)

        # Right vertical layout
        self.right_layout = QVBoxLayout()
        self.right_widgets = dict()
        self.populate_right_layout()
        horizontal_layout.addLayout(self.right_layout)
        main_layout.addLayout(horizontal_layout)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Background process setup
        self.worker = Worker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.update_signal.connect(self.update_interface)

    def start_process(self):
        self.thread.started.connect(self.worker.start_work)
        self.thread.start()

    def stop_process(self):
        self.worker.stop_work()
        self.thread.quit()
        self.thread.wait()

    def update_interface(self, message):
        self.label.setText(message)

    def add_common_fields(self, layout):
        """Adds common fields to the main layout."""
        # Group box for radio buttons
        group_box = QGroupBox("File Synchronization Options")
        radio_layout = QVBoxLayout()

        local_to_fj_radio = QRadioButton("Local to FJ")
        fj_to_local_radio = QRadioButton("FJ to Local")
        all_files_radio = QRadioButton("All files to Both Sides")

        radio_layout.addWidget(local_to_fj_radio)
        radio_layout.addWidget(fj_to_local_radio)
        radio_layout.addWidget(all_files_radio)
        group_box.setLayout(radio_layout)

        layout.addWidget(group_box)

        # Start and Close buttons
        button_layout = QHBoxLayout()
        start_button = QPushButton("Start")
        close_button = QPushButton("Close")

        button_layout.addWidget(start_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def populate_left_layout(self):
        """Populates the left vertical layout with widgets."""
        self.create_common_part(self.left_layout, self.left_fields)

    def populate_right_layout(self):
        """Populates the right vertical layout with widgets."""
        self.create_common_part(self.right_layout, self.right_fields)

    def create_common_part(self, layout, fields_dict):
        """Creates the common part of the layouts and stores widgets in the given dictionary."""
        # Path input and Browse button
        path_layout = QHBoxLayout()
        path_list = QListWidget()
        browse_button = QPushButton("Browse")
        path_layout.addWidget(path_list)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        # Store widgets in the dictionary
        fields_dict["path_edit"] = path_list
        fields_dict["browse_button"] = browse_button

        # Table for file details
        file_table = QTableWidget()
        file_table.setColumnCount(6)
        file_table.setHorizontalHeaderLabels(["Path", "Name", "Creation Date", "Modification Date", "Size", "SHA256"])
        layout.addWidget(file_table)

        # Store the table in the dictionary
        fields_dict["file_table"] = file_table

    def browse_local_paths(self):
        """Callback for the Browse button in local_paths."""
        # Placeholder for browse code
        result = None  # Replace with actual file dialog code
        if result is not None:
            self.left_widgets["path_list"].addItem(result)

    def browse_fj_paths(self):
        """Callback for the Browse button in fj_paths."""
        # Placeholder for browse code
        result = None  # Replace with actual file dialog code
        if result is not None:
            self.right_widgets["path_list"].addItem(result)

    def close_application(self):
        """Callback for the Close button."""
        if not self.is_process_running():  # Replace with actual process check
            self.close()
        else:
            reply = QMessageBox.question(
                self,
                "Process Running",
                "A process is currently running. Do you want to stop it and close the application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.stop_process()  # Replace with actual process stop logic
                self.close()

    def start_process(self):
        """Callback for the Start button."""
        # Placeholder for start process logic
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
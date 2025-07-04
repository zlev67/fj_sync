from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, \
    QMessageBox, QGroupBox, QRadioButton, QListWidget, QTableWidget, QInputDialog, QTableWidgetItem, QLabel, QCheckBox
from PySide6.QtCore import Qt, QThread

from zlev.synchronize.SyncData import SyncData
from zlev.filejump.FileJumpApi import FileJumpApi
from zlev.synchronize.Worker import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window with Layouts")
        self.setGeometry(100, 100, 900, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # --- Top row: Options+Collision (vertical), Source, Arrow, Destination, Actions group ---
        top_row_layout = QHBoxLayout()

        # Vertical layout for File Synchronization Options and Collision Resolution
        self.options_and_collision_layout = QVBoxLayout()
        # File Synchronization Options group (small)
        self.options_group = QGroupBox("File Synchronization Options")
        self.options_group.setMaximumWidth(200)
        options_layout = QVBoxLayout()
        self.local_to_fj_radio = QRadioButton("Local to FJ")
        self.local_to_fj_radio.setChecked(True)
        self.fj_to_local_radio = QRadioButton("FJ to Local")
        self.all_files_radio = QRadioButton("All files to Both Sides")
        options_layout.addWidget(self.local_to_fj_radio)
        options_layout.addWidget(self.fj_to_local_radio)
        options_layout.addWidget(self.all_files_radio)
        self.options_group.setLayout(options_layout)
        self.options_and_collision_layout.addWidget(self.options_group)

        # Collision Resolution group (small)
        self.collision_group = QGroupBox("Collision Resolution")
        self.collision_group.setMaximumWidth(200)
        collision_layout = QVBoxLayout()
        self.collision_overwrite_radio = QRadioButton("Overwrite")
        self.collision_overwrite_radio.setChecked(True)
        self.collision_rename_old_radio = QRadioButton("Rename Old")
        self.collision_rename_new_radio = QRadioButton("Rename New")
        # Add the new checkbox
        self.collision_delete_checkbox = QCheckBox("Delete at destination")
        collision_layout.addWidget(self.collision_overwrite_radio)
        collision_layout.addWidget(self.collision_rename_old_radio)
        collision_layout.addWidget(self.collision_rename_new_radio)
        collision_layout.addWidget(self.collision_delete_checkbox)
        self.collision_group.setLayout(collision_layout)
        self.options_and_collision_layout.addWidget(self.collision_group)

        # Add the vertical layout to the top row
        top_row_layout.addLayout(self.options_and_collision_layout)

        # Local group
        local_group = QGroupBox("Local")
        local_group_layout = QVBoxLayout()
        self.left_widgets = dict()
        self.left_widgets["path_list"] = QListWidget()
        local_group_layout.addWidget(self.left_widgets["path_list"])
        local_btn_layout = QHBoxLayout()
        self.left_widgets["browse_button"] = QPushButton("Browse")
        self.left_widgets["delete_button"] = QPushButton("Delete")
        local_btn_layout.addWidget(self.left_widgets["browse_button"])
        local_btn_layout.addWidget(self.left_widgets["delete_button"])
        local_group_layout.addLayout(local_btn_layout)
        local_group.setLayout(local_group_layout)

        # FileJump group
        fj_group = QGroupBox("FileJump")
        fj_group_layout = QVBoxLayout()
        self.right_widgets = dict()
        self.right_widgets["path_list"] = QListWidget()
        fj_group_layout.addWidget(self.right_widgets["path_list"])
        fj_btn_layout = QHBoxLayout()
        self.right_widgets["browse_button"] = QPushButton("Browse")
        self.right_widgets["delete_button"] = QPushButton("Delete")
        fj_btn_layout.addWidget(self.right_widgets["browse_button"])
        fj_btn_layout.addWidget(self.right_widgets["delete_button"])
        fj_group_layout.addLayout(fj_btn_layout)
        fj_group.setLayout(fj_group_layout)

        # Arrow icon label (big and colorful) for top row
        self.arrow_label = QLabel()
        self.arrow_label.setAlignment(Qt.AlignCenter)
        self.arrow_label.setFixedWidth(60)
        self.arrow_label.setStyleSheet("font-size: 48px; color: #1976d2;")
        self._update_arrow_icon()

        # Actions group (Scan Directories and Start)
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        self.scan_button = QPushButton("Scan Directories")
        self.start_button = QPushButton("Start")
        actions_layout.addWidget(self.scan_button)
        actions_layout.addWidget(self.start_button)
        actions_group.setLayout(actions_layout)

        # Save references for dynamic layout
        self.top_row_layout = top_row_layout
        self.local_group = local_group
        self.fj_group = fj_group
        self.actions_group = actions_group
        main_layout.addLayout(top_row_layout)

        # --- Tables row with arrow between ---
        tables_row_layout = QHBoxLayout()
        self.left_widgets["file_table"] = QTableWidget()
        self.left_widgets["file_table"].setColumnCount(6)
        self.left_widgets["file_table"].setHorizontalHeaderLabels(
            ["Path", "Name", "Creation Date", "Modification Date", "Size", "SHA256"]
        )
        self.right_widgets["file_table"] = QTableWidget()
        self.right_widgets["file_table"].setColumnCount(6)
        self.right_widgets["file_table"].setHorizontalHeaderLabels(
            ["Path", "Name", "Creation Date", "Modification Date", "Size", "SHA256"]
        )
        # Arrow label between tables
        self.tables_arrow_label = QLabel()
        self.tables_arrow_label.setAlignment(Qt.AlignCenter)
        self.tables_arrow_label.setFixedWidth(60)
        self.tables_arrow_label.setStyleSheet("font-size: 48px; color: #1976d2;")
        self._update_tables_arrow_icon()
        self.tables_row_layout = tables_row_layout
        main_layout.addLayout(tables_row_layout)

        # --- Bottom row: Close button ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Add status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Connect buttons
        self.left_widgets["browse_button"].clicked.connect(self.browse_local_paths)
        self.left_widgets["delete_button"].clicked.connect(self.delete_local_path)
        self.right_widgets["browse_button"].clicked.connect(self.browse_fj_paths)
        self.right_widgets["delete_button"].clicked.connect(self.delete_fj_path)
        self.scan_button.clicked.connect(self.scan_directories_callback)
        self.close_button.clicked.connect(self.close_application)
        self.start_button.clicked.connect(self.start_process)

        # Connect list changes to update scan button state and browse button state
        self.left_widgets["path_list"].model().rowsInserted.connect(self.update_scan_button_state)
        self.left_widgets["path_list"].model().rowsRemoved.connect(self.update_scan_button_state)
        self.right_widgets["path_list"].model().rowsInserted.connect(self.update_scan_button_state)
        self.right_widgets["path_list"].model().rowsRemoved.connect(self.update_scan_button_state)
        self.left_widgets["path_list"].model().rowsInserted.connect(self.update_browse_buttons_state)
        self.left_widgets["path_list"].model().rowsRemoved.connect(self.update_browse_buttons_state)
        self.right_widgets["path_list"].model().rowsInserted.connect(self.update_browse_buttons_state)
        self.right_widgets["path_list"].model().rowsRemoved.connect(self.update_browse_buttons_state)

        # Worker and thread setup
        self.filejump_api = FileJumpApi()
        self.local_files = None
        self.fj_files = None

        self.worker = Worker(filejump_api=self.filejump_api)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.update_signal.connect(self.update_interface)
        self.worker.fj_tree_loaded.connect(self.on_fj_tree_loaded)
        self.worker.scan_done.connect(self.on_scan_done)
        self.thread.start()

        # Initial state
        self.update_scan_button_state()
        self.update_browse_buttons_state()
        self.start_button.setEnabled(False)
        self.update_source_dest_layout()  # Set initial layout

        # Connect radio buttons to update layout and arrow
        self.local_to_fj_radio.toggled.connect(self.update_source_dest_layout)
        self.fj_to_local_radio.toggled.connect(self.update_source_dest_layout)
        self.all_files_radio.toggled.connect(self.update_source_dest_layout)
        self.update_source_dest_layout()  # Set initial layout

        # Check for sync_data.json and prompt user to load if exists
        self.check_and_load_sync_data()

    def _update_arrow_icon(self):
        """Set the arrow icon direction to always point to the second box, or double arrow for both sides, big and colorful."""
        if self.all_files_radio.isChecked():
            self.arrow_label.setText("🔁")
        else:
            self.arrow_label.setText("➡️")

    def _update_tables_arrow_icon(self):
        """Set the arrow icon between tables."""
        if self.all_files_radio.isChecked():
            self.tables_arrow_label.setText("🔁")
        else:
            self.tables_arrow_label.setText("➡️")

    def update_scan_button_state(self):
        """Enable Scan Directories only if both lists have at least one item. Start is always disabled until scan."""
        local_count = self.left_widgets["path_list"].count()
        fj_count = self.right_widgets["path_list"].count()
        self.scan_button.setEnabled(local_count > 0 and fj_count > 0)
        self.start_button.setEnabled(False)  # Always disable Start until scan completes

    def update_browse_buttons_state(self):
        """Disable Browse button in destination group if list already has one item; enable if 0 items.
        Also disable Delete buttons if 0 items in list."""
        # Determine which is destination group based on radio selection
        if self.local_to_fj_radio.isChecked():
            dest_list = self.right_widgets["path_list"]
            dest_browse = self.right_widgets["browse_button"]
        elif self.fj_to_local_radio.isChecked():
            dest_list = self.left_widgets["path_list"]
            dest_browse = self.left_widgets["browse_button"]
        else:  # all_files_radio
            # In both-sides mode, allow both browse buttons
            self.left_widgets["browse_button"].setEnabled(True)
            self.right_widgets["browse_button"].setEnabled(True)
            # Also handle Delete buttons for both lists
            self.left_widgets["delete_button"].setEnabled(self.left_widgets["path_list"].count() > 0)
            self.right_widgets["delete_button"].setEnabled(self.right_widgets["path_list"].count() > 0)
            return

        if dest_list.count() >= 1:
            dest_browse.setEnabled(False)
        else:
            dest_browse.setEnabled(True)

        # Also handle Delete buttons for both lists
        self.left_widgets["delete_button"].setEnabled(self.left_widgets["path_list"].count() > 0)
        self.right_widgets["delete_button"].setEnabled(self.right_widgets["path_list"].count() > 0)

    def update_source_dest_layout(self):
        """Rearrange Local/FileJump groups and tables so source is always left and destination is right, and update arrows."""
        # --- Top row ---
        while self.top_row_layout.count():
            item = self.top_row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.top_row_layout.addLayout(self.options_and_collision_layout)
        self._update_arrow_icon()
        self._update_tables_arrow_icon()

        # Determine order and swap if needed
        if self.local_to_fj_radio.isChecked():
            # Local left, FJ right
            self.top_row_layout.addWidget(self.local_group)
            self.top_row_layout.addWidget(self.arrow_label)
            self.top_row_layout.addWidget(self.fj_group)
            self.top_row_layout.addWidget(self.actions_group)
            self.top_row_layout.addStretch()
            self._set_tables_order(left_table=self.left_widgets["file_table"], right_table=self.right_widgets["file_table"])
            self._ensure_only_one_path(self.right_widgets["path_list"])
            # Enable Browse in source (Local), update dest (FJ)
            self.left_widgets["browse_button"].setEnabled(True)
            self.update_browse_buttons_state()
        elif self.fj_to_local_radio.isChecked():
            # FJ left, Local right
            self.top_row_layout.addWidget(self.fj_group)
            self.top_row_layout.addWidget(self.arrow_label)
            self.top_row_layout.addWidget(self.local_group)
            self.top_row_layout.addWidget(self.actions_group)
            self.top_row_layout.addStretch()
            self._set_tables_order(left_table=self.right_widgets["file_table"], right_table=self.left_widgets["file_table"])
            self._ensure_only_one_path(self.left_widgets["path_list"])
            # Enable Browse in source (FJ), update dest (Local)
            self.right_widgets["browse_button"].setEnabled(True)
            self.update_browse_buttons_state()
        else:  # all_files_radio
            self.top_row_layout.addWidget(self.local_group)
            self.top_row_layout.addWidget(self.arrow_label)
            self.top_row_layout.addWidget(self.fj_group)
            self.top_row_layout.addWidget(self.actions_group)
            self.top_row_layout.addStretch()
            self._set_tables_order(left_table=self.left_widgets["file_table"], right_table=self.right_widgets["file_table"])
            # In both-sides mode, allow both browse buttons
            self.left_widgets["browse_button"].setEnabled(True)
            self.right_widgets["browse_button"].setEnabled(True)

    def _set_tables_order(self, left_table, right_table):
        """Place the tables and arrow in the correct order in the tables row layout."""
        while self.tables_row_layout.count():
            item = self.tables_row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self._update_tables_arrow_icon()
        self.tables_row_layout.addWidget(left_table)
        self.tables_row_layout.addWidget(self.tables_arrow_label)
        self.tables_row_layout.addWidget(right_table)

    def _ensure_only_one_path(self, list_widget):
        """Ensure only the first path remains in the given list widget (destination list)."""
        # Remove all items except the first (index 0)
        while list_widget.count() > 1:
            list_widget.takeItem(1)

    def delete_local_path(self):
        """Remove selected item from local path list."""
        list_widget = self.left_widgets["path_list"]
        row = list_widget.currentRow()
        if row >= 0:
            list_widget.takeItem(row)
        self.update_scan_button_state()
        self.update_browse_buttons_state()

    def delete_fj_path(self):
        """Remove selected item from FileJump path list."""
        list_widget = self.right_widgets["path_list"]
        row = list_widget.currentRow()
        if row >= 0:
            list_widget.takeItem(row)
        self.update_scan_button_state()
        self.update_browse_buttons_state()

    def set_status(self, message):
        """Set the status bar message."""
        self.status_bar.showMessage(message)

    def start_process(self):
        # Store collision resolution state to SyncData before starting
        collision_mode = (
            "overwrite" if self.collision_overwrite_radio.isChecked() else
            "rename_old" if self.collision_rename_old_radio.isChecked() else
            "rename_new"
        )
        delete_at_dest = self.collision_delete_checkbox.isChecked()
        SyncData.get_instance().collision_resolution = collision_mode
        SyncData.get_instance().delete_at_destination = delete_at_dest

        self.set_status("Starting synchronization...")
        self.worker.start_upload_download.emit()

    def update_interface(self, message):
        """Updates the interface with messages from the worker."""
        # This method can be used to update the UI with messages from the worker
        print(message)

    def browse_local_paths(self):
        """Callback for the Browse button in local_paths."""
        if self.left_widgets["path_list"].count() >= 1 and self.fj_to_local_radio.isChecked():
            return  # Prevent adding more than one if Local is destination
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "/",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if dir_path:
            self.left_widgets["path_list"].addItem(dir_path)
        self.update_browse_buttons_state()

    def browse_fj_paths(self):
        """Callback for the Browse button in fj_paths."""
        if self.right_widgets["path_list"].count() >= 1 and self.local_to_fj_radio.isChecked():
            return  # Prevent adding more than one if FileJump is destination
        self.status_bar.showMessage("Loading FileJump Directory Tree...")
        if SyncData.get_instance().all_fj_entries:
            self.on_fj_tree_loaded()
            return
        self.worker.request_fj_tree.emit()
        self.update_browse_buttons_state()

    def on_fj_tree_loaded(self):
        """Slot to handle FileJump directory tree loaded from worker."""
        self.status_bar.showMessage("Loading FileJump Dir Tree...")
        f_names = []
        folder_names = SyncData.get_instance().get_fj_folders()
        if folder_names:
            f_names = [f"{name} (id: {_id})" for _id, name in folder_names.items()]
        selected, ok = QInputDialog.getItem(
            self,
            "Select FileJump Directory",
            "Choose a directory from FileJump:",
            f_names,
            0,
            False
        )
        if ok and selected:
            idx = f_names.index(selected)
            folder_name = f_names[idx]
            self.right_widgets["path_list"].addItem(f"{folder_name}")
        self.status_bar.showMessage("Ready")

    def close_application(self):
        """Callback for the Close button."""
        if not self.worker.is_running:  # Replace with actual process check
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
                self.close()


    def scan_directories_callback(self):
        """Trigger scan in worker thread and disable scan button until done."""
        self.scan_button.setEnabled(False)
        self.start_button.setEnabled(False)
        local_paths = [self.left_widgets["path_list"].item(i).text() for i in range(self.left_widgets["path_list"].count())]
        fj_folder_ids = []
        for i in range(self.right_widgets["path_list"].count()):
            text = self.right_widgets["path_list"].item(i).text()
            if "(id:" in text:
                try:
                    folder_id = text.split("(id:")[1].split(")")[0].strip()
                    fj_folder_ids.append(folder_id)
                except Exception:
                    continue
        # Set SyncData config before scanning
        direction = (
            "local_to_fj" if self.local_to_fj_radio.isChecked() else
            "fj_to_local" if self.fj_to_local_radio.isChecked() else
            "both"
        )
        SyncData.get_instance().set_config(direction, local_paths, fj_folder_ids, None)
        # Use signal to request scan in worker thread
        self.worker.scan_directories_requested.emit(local_paths, fj_folder_ids)

    def on_scan_done(self):
        """Fill tables with scan results and re-enable scan/start buttons."""
        # Fill local table
        table = self.left_widgets["file_table"]
        table.setRowCount(0)
        sd = SyncData.get_instance()
        local_entries = sd.get_local_files()
        fj_entries = sd.get_fj_files()
        for row, entry in enumerate(local_entries):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(entry["path"]))
            table.setItem(row, 1, QTableWidgetItem(entry["name"]))
            table.setItem(row, 2, QTableWidgetItem(str(entry["ctime"])))
            table.setItem(row, 3, QTableWidgetItem(str(entry["mtime"])))
            table.setItem(row, 4, QTableWidgetItem(str(entry["size"])))
            table.setItem(row, 5, QTableWidgetItem(entry["sha256"]))

        # Fill fj table
        table = self.right_widgets["file_table"]
        table.setRowCount(0)
        for row, entry in enumerate(fj_entries):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(entry["path"]))
            table.setItem(row, 1, QTableWidgetItem(entry["name"]))
            table.setItem(row, 2, QTableWidgetItem(str(entry["ctime"])))
            table.setItem(row, 3, QTableWidgetItem(str(entry["mtime"])))
            table.setItem(row, 4, QTableWidgetItem(str(entry["size"])))
            table.setItem(row, 5, QTableWidgetItem(entry["sha256"]))

        self.scan_button.setEnabled(True)   # Enable Scan button after scan is done
        self.start_button.setEnabled(True)

    def check_and_load_sync_data(self):
        """Check if sync_data.json exists and prompt user to load it."""
        if SyncData.is_backup():
            reply = QMessageBox.question(
                self,
                "Load Previous Session",
                "A previous sync_data.json file was found. Do you want to load values from it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                loaded = SyncData.get_instance().restore()
                # Load values into dialog fields after restoring SyncData
                sync_data = SyncData.get_instance()
                # Set radio buttons
                self.local_to_fj_radio.setChecked(sync_data.direction == "local_to_fj")
                self.fj_to_local_radio.setChecked(sync_data.direction == "fj_to_local")
                self.all_files_radio.setChecked(sync_data.direction == "both")
                # Set local path list
                self.left_widgets["path_list"].clear()
                if sync_data.local_folders:
                    for path in sync_data.local_folders:
                        self.left_widgets["path_list"].addItem(path)
                # Set fj path list
                self.right_widgets["path_list"].clear()
                if sync_data.fj_folders:
                    for folder in sync_data.fj_folders:
                        self.right_widgets["path_list"].addItem(folder)
                # Restore collision resolution state
                collision = sync_data.collision_resolution
                delete_at_destination= sync_data.delete_at_destination
                self.collision_overwrite_radio.setChecked(collision == "overwrite")
                self.collision_rename_old_radio.setChecked(collision == "rename_old")
                self.collision_rename_new_radio.setChecked(collision == "rename_new")
                self.collision_delete_checkbox.setChecked(delete_at_destination)
                self.update_scan_button_state()
                self.update_browse_buttons_state()
                self.on_scan_done()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
from PySide6.QtCore import QObject, Signal, Slot, QThread
from zlev.synchronize.SyncData import SyncData
from zlev.synchronize.Synchronize import Synchronize


class Worker(QObject):
    update_signal = Signal(str)
    fj_tree_loaded = Signal()
    request_fj_tree = Signal()
    start_upload_download = Signal()
    scan_directories_requested = Signal(list, list)  # local_paths, fj_folder_ids
    scan_done = Signal()  # local_entries, fj_entries

    def __init__(self, filejump_api=None):
        super().__init__()
        self.filejump_api = filejump_api
        self._is_running = False
        self.request_fj_tree.connect(self.read_fj_directory_tree)
        self.scan_directories_requested.connect(self.scan_directories)
        self.start_upload_download.connect(self.upload_download)

    def is_running(self):
        """Return True if any worker function is currently running."""
        return self._is_running

    @Slot()
    def read_fj_directory_tree(self):
        """Read the FileJump directory tree in the worker thread."""
        self._is_running = True
        try:
            if self.filejump_api is not None:
                SyncData.get_instance().init_fj()
                self.fj_tree_loaded.emit()
        finally:
            self._is_running = False

    @Slot(list, list)
    def scan_directories(self, local_paths, fj_folder_ids):
        """Scan local and FileJump directories in the worker thread and emit results."""
        self._is_running = True
        try:
            sd = SyncData.get_instance()
            sd.set_fj_files(fj_folder_ids)
            sd.set_local(local_paths)
            sd.save()
            self.scan_done.emit()
        finally:
            self._is_running = False

    @Slot()
    def upload_download(self):
        """Start the upload/download process in the worker thread."""
        self._is_running = True
        try:
            sync = Synchronize()
            sync.synchronize()
            self.update_signal.emit("Upload/Download completed.")
        finally:
            self._is_running = False

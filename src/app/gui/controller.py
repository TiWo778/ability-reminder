from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog

from .constants import YOUR_PHASES, ENEMY_PHASES, PRE_GAME_PHASE, PRE_ROUND_PHASE, ALWAYS_ACTIVE_KEYS
from .config_reader import ConfigReader
from src.data_loading.services import DownloadService
from .widgets.passive_ability_window import PassiveAbilitiesWindow
from src.core.services import ListService, PDFService, AbilityService

class GUIController:
    """
    Controller for the functionality of the GUI.
    """
    def __init__(self, main_window):
        """
        Constructor.
        :param main_window: The main window of the application.
        """
        self.main_window = main_window

        # Services
        self.list_service = ListService()
        self.pdf_service = PDFService(self.list_service)
        self.ability_service = AbilityService(self.list_service)
        self.download_service = DownloadService()
        self.config_reader = ConfigReader()

        # State
        self.phase_abilities_dict = None
        self.current_round = 0
        self.phase_counter = -1
        self.priority = "You"
        self.game_history = []
        self.current_turn_order = None
        self.passive_window = None
        self.data_dir = self.config_reader.get("data_dir")
        self.pdf_dir = self.config_reader.get("pdf_dir")

        if self.data_dir != "":
            self._update_data_dir()
        if self.pdf_dir != "":
            self._update_pdf_dir()

        self.connect_views()

    def connect_views(self):
        """
        Connects UI elements of the main window to functionality.
        """
        init_view = self.main_window.initial_view
        game_view = self.main_window.game_view
        all_phases_view = self.main_window.all_phases_view

        init_view.submit_button.clicked.connect(self.handle_submit)
        init_view.create_pdf_button.clicked.connect(self.handle_create_pdf)
        init_view.start_game_button.clicked.connect(self.handle_start_game)
        init_view.show_all_button.clicked.connect(self.handle_show_all)
        init_view.download_action.triggered.connect(self.handle_download)
        init_view.refresh_action.triggered.connect(self.handle_refresh)
        init_view.delete_action.triggered.connect(self.handle_delete)
        init_view.change_data_dir_action.triggered.connect(self.handle_change_data_dir)
        init_view.change_pdf_dir_action.triggered.connect(self.handle_change_pdf_dir)

        game_view.prev_button.clicked.connect(self.handle_prev)
        game_view.next_button.clicked.connect(self.handle_next)
        game_view.back_button.clicked.connect(self.handle_back)
        game_view.passive_button.clicked.connect(self.show_passives)
        game_view.flip_prio_button.clicked.connect(self.flip_prio)

        all_phases_view.back_button.clicked.connect(self.handle_back)

    def handle_submit(self):
        """
        Handles the pressing of the submit button by initiating parsing of a list and enabling the other buttons.
        """
        text = self.main_window.initial_view.text_edit.toPlainText()
        try:
            self.list_service.load_from_text(text)
        except Exception as e:
            self.main_window.initial_view.submission_label.setText(f"Error parsing input: {e}")
            return

        self.main_window.initial_view.submission_label.setText("Submission successful")
        self.main_window.initial_view.create_pdf_button.setEnabled(True)
        self.main_window.initial_view.start_game_button.setEnabled(True)
        self.main_window.initial_view.show_all_button.setEnabled(True)

    def handle_create_pdf(self):
        """
        Handles the pressing of the Create PDF button by initiating PDF creation
        """
        try:
            filepath = self.pdf_service.make_pdf()
            self.main_window.initial_view.submission_label.setText(f"Successfully created PDF at: {filepath}")
        except Exception as e:
            self.main_window.initial_view.submission_label.setText(f"Error generating PDF: {e}")
            return

    def handle_download(self):
        """
        Handles the pressing of the download option by creating a worker to download files.
        """
        self._run_download_task(mode="download", title="Downloading Data", message="Downloading data now, this may take a while...")

    def handle_refresh(self):
        """
        Handles the pressing of the refresh option by creating a worker to re-download files.
        """
        self._run_download_task(mode="refresh", title="Refreshing Data", message="Refreshing local data, please wait...")

    def handle_delete(self):
        """
        Handles the pressing of the delete option by creating a worker to delete files.
        """
        self._run_download_task(mode="delete", title="Deleting Data", message="Deleting local data, please wait...")

    def handle_change_data_dir(self):
        """
        Handles the pressing of the change data directory option by opening a file dialog and changing the data directory in the current services and the config
        """
        self.data_dir = self._select_folder("Select new data folder")
        if not self.data_dir:
            self.data_dir = ""
            return

        self._update_data_dir()
        self.config_reader.set("data_dir", self.data_dir)
        self.main_window.initial_view.submission_label.setText(f"Successfully set data folder to: {self.pdf_dir}")


    def handle_change_pdf_dir(self):
        """
        Handles the pressing of the change pdf directory option by opening a file dialog and changing the pdf directory in the current services and the config
        """
        self.pdf_dir = self._select_folder("Select new PDF folder")
        if not self.pdf_dir:
            self.pdf_dir = ""
            return

        self._update_pdf_dir()
        self.config_reader.set("pdf_dir", self.pdf_dir)
        print(self.pdf_dir)
        self.main_window.initial_view.submission_label.setText(f"Successfully set PDF folder to: {self.pdf_dir}")

    def handle_show_all(self):
        """
        Handles the pressing of the show all button by getting the abilities grouped by timing and transitioning to the all_phases view.
        """
        try:
            self.phase_abilities_dict = self.ability_service.get_abilities_grouped_by_phases()
        except Exception as e:
            self.main_window.initial_view.submission_label.setText(f"Error getting ability data: {e}")

        self.update_all_phases_view()
        self.main_window.setCurrentWidget(self.main_window.all_phases_view)

    def update_all_phases_view(self):
        """
        Updates the all_phases view to display new information
        """
        self.main_window.all_phases_view.show_all_phases(self.phase_abilities_dict)

    def handle_start_game(self):
        """
        Handles the pressing of the start game button by getting the abilities grouped by timing and transitioning to the game view.
        :return:
        """
        try:
            self.phase_abilities_dict = self.ability_service.get_abilities_grouped_by_phases()
            self.current_round = 0
            self.phase_counter = -1
            self.game_history = []
            self.priority = "You"
        except Exception as e:
            self.main_window.initial_view.submission_label.setText(f"Error getting ability data: {e}")

        self.update_game_view()
        self.main_window.setCurrentWidget(self.main_window.game_view)

    def show_passives(self):
        """
        Handles the pressing of the Show All Abilities button by opening another window showing passive abilities.
        """
        if not self.phase_abilities_dict:
            QMessageBox.warning(None, "Error", "Start the game first.")
            return

        always_active_dict = {}
        for key in ALWAYS_ACTIVE_KEYS:
            always_active_dict[key] = self.phase_abilities_dict[key]

        self.passive_window = PassiveAbilitiesWindow(always_active_dict)
        self.passive_window.show()

    def handle_prev(self):
        """
        Handles the pressing of the previous phase button by displaying the previous phase data.
        """
        if not self.game_history:
            return

        self.current_round, self.phase_counter, self.priority, self.current_turn_order = self.game_history.pop()
        self.main_window.game_view.display_phase(self.construct_phase_dict())

    def handle_next(self):
        """
        Handles the pressing of the next phase button by displaying the next phase data.
        """
        self.game_history.append((self.current_round, self.phase_counter, self.priority, self.current_turn_order))
        self.phase_counter += 1

        # Switch to next round
        if self.phase_counter == len(self.current_turn_order):
            self.current_round += 1
            self.phase_counter = 0

        self.main_window.game_view.display_phase(self.construct_phase_dict())

    def handle_back(self):
        """
        Handles the pressing of the back button by resetting the state of the game view and transitioning back to the initial view.
        """
        self.phase_abilities_dict = None
        self.current_round = 0
        self.phase_counter = -1
        self.game_history = []
        self.priority = "You"
        self.main_window.setCurrentWidget(self.main_window.initial_view)

    def update_game_view(self):
        """
        Updates the game view to display new information
        """
        self.current_turn_order = [PRE_ROUND_PHASE] + YOUR_PHASES + ENEMY_PHASES
        self.main_window.game_view.display_phase(self.construct_phase_dict())
        self.current_round += 1

    def flip_prio(self):
        """
        Handles the pressing of the flip prio button by changing the state of the game view to respect the flipped priority.
        """
        if self.priority == "You":
            self.priority = "Enemy"
            self.current_turn_order = [PRE_ROUND_PHASE] + ENEMY_PHASES + YOUR_PHASES
        else:
            self.priority = "You"
            self.current_turn_order = [PRE_ROUND_PHASE] + YOUR_PHASES + ENEMY_PHASES

        self.main_window.game_view.status_label.setText(f"Switched priority to {self.priority.lower()}")

    def construct_phase_dict(self):
        """
        Constructs a dict representing a phase with all abilities in that phase to be displayed by the game view.
        """
        current_phase = self.current_turn_order[self.phase_counter] if self.phase_counter >= 0 else PRE_GAME_PHASE
        return {
            "phase": current_phase,
            "abilities": self.phase_abilities_dict[current_phase],
            "priority": self.priority,
            "round": self.current_round
        }

    def _update_data_dir(self):
        """
        Helper to update the data directory.
        """
        self.download_service.change_download_dir(self.data_dir)
        self.list_service.change_data_dir(self.data_dir)

    def _update_pdf_dir(self):
        """
        Helper to update the PDF directory.
        """
        self.pdf_service.change_pdf_location(self.pdf_dir)

    def _select_folder(self, caption):
        """
        Helper to open a file dialog and select a folder.
        :param caption: The caption for the file dialog.
        :return: the selected folder.
        """
        return QFileDialog.getExistingDirectory(caption=caption)

    def _run_download_task(self, mode: str, title: str, message: str):
        """
        Starts a worker thread to run a download/refresh/delete task and disables the main window until the thread is done.
        :param mode: The task (download/refresh/delete).
        :param title: The title of the popup window
        :param message: The message of the popup window once the thread is done.
        """
        # Disable all input while running
        self.main_window.setEnabled(False)

        # Show progress dialog (modal and blocking interactions)
        self.progress = QProgressDialog(message, None, 0, 0, self.main_window)
        self.progress.setWindowTitle(title)
        self.progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.show()

        # Setup background thread
        self.thread = QThread()
        self.worker = DownloadWorker(self.download_service, mode=mode)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_download_finished)
        self.worker.error.connect(self._on_download_error)

        # Clean up
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.start()

    def _on_download_finished(self, message):
        """
        Helper called when the download thread is finished to display a message.
        :param message: Message to display
        """
        self.progress.close()
        self.main_window.setEnabled(True)
        QMessageBox.information(self.main_window, "Done", message)
        self.main_window.initial_view.submission_label.setText(message)

    def _on_download_error(self, error):
        """
        Helper called when the download thread encounters an error to display it.
        :param error: the error to display
        """
        self.progress.close()
        self.main_window.setEnabled(True)
        QMessageBox.critical(self.main_window, "Error", f"An error occurred: {error}")
        self.main_window.initial_view.submission_label.setText(f"Error: {error}")


class DownloadWorker(QObject):
    """
    Download worker class.
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, download_service, mode="download"):
        """
        Constructor.
        :param download_service: The download service to communicate with
        :param mode: The task for the worker (Optional, defaults to "download")
        """
        super().__init__()
        self.download_service = download_service
        self.mode = mode

    def run(self):
        """
        Runs the download worker.
        """
        try:
            if self.mode == "download":
                self.download_service.download_all_files()
                self.finished.emit("Successfully downloaded all data.")
            elif self.mode == "refresh":
                self.download_service.refresh_all_files_present()
                self.finished.emit("Successfully refreshed data.")
            elif self.mode == "delete":
                self.download_service.delete_all_files_present()
                self.finished.emit("Successfully deleted data.")
        except Exception as e:
            self.error.emit(str(e))

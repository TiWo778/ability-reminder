from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QToolButton, QMenu
from PyQt6.QtCore import Qt

class InitialView(QWidget):
    """
    View initially opened, used for navigation and list submission
    """
    def __init__(self, parent=None):
        """
        Constructor
        :param parent: parent widget
        """
        super().__init__(parent)
        self.layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        self.menu_button = QToolButton()
        self.menu_button.setIcon(QIcon.fromTheme("open-menu-symbolic"))

        menu = QMenu()
        self.refresh_action = QAction("Refresh Data")
        self.delete_action = QAction("Delete All Data")
        self.download_action = QAction("Download All Data")
        self.change_data_dir_action = QAction("Change Data Directory")
        self.change_pdf_dir_action = QAction("Change PDF Directory")

        menu.addAction(self.download_action)
        menu.addAction(self.refresh_action)
        menu.addAction(self.delete_action)
        menu.addSeparator()
        menu.addAction(self.change_data_dir_action)
        menu.addAction(self.change_pdf_dir_action)
        self.menu_button.setMenu(menu)
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        top_bar.addStretch()
        top_bar.addWidget(self.menu_button)
        self.layout.addLayout(top_bar)

        # Multiline input
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Paste your list here")
        self.layout.addWidget(self.text_edit)

        # Buttons
        self.submit_button = QPushButton("Submit")
        self.create_pdf_button = QPushButton("Create PDF")
        self.create_pdf_button.setEnabled(False)
        self.start_game_button = QPushButton("Start Game")
        self.start_game_button.setEnabled(False)
        self.show_all_button = QPushButton("Show All Abilities")
        self.show_all_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.create_pdf_button)
        button_layout.addWidget(self.show_all_button)
        button_layout.addWidget(self.start_game_button)
        self.layout.addLayout(button_layout)

        # Submission label
        self.submission_label = QLabel("")
        self.layout.addWidget(self.submission_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

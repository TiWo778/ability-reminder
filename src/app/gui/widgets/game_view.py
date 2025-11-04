from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLabel
from .phase_widget import PhaseWidget


class GameView(QWidget):
    """
    View for displaying an in progress game.
    """
    def __init__(self, parent=None):
        """
        Constructor.
        :param parent: parent widget
        """
        super().__init__(parent)

        self.layout = QVBoxLayout()

        # Top bar
        top_layout = QHBoxLayout()

        self.phase_label = QLabel("—")
        self.round_label = QLabel("Round: —")
        self.priority_label = QLabel("Priority: -")
        self.phase_label.setStyleSheet("font-size: 16pt; color: #FFF;font-weight: bold;")
        self.round_label.setStyleSheet("font-size: 14pt; color: #777; margin-left: 20px;")
        self.priority_label.setStyleSheet("font-size: 12pt; color: #777; margin-left: 20px;")

        self.back_button = QPushButton("Back")

        top_layout.addWidget(self.phase_label)
        top_layout.addWidget(self.round_label)
        top_layout.addWidget(self.priority_label)
        top_layout.addStretch()
        top_layout.addWidget(self.back_button)
        self.layout.addLayout(top_layout)

        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Bottom navigation
        bottom_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Phase")
        self.next_button = QPushButton("Next Phase")
        self.passive_button = QPushButton("Show Always Active Abilities")
        self.flip_prio_button = QPushButton("Flip Priority")
        self.status_label = QLabel("")
        bottom_layout.addWidget(self.prev_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addWidget(self.flip_prio_button)
        bottom_layout.addWidget(self.passive_button)
        bottom_layout.addWidget(self.next_button)

        self.layout.addLayout(bottom_layout)
        self.setLayout(self.layout)

    def display_phase(self, phase_dict: dict[str, list]):
        """
        Refreshes the view to display a phase
        :param phase_dict: dict containing phase name and abilities
        """
        # Clear old widgets and reset status label
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.status_label.setText("")

        # Update top info bar
        self.phase_label.setText(phase_dict["phase"])

        self.round_label.setText(f"Round: {phase_dict["round"]}")

        self.priority_label.setText(f"Priority: {phase_dict["priority"]}")

        if phase_dict["phase"] == "Start of Battle Round":
            self.flip_prio_button.show()
        else:
            self.flip_prio_button.hide()

        phase_widget = PhaseWidget(phase_dict["abilities"])
        self.scroll_layout.addWidget(phase_widget)

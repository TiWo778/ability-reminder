from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
from .ability_card import AbilityCard
from .accordion_widget import AccordionSection
from .phase_widget import PhaseWidget


class PassiveAbilitiesWindow(QDialog):
    """
    Pop-out window for displaying passive abilities.
    """
    def __init__(self, abilities_dict: dict[str, list], parent=None):
        """
        Constructor.
        :param abilities_dict: dict containing the abilities for the passive timing
        :param parent: parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Always Available Abilities")
        self.setMinimumSize(400, 500)
        self.abilities_dict = abilities_dict
        self.init_ui()

    def init_ui(self):
        """
        Initializes window layout
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("Passive Abilities and Reactions")
        title.setStyleSheet("font-size: 16pt; color: #FFF;font-weight: bold;")
        layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        for timing, abilities in self.abilities_dict.items():
            if not abilities:
                continue

            content = PhaseWidget(abilities)
            scroll_layout.addWidget(AccordionSection(timing, content))

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

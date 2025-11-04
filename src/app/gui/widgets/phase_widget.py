from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .ability_card import AbilityCard


class PhaseWidget(QWidget):
    """
    Widget for displaying information for a phase, including the abilities
    """
    def __init__(self, abilities: list, parent=None):
        """
        Constructor
        :param abilities: list of Ability objects for which to construct ability cards
        :param parent: parent widget
        """
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 10, 0, 10)

        if not abilities:
            nothing_label = QLabel("Nothing to do in this phase.")
            nothing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nothing_label.setStyleSheet("color: #999; font-style: italic; font-size: 20pt;margin: 20px;")
            layout.addWidget(nothing_label)
        else:
            for ability in abilities:
                layout.addWidget(AbilityCard(ability))

            layout.addStretch()
        self.setLayout(layout)

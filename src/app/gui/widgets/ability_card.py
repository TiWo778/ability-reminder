from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy


class AbilityCard(QFrame):
    """
    Widget for an ability
    """
    def __init__(self, ability, parent=None):
        """
        Constructor
        :param ability: The ability to display
        :param parent: The parent widget
        """
        super().__init__(parent)
        self.ability = ability
        self.init_ui()

    def init_ui(self):
        """
        Initialize the widget layout
        """
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #403C3C;
                color: #FFFFFF;
                font-size: 14pt;
                border-radius: 8px;
                padding: 8px;
                margin-bottom: 6px;
            }
        """)
        layout = QVBoxLayout()

        name_label = QLabel(f"<b>{self.ability.name} "
                            f"<i>({self.ability.source})</i>"
                            f"{f" -- {self.ability.timing}" if self.ability.timing is not None else ""}</b>")
        desc_label = QLabel(f"{f"<b>Declare:</b> {f"<b><i>({self.ability.cost})</i></b> -- " if self.ability.cost else""}"
                               f"{self.ability.declare}<br><br>" if self.ability.declare else ""}"
                            f"<b>Effect:</b> {self.ability.effect}<br><br>"
                            f"{f"Keywords: <i>{self.ability.keywords}</i>" if self.ability.keywords else ""}")
        desc_label.setWordWrap(True)

        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        self.setLayout(layout)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea

from .accordion_widget import AccordionSection
from .phase_widget import PhaseWidget


class AllPhasesView(QWidget):
    """
    View for displaying all phases for which abilities exist
    """
    def __init__(self, parent=None):
        """
        Constructor
        :param parent: parent widget
        """
        super().__init__(parent)

        self.layout = QVBoxLayout()

        # Top bar
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")

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

        self.setLayout(self.layout)


    def show_all_phases(self, phase_dict: dict[str, list]):
        """
        Refresh view to show all phases.
        :param phase_dict: dict containing phase name and abilities
        """
        # Clear old widgets and reset status label
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for phase_name, abilities in phase_dict.items():
            if not abilities:
                continue

            section_content = PhaseWidget(abilities)
            accordion_section = AccordionSection(phase_name, section_content)

            self.scroll_layout.addWidget(accordion_section)
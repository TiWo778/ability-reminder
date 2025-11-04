from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolButton
from PyQt6.QtCore import Qt

class AccordionSection(QWidget):
    """
    Widget for a section of an accordion menu
    """
    def __init__(self, title, content_widget):
        """
        Constructor
        :param title: The title of the section
        :param content_widget: The widget to show in the section
        """
        super().__init__()

        # Toggle button
        self.toggle_button = QToolButton(text=title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.clicked.connect(self.toggle)

        self.toggle_button.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                color: #FFF;
                padding: 6px;
                text-align: left;
            }
        """)

        # Content area
        self.content = content_widget
        self.content.setVisible(False)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

    def toggle(self):
        """
        Toggles the content
        """
        expanded = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.content.setVisible(expanded)
        self.adjustSize()

from PyQt6.QtWidgets import QApplication, QStackedWidget

from .widgets import InitialView, GameView, AllPhasesView
from .controller import GUIController
from .theme import apply_dark_palette

class MainWindow(QStackedWidget):
    """
    Main window of the application
    """
    def __init__(self):
        super().__init__()
        self.initial_view = InitialView(self)
        self.game_view = GameView(self)
        self.all_phases_view = AllPhasesView(self)

        self.addWidget(self.initial_view)
        self.addWidget(self.game_view)
        self.addWidget(self.all_phases_view)

        self.setWindowTitle("Ability Reminders")
        self.setMinimumSize(1000, 600)
        self.show()


def main():
    """
    Entry point of the application
    :return:
    """
    app = QApplication([])
    app.setStyle("Fusion")
    apply_dark_palette(app)
    window = MainWindow()
    controller = GUIController(window)
    app.exec()

if __name__ == "__main__":
    main()

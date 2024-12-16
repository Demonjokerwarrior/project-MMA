import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class App(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.setWindowTitle("Open Terminal Example")
        self.setGeometry(100, 100, 300, 100)

        # Create button
        self.button = QPushButton('Open Terminal', self)
        self.button.clicked.connect(self.open_terminal)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def open_terminal(self):
        # Command to open terminal and run the command
        command = "gnome-terminal -- bash -c 'sudo su - restricted_user; exec bash'"

        # Execute the command
        subprocess.Popen(command, shell=True)

# Run the application
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())

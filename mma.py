import os
import sys
import subprocess
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QFileDialog, QLabel, QMessageBox, QTabWidget, QHBoxLayout, QListWidget, QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class FileSecureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure File Storage")
        self.setGeometry(300, 300, 800, 600)

        # Change the folder name to 'sec'
        self.secure_folder = "./sec"
        self.ensure_secure_folder()

        # Load or generate encryption key
        self.encryption_key_path = os.path.join(self.secure_folder, "encryption.key")
        self.load_or_generate_key()

        # Cipher for encryption and decryption
        self.cipher = Fernet(self.encryption_key)

        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tab 1: File Encryption
        self.tab_encrypt = QWidget()
        self.encrypt_layout = QVBoxLayout()
        self.tab_encrypt.setLayout(self.encrypt_layout)

        self.encrypt_label = QLabel("Choose a file to secure:")
        self.encrypt_label.setAlignment(Qt.AlignCenter)
        self.encrypt_layout.addWidget(self.encrypt_label)

        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.select_file)
        self.encrypt_layout.addWidget(self.select_button)

        self.secure_button = QPushButton("Secure File")
        self.secure_button.clicked.connect(self.secure_file)
        self.secure_button.setEnabled(False)
        self.encrypt_layout.addWidget(self.secure_button)

        self.tabs.addTab(self.tab_encrypt, "Secure a File")

        # Tab 2: View Secured Files
        self.tab_view = QWidget()
        self.view_layout = QHBoxLayout()
        self.tab_view.setLayout(self.view_layout)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.view_file)
        self.view_layout.addWidget(self.file_list)

        self.file_viewer_area = QScrollArea()
        self.file_viewer = QLabel()
        self.file_viewer.setAlignment(Qt.AlignCenter)
        self.file_viewer_area.setWidget(self.file_viewer)
        self.file_viewer_area.setWidgetResizable(True)
        self.view_layout.addWidget(self.file_viewer_area)

        self.open_terminal_button = QPushButton("Open Secure Folder in Terminal")
        self.open_terminal_button.clicked.connect(self.open_secure_folder_in_terminal)
        self.view_layout.addWidget(self.open_terminal_button)

        self.restricted_terminal_button = QPushButton("Open Restricted Terminal")
        self.restricted_terminal_button.clicked.connect(self.open_restricted_terminal)
        self.view_layout.addWidget(self.restricted_terminal_button)

        self.tabs.addTab(self.tab_view, "View Secured Files")

        # Initialize the file list
        self.update_file_list()

        # State
        self.selected_file = None

    def ensure_secure_folder(self):
        """Ensure the secure folder exists."""
        if not os.path.exists(self.secure_folder):
            os.makedirs(self.secure_folder)
            os.chmod(self.secure_folder, 0o700)

    def load_or_generate_key(self):
        """Load an existing key or generate a new one."""
        if os.path.exists(self.encryption_key_path):
            with open(self.encryption_key_path, "rb") as key_file:
                self.encryption_key = key_file.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(self.encryption_key_path, "wb") as key_file:
                key_file.write(self.encryption_key)

    def update_file_list(self):
        """Update the list of encrypted files in the secure folder."""
        self.file_list.clear()
        for file_name in os.listdir(self.secure_folder):
            if file_name.endswith(".enc"):
                self.file_list.addItem(file_name)

    def select_file(self):
        """Open a file dialog to select a file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "All Files (*);;Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;Text Files (*.txt)",
            options=options
        )
        if file_path:
            self.selected_file = file_path
            self.encrypt_label.setText(f"Selected File: {os.path.basename(file_path)}")
            self.secure_button.setEnabled(True)

    def secure_file(self):
        """Encrypt and store the file in the secure folder."""
        if not self.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select a file to secure.")
            return

        try:
            # Read the file and encrypt it
            with open(self.selected_file, "rb") as f:
                file_data = f.read()
            encrypted_data = self.cipher.encrypt(file_data)

            # Save the encrypted file in the secure folder
            encrypted_file_path = os.path.join(self.secure_folder, os.path.basename(self.selected_file) + ".enc")
            with open(encrypted_file_path, "wb") as f:
                f.write(encrypted_data)

            QMessageBox.information(self, "Success", f"File secured in: {self.secure_folder}")
            self.encrypt_label.setText("Choose a file to secure:")
            self.selected_file = None
            self.secure_button.setEnabled(False)

            # Update the file list
            self.update_file_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to secure file: {str(e)}")

    def open_secure_folder_in_terminal(self):
        """Open the secure folder in the terminal."""
        try:
            if os.name == "nt":  # For Windows
                subprocess.run(["start", "cmd", "/K", f"cd {self.secure_folder}"], shell=True)
            elif os.name == "posix":  # For Linux or macOS
                terminal = os.getenv("TERMINAL", "x-terminal-emulator") or "gnome-terminal"
                subprocess.Popen([terminal, "-e", f"bash -c 'cd \"{self.secure_folder}\"; exec bash'"])
            else:
                QMessageBox.warning(self, "Unsupported OS", "This feature is not supported on your operating system.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open terminal: {str(e)}")

    def open_restricted_terminal(self):
        """Open a restricted terminal as a different user."""
        try:
            if os.name == "posix":  # Linux or macOS
                terminal = os.getenv("TERMINAL", "x-terminal-emulator") or "gnome-terminal"
                command = "gnome-terminal -- bash -c 'sudo su - restricted_user; exec bash'"
                subprocess.Popen(command, shell=True)
            else:
                QMessageBox.warning(self, "Unsupported OS", "Restricted terminal is not supported on Windows.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open restricted terminal: {str(e)}")

    def view_file(self, item):
        """Decrypt and display the selected file in the viewer."""
        encrypted_file_path = os.path.join(self.secure_folder, item.text())
        try:
            with open(encrypted_file_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)

            # Determine if the file is an image
            file_name = item.text()
            if any(file_name.lower().endswith(ext) for ext in [".png.enc", ".jpg.enc", ".jpeg.enc", ".bmp.enc", ".gif.enc"]):
                # Save the image temporarily
                temp_image_path = os.path.join(self.secure_folder, "temp_image.png")
                with open(temp_image_path, "wb") as img_file:
                    img_file.write(decrypted_data)
                pixmap = QPixmap(temp_image_path)
                self.file_viewer.setPixmap(pixmap)
            else:
                # Display text or binary data
                self.file_viewer.setText(decrypted_data.decode("utf-8", errors="replace"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt file: {str(e)}")


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
window = FileSecureApp()
window.show()
sys.exit(app.exec_())

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QVBoxLayout, QWidget, QAction, QComboBox, QHBoxLayout, QMessageBox, QPushButton, QTabWidget, QCheckBox, QDialog, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QStandardPaths, Qt

class RipeBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ripe Browser")
        self.setGeometry(100, 100, 1000, 700)

        self.setup_ui()
        self.saved_credentials = []

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Toolbar
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)

        # Back button
        back_button = QAction(QIcon("left-arrow.png"), "Back", self)
        back_button.triggered.connect(self.on_back_triggered)
        self.toolbar.addAction(back_button)

        # Forward button
        forward_button = QAction(QIcon("right-arrow.png"), "Forward", self)
        forward_button.triggered.connect(self.on_forward_triggered)
        self.toolbar.addAction(forward_button)

        # Refresh button
        refresh_button = QAction(QIcon("refresh.png"), "Refresh", self)
        refresh_button.triggered.connect(self.on_refresh_triggered)
        self.toolbar.addAction(refresh_button)

        # Home button
        home_button = QAction(QIcon("home.png"), "Home", self)
        home_button.triggered.connect(self.go_home)
        self.toolbar.addAction(home_button)

        # Address bar and Go button
        address_layout = QHBoxLayout()
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate)
        self.address_bar.setPlaceholderText("Search or enter URL")
        address_layout.addWidget(self.address_bar)

        go_button = QPushButton("Go")
        go_button.clicked.connect(self.navigate)
        address_layout.addWidget(go_button)

        # Website selector
        self.website_selector = QComboBox()
        self.website_selector.addItems(["Google", "Discord", "Spotify", "Amazon", "YouTube"])
        self.website_selector.currentIndexChanged.connect(self.navigate_to_selected_website)
        address_layout.addWidget(self.website_selector)

        # Add address bar and website selector to toolbar
        self.toolbar.addWidget(self.address_bar)
        self.toolbar.addWidget(go_button)
        self.toolbar.addWidget(self.website_selector)

        self.add_tab_button = QPushButton("+")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.toolbar.addWidget(self.add_tab_button)

        # Save Password checkbox
        self.save_password_checkbox = QCheckBox("Save Password")
        self.save_password_checkbox.stateChanged.connect(self.save_password_state_changed)
        self.toolbar.addWidget(self.save_password_checkbox)

        # History button
        history_button = QPushButton("History")
        history_button.clicked.connect(self.show_history_dialog)
        self.toolbar.addWidget(history_button)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

        # Add initial tab
        self.add_new_tab()

    def add_new_tab(self):
        browser = QWebEngineView()
        browser.page().profile().downloadRequested.connect(self.download_requested)
        browser.load(QUrl("https://www.google.com"))
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def navigate(self):
        text = self.address_bar.text()
        url = QUrl(text)
        if not url.isValid() or url.scheme() == '':
            if ' ' in text:
                search_url = QUrl('https://www.google.com/search?q=' + '+'.join(text.split()))
            else:
                search_url = QUrl('https://www.google.com/search?q=' + text)
            if self.tabs.currentWidget() is not None:
                self.tabs.currentWidget().setUrl(search_url)
        else:
            if self.tabs.currentWidget() is not None:
                self.tabs.currentWidget().setUrl(url)

    def navigate_to_selected_website(self, index):
        websites = {
            "Google": "https://www.google.com",
            "Discord": "https://discord.com",
            "Spotify": "https://www.spotify.com",
            "Amazon": "https://www.amazon.com",
            "YouTube": "https://www.youtube.com"
        }
        website = self.website_selector.itemText(index)
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().setUrl(QUrl(websites.get(website)))

    def download_requested(self, download):
        try:
            # Get the user's downloads directory
            downloads_dir = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
            # Construct the full path for the downloaded file
            full_path = os.path.join(downloads_dir, download.url().fileName())
            
            # Check if the file already exists
            if os.path.exists(full_path):
                # If the file already exists, append a number to the file name to avoid overwriting
                base_name, extension = os.path.splitext(download.url().fileName())
                counter = 1
                while os.path.exists(os.path.join(downloads_dir, f"{base_name} ({counter}){extension}")):
                    counter += 1
                full_path = os.path.join(downloads_dir, f"{base_name} ({counter}){extension}")

            # Set the download path
            download.setPath(full_path)
            download.accept()

            # Open the downloaded file with the default handler
            if sys.platform.startswith('win'):
                os.startfile(full_path)
            else:
                QMessageBox.information(self, "Download Started", f"Downloading {download.url().fileName()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during download: {str(e)}")

    def go_home(self):
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def on_back_triggered(self):
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().back()

    def on_forward_triggered(self):
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().forward()

    def on_refresh_triggered(self):
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().reload()

    def save_password_state_changed(self, state):
        if state == Qt.Checked:
            # Call a function to prompt for password and save it
            self.show_password_manager_dialog()

    def show_password_manager_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Password Manager")
        layout = QVBoxLayout()

        email_label = QLabel("Email:")
        self.email_edit = QLineEdit()
        layout.addWidget(email_label)
        layout.addWidget(self.email_edit)

        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_credentials)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_credentials(self):
        email = self.email_edit.text()
        password = self.password_edit.text()
        if email and password:
            self.saved_credentials.append((email, password))
            QMessageBox.information(self, "Success", "Credentials saved successfully. You are trusting RipeBrowser.")

    def show_history_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Password History")
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for email, password in self.saved_credentials:
            item = QListWidgetItem(f"Email: {email}, Password: {password}")
            list_widget.addItem(item)

        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RipeBrowser()
    window.show()
    sys.exit(app.exec_())

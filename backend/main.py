import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QFontDatabase, QFont, QResizeEvent
from PyQt6.QtCore import QDate, QSize, Qt, QTimer

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumSize(QSize(990, 822))

        try:
            # Assuming GUI folder is in the same directory as the script
            # or the script is run from a context where ./GUI is valid.
            uic.loadUi("../GUI/pcg-main-screen.ui", self)
        except FileNotFoundError:
            print("Error: payment_cert_generator.ui not found in ./GUI/ folder.")
            error_label = QtWidgets.QLabel("Error: UI File not found in ./GUI/", self)
            self.setCentralWidget(error_label)
            self.setWindowTitle("Error")
            self.setMinimumSize(QSize(300,100))
            return # Important to return if UI can't be loaded
        except Exception as e:
            print(f"Error loading UI file: {e}")
            error_label = QtWidgets.QLabel(f"Error loading UI file: {e}", self)
            error_label.setWordWrap(True)
            self.setCentralWidget(error_label)
            self.setWindowTitle("UI Load Error")
            self.setMinimumSize(QSize(400,150))
            return # Important to return if UI can't be loaded

        # --- Configure ScrollArea Scrollbars ---
        if hasattr(self, 'scrollArea'):
            self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            print("Warning: scrollArea not found in UI.")

        # --- Setup for Dynamic Card Layout ---
        self.featuresContainer = self.findChild(QtWidgets.QWidget, "featuresContainer")
        self.featureCard1 = self.findChild(QtWidgets.QFrame, "featureCard1")
        self.featureCard2 = self.findChild(QtWidgets.QFrame, "featureCard2")
        self.featureCard3 = self.findChild(QtWidgets.QFrame, "featureCard3")

        # Initialize attributes to ensure they exist even if components are not found
        self.cards = []
        self.horizontal_cards_layout = None
        self.vertical_cards_layout = QtWidgets.QVBoxLayout() # Create instance early
        self.current_layout_is_horizontal = True # Default assumption

        if not all([self.featuresContainer, self.featureCard1, self.featureCard2, self.featureCard3]):
            print("Error: Not all feature card components found in the UI. Dynamic layout may fail.")
            # self.cards will remain empty, and layout switching won't occur
        else:
            self.cards = [self.featureCard1, self.featureCard2, self.featureCard3]

            # Store the initial horizontal layout from the .ui file
            self.horizontal_cards_layout = self.featuresContainer.layout()
            if not isinstance(self.horizontal_cards_layout, QtWidgets.QHBoxLayout):
                print("Warning: Initial layout of featuresContainer is not QHBoxLayout. Creating a new one for horizontal.")
                # This is a fallback, ideally the .ui file's layout is QHBoxLayout.
                self.horizontal_cards_layout = QtWidgets.QHBoxLayout()
                # Manually add cards if we had to create it (less ideal, but makes it work)
                for card_widget in self.cards:
                    self.horizontal_cards_layout.addWidget(card_widget)
                self.featuresContainer.setLayout(self.horizontal_cards_layout) # Apply the new one

            # Configure the vertical layout instance (already created)
            if self.horizontal_cards_layout: # Copy properties if original layout exists and is valid
                try: # Check if horizontal_cards_layout is a valid layout object
                    margins = self.horizontal_cards_layout.contentsMargins()
                    self.vertical_cards_layout.setContentsMargins(margins)
                    self.vertical_cards_layout.setSpacing(self.horizontal_cards_layout.spacing())
                except AttributeError: # If self.horizontal_cards_layout was None or not a layout
                    print("Warning: Could not copy properties from horizontal_cards_layout.")
                    self.vertical_cards_layout.setContentsMargins(0,0,0,0)
                    self.vertical_cards_layout.setSpacing(30) # Default spacing
            else: # Default properties if original layout was missing
                self.vertical_cards_layout.setContentsMargins(0,0,0,0)
                self.vertical_cards_layout.setSpacing(30) # Default spacing

            self.current_layout_is_horizontal = True # Assume it starts horizontal as per .ui
            self.card_layout_threshold_width = 750  # Pixels: Width to switch layout

        # --- Dynamic Content ---
        current_year = QDate.currentDate().year()
        if hasattr(self, 'footerLabel'):
            self.footerLabel.setText(f"© {current_year} Payment Certificates Generator")

        # --- Connect Signals ---
        if hasattr(self, 'viewProjectsButton'):
            self.viewProjectsButton.clicked.connect(self.view_projects)
        if hasattr(self, 'createProjectButton'):
            self.createProjectButton.clicked.connect(self.create_new_project)

        # Initial layout update after a short delay to ensure window is shown and sized
        if self.cards: # Only if cards were successfully found and dynamic layout is intended
            QTimer.singleShot(50, self.update_features_layout)

        self.show()

    def _transfer_widgets_to_layout(self, target_layout: QtWidgets.QLayout):
        """Helper to move cards to the target_layout."""
        if not self.cards: # Safety check
            return
        for card in self.cards:
            # addWidget will re-parent the widget if it's already in another layout
            target_layout.addWidget(card)

    def update_features_layout(self):
        """Switches the layout of feature cards based on container width."""
        if not self.cards or not self.featuresContainer or not self.horizontal_cards_layout or not self.vertical_cards_layout:
            # Essential components for dynamic layout are missing
            return

        container_width = self.scrollArea.viewport().width() if self.scrollArea else self.featuresContainer.width()

        if container_width < self.card_layout_threshold_width:
            if self.current_layout_is_horizontal:
                print(f"Width {container_width} < {self.card_layout_threshold_width}: Switching to Vertical")
                # Ensure vertical layout is empty before adding widgets
                while self.vertical_cards_layout.count():
                    item = self.vertical_cards_layout.takeAt(0)
                    if item.widget(): # If it's a widget, it's now orphaned, which is fine before re-adding
                        pass # No need to delete, addWidget will re-parent
                self._transfer_widgets_to_layout(self.vertical_cards_layout)
                self.featuresContainer.setLayout(self.vertical_cards_layout)
                self.current_layout_is_horizontal = False
        else: # Width is >= threshold
            if not self.current_layout_is_horizontal:
                print(f"Width {container_width} >= {self.card_layout_threshold_width}: Switching to Horizontal")
                # Ensure horizontal layout is empty before adding widgets
                while self.horizontal_cards_layout.count():
                    item = self.horizontal_cards_layout.takeAt(0)
                    if item.widget():
                        pass
                self._transfer_widgets_to_layout(self.horizontal_cards_layout)
                self.featuresContainer.setLayout(self.horizontal_cards_layout)
                self.current_layout_is_horizontal = True

        self.featuresContainer.updateGeometry() # Ask the container to re-evaluate its geometry

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events to update card layout."""
        super().resizeEvent(event)
        if self.cards: # Only if dynamic layout is intended
            self.update_features_layout()

    def view_projects(self):
        print("View Projects button clicked")
        QtWidgets.QMessageBox.information(self, "Action", "View Projects clicked!")

    def create_new_project(self):
        print("Create New Project button clicked")
        QtWidgets.QMessageBox.information(self, "Action", "Create New Project clicked!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Font loading (optional) ...
    # Example:
    # font_files = ["fonts/Inter-Regular.ttf", "fonts/Inter-SemiBold.ttf", "fonts/Inter-Bold.ttf"]
    # for font_file in font_files:
    #     font_id = QFontDatabase.addApplicationFont(font_file)
    #     if font_id == -1:
    #         print(f"Warning: Could not load font: {font_file}")
    #
    # families = QFontDatabase().families()
    # if "Inter" in families:
    #     default_font = QFont("Inter")
    #     app.setFont(default_font)
    #     print("Inter font loaded and potentially set as application default.")
    # else:
    #     print("Inter font not available. Stylesheet will fall back to 'sans-serif'.")
    window = MainWindow()
    sys.exit(app.exec())

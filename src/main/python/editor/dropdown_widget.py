from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox


class DropdownWidget(QWidget):
    def __init__(self, label_text, options, parent=None):
        super().__init__(parent)

        # Layout for the dropdown widget
        layout = QVBoxLayout()

        # Label for the dropdown
        self.label = QLabel(label_text)
        layout.addWidget(self.label)

        # Dropdown (QComboBox)
        self.dropdown = QComboBox()
        self.dropdown.addItems(options)
        layout.addWidget(self.dropdown)

        # Set the layout
        self.setLayout(layout)

    def get_selected_option(self):
        """Returns the currently selected option."""
        return self.dropdown.currentText()

    def set_selected_option(self, option):
        """Sets the dropdown to the specified option."""
        index = self.dropdown.findText(option)
        if index != -1:
            self.dropdown.setCurrentIndex(index)
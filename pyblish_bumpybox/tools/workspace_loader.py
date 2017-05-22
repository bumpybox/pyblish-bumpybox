from Qt import QtWidgets, QtCore

import pyblish.util


class Window(QtWidgets.QDialog):
    """ Tool for loading in output instances.

    Usage:
        Instantiate the win, add some items and the application functionality.

        >> win = Window()
        >> def application_function(instance):
               print instance
        >> win.application_function = application_function
        >> win.show()
    """

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Workspace Loader")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Layout
        body = QtWidgets.QVBoxLayout(self)

        self.list = QtWidgets.QListWidget()
        body.addWidget(self.list)

        self.load_button = QtWidgets.QPushButton("Load")
        body.addWidget(self.load_button)

        # Collect items
        context = pyblish.util.collect()
        self.items = []
        for instance in context:
            if "output" in instance.data["families"]:
                self.list.addItem(instance.data["label"])
                self.items.append(instance)

        # Functionality
        self.load_button.clicked.connect(self.load)

    # Standin function for application
    def application_function(self, instance):

        raise ValueError("Application function is not implemented")

    def load(self):
        for item in self.list.selectedItems():
            instance = self.items[self.list.row(item)]
            self.application_function(instance)

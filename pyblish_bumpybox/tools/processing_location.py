from Qt import QtWidgets, QtCore


class Window(QtWidgets.QDialog):
    """ Tool for setting up remote instances.

    Usage:
        Instantiate the win, add some items and the application functionality.

        >> win = Window()
        >> win.add_item("bob")
        >> win.add_item("paul", remote=True)
        >> def application_function(selection, localProcessing):
               location = "remotely"
               if localProcessing:
                   location = "locally"
               print "These items: {0} will be processed {1}.".format(
                   selection, location
               )
        >> win.application_function = application_function
        >> win.show()
    """

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Processing Location")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Layout
        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(QtWidgets.QLabel("Local Processing"), 0, 0)
        self.local_list = QtWidgets.QListWidget()
        layout.addWidget(self.local_list, 1, 0)

        self.remote_to_local_button = QtWidgets.QPushButton("<")
        layout.addWidget(self.remote_to_local_button, 1, 1)
        self.local_to_remote_button = QtWidgets.QPushButton(">")
        layout.addWidget(self.local_to_remote_button, 1, 2)

        layout.addWidget(QtWidgets.QLabel("Remote Processing"), 0, 3)
        self.remote_list = QtWidgets.QListWidget()
        layout.addWidget(self.remote_list, 1, 3)

        # Functionality
        self.local_to_remote_button.clicked.connect(lambda: self.switch(False))
        self.remote_to_local_button.clicked.connect(lambda: self.switch(True))

    # Standin function for application
    def application_function(self, selection, localProcessing):

        raise ValueError("Application function is not implemented")

    def switch(self, localProcessing):

        # Set source and target widget
        source_widget = self.local_list
        target_widget = self.remote_list

        if localProcessing:
            source_widget = self.remote_list
            target_widget = self.local_list

        # Switch items from source to target
        selection = source_widget.selectedItems()
        results = []
        for item in selection:
            results.append(item.text())
            target_widget.addItem(item.text())
            source_widget.takeItem(source_widget.row(item))

        # Run application functionality
        self.application_function(results, localProcessing)

    def add_item(self, name, remote=False):

        widget = self.local_list
        if remote:
            widget = self.remote_list

        widget.addItem(name)

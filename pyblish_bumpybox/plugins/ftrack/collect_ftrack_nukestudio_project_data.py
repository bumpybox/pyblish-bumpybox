from PySide import QtCore, QtGui

import hiero

import pyblish.api
import ftrack_api


class CollectFtrackHieroNukeStudioProjectData(pyblish.api.ContextPlugin):
    """Collect the Ftrack project data.

    Its assumed at tag is applied to the active sequence with these keys:

    name - The project"s code.
    full_name - The project"s full name.
    project_schema_id - The id of the workflow schema applied to the project.

    Optional keys:

    root - The project"s root.
    disk_id - The id of the disk applied to the project.
    """

    order = pyblish.api.CollectorOrder
    label = "Ftrack Project Data"
    hosts = ["nukestudio"]

    def process(self, context):

        data = context.data.get("ftrackProjectData", {})
        data.update(self.get_project_data(context))
        self.log.info("Found project data: {0}".format(data))
        context.data["ftrackProjectData"] = data

    def get_project_data(self, context):

        data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Get project name from existing tag
        for tag in hiero.ui.activeSequence().tags():
            if tag.name().lower() != "ftrack.project":
                continue

            for key in data:
                if ("tag." + key) in tag.metadata().keys():
                    data[key] = tag.metadata().value(key)

        return data


class Window(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Ftrack Project Data")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setLayout(QtGui.QGridLayout())
        self.session = ftrack_api.Session()

        self.data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Collect projects
        self.projects = [
            {
                "name": "new_project",
                "full_name": "New Project",
                "project_schema_id": "",
                "root": "",
                "disk_id": ""
            }
        ]
        for project in self.session.query("Project where status is active"):
            self.projects.append(project)

        # Project selection
        self.layout().addWidget(QtGui.QLabel("Project:"), 0, 0)
        self.projects_combo = QtGui.QComboBox()
        for project in self.projects:
            self.projects_combo.addItem(project["full_name"])
        self.layout().addWidget(self.projects_combo, 0, 1)

        self.projects_combo.currentIndexChanged.connect(
            self.on_project_combo_changed
        )

        # Naming inputs
        self.layout().addWidget(QtGui.QLabel("Full name:"), 1, 0)
        self.fullname_lineedit = QtGui.QLineEdit(self.projects[0]["full_name"])
        self.layout().addWidget(self.fullname_lineedit, 1, 1)

        self.fullname_lineedit.textChanged.connect(self.on_fullname_lineedit)

        self.layout().addWidget(QtGui.QLabel("Name:"), 2, 0)
        self.name_lineedit = QtGui.QLineEdit(self.projects[0]["name"])
        self.name_lineedit.setEnabled(False)
        self.layout().addWidget(self.name_lineedit, 2, 1)

        # Project schema input
        self.schemas = []
        for schema in self.session.query("ProjectSchema"):
            self.schemas.append(schema)
        self.projects[0]["project_schema_id"] = self.schemas[0]["id"]

        self.layout().addWidget(QtGui.QLabel("Schema:"), 3, 0)
        self.schemas_combo = QtGui.QComboBox()
        for schema in self.schemas:
            self.schemas_combo.addItem(schema["name"])
        self.layout().addWidget(self.schemas_combo, 3, 1)

        self.schemas_combo.currentIndexChanged.connect(
            self.on_schemas_combo_changed
        )

        # Root input
        self.layout().addWidget(QtGui.QLabel("Root:"), 4, 0)
        self.root_lineedit = QtGui.QLineEdit(self.projects[0]["root"])
        self.layout().addWidget(self.root_lineedit, 4, 1)

        self.root_lineedit.textChanged.connect(self.on_root_lineedit)

        # Disk input
        self.disks = []
        for disk in self.session.query("Disk"):
            self.disks.append(disk)
        self.projects[0]["disk_id"] = self.disks[0]["id"]

        self.layout().addWidget(QtGui.QLabel("Disk:"), 5, 0)
        self.disks_combo = QtGui.QComboBox()
        for disk in self.disks:
            self.disks_combo.addItem(disk["name"])
        self.layout().addWidget(self.disks_combo, 5, 1)

        self.disks_combo.currentIndexChanged.connect(
            self.on_disks_combo_changed
        )

        # Submit button
        self.submit_button = QtGui.QPushButton("Submit")
        self.layout().addWidget(self.submit_button, 6, 0, 1, 2)

        self.submit_button.clicked.connect(self.on_submit_button)

    def on_project_combo_changed(self, index):

        # Enable/Disable UI elements
        if index == 0:
            self.fullname_lineedit.setEnabled(True)
            self.schemas_combo.setEnabled(True)
            self.root_lineedit.setEnabled(True)
            self.disks_combo.setEnabled(True)
        else:
            self.fullname_lineedit.setEnabled(False)
            self.schemas_combo.setEnabled(False)
            self.root_lineedit.setEnabled(False)
            self.disks_combo.setEnabled(False)

        # Update UI elements
        data = self.projects[index]
        self.fullname_lineedit.setText(data["full_name"])
        self.name_lineedit.setText(data["name"])

        for schema in self.schemas:
            if schema["id"] == data["project_schema_id"]:
                self.schemas_combo.setCurrentIndex(
                    self.schemas.index(schema)
                )

        self.root_lineedit.setText(data["root"])

        for disk in self.disks:
            if disk["id"] == data["disk_id"]:
                self.disks_combo.setCurrentIndex(
                    self.disks.index(disk)
                )

    def on_fullname_lineedit(self, text):
        if self.projects_combo.currentIndex() == 0:
            self.projects[0]["full_name"] = text
            name = text.replace(" ", "_").lower()
            self.name_lineedit.setText(name)
            self.projects[0]["name"] = name

    def on_schemas_combo_changed(self, index):
        if self.projects_combo.currentIndex() == 0:
            self.projects[0]["project_schema_id"] = self.schemas[
                self.schemas_combo.currentIndex()
            ]["id"]

    def on_root_lineedit(self, text):
        if self.projects_combo.currentIndex() == 0:
            self.projects[0]["root"] = text

    def on_disks_combo_changed(self, index):
        if self.projects_combo.currentIndex() == 0:
            self.projects[0]["disk_id"] = self.disks[
                self.disks_combo.currentIndex()
            ]["id"]

    def on_submit_button(self):

        project = self.projects[self.projects_combo.currentIndex()]
        self.data = {
            "name": str(project["name"]),
            "full_name": str(project["full_name"]),
            "project_schema_id": str(project["project_schema_id"]),
            "root": str(project["root"]),
            "disk_id": str(project["disk_id"])
        }
        self.close()


class CollectFtrackNukeStudioProjectUI(pyblish.api.ContextPlugin):
    """Collects the Ftrack project data with a user friendly UI.

    Only run if tag on sequence does not exist.
    """

    order = CollectFtrackHieroNukeStudioProjectData.order - 0.1
    label = "Ftrack Project UI"
    hosts = ["nukestudio"]

    def process(self, context):

        # Get project name from existing tag
        show_gui = True
        for tag in hiero.ui.activeSequence().tags():
            if tag.name().lower() == "ftrack.project":
                show_gui = False

        if show_gui:
            win = Window()
            win.exec_()
            self.log.info(
                "Creating tag on sequence with data: {0}".format(win.data)
            )

            tag = hiero.core.Tag("ftrack.project")
            metadata = tag.metadata()
            for key, value in win.data.iteritems():
                metadata.setValue("tag." + key, value)
            hiero.ui.activeSequence().addTag(tag)

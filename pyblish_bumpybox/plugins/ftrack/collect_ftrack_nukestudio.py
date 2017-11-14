from PySide import QtCore, QtGui

import hiero

import pyblish.api
import ftrack_api


class Window(QtGui.QDialog):
    """Dialog for selecting project data."""

    def __init__(self, parent=None, data=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Ftrack Project Data")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setLayout(QtGui.QGridLayout())
        self.session = ftrack_api.Session()

        self.data = data

        # Collect projects
        self.projects = [data]
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


class CollectFtrackNukeStudioProjectData(pyblish.api.ContextPlugin):
    """Collect the Ftrack project data.

    Offset to get collected Ftrack data from pyblish-ftrack.

    Its assumed at tag is applied to the active sequence with these keys:

    name - The project"s code.
    full_name - The project"s full name.
    project_schema_id - The id of the workflow schema applied to the project.

    Optional keys:

    root - The project"s root.
    disk_id - The id of the disk applied to the project.
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Ftrack Project Data"
    hosts = ["nukestudio"]

    def process(self, context):

        data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Get project data from launched task.
        task = context.data["ftrackTask"]
        if task:
            project = task["project"]
            data.update(
                {
                    "name": project["name"],
                    "full_name": project["full_name"],
                    "project_schema_id": project["project_schema_id"],
                    "root": project["root"],
                    "disk_id": project["disk_id"]
                }
            )

        # Get data from active sequence tag.
        data.update(self.get_sequence_data(context))

        # Show project input dialog if any data is missing.
        show_gui = False
        for key, value in data.iteritems():
            if key not in ["name", "full_name", "project_schema_id"]:
                continue

            if not value:
                show_gui = True

        if show_gui:
            win = Window(data=data)
            win.exec_()
            self.log.info(
                "Creating tag on sequence with data: {0}".format(win.data)
            )

        # Persist data
        self.log.info("Found project data: {0}".format(data))
        context.data["ftrackProjectData"] = data

    def get_sequence_data(self, context):

        data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Get project name from existing tag
        for tag in hiero.ui.activeSequence().tags():
            if ("tag.ftrack") not in tag.metadata().keys():
                continue

            for key in data:
                if ("tag." + key) in tag.metadata().keys():
                    data[key] = tag.metadata().value(key)

        # Remove any empty key/value pairs.
        results = {}
        for key, value in data.iteritems():
            if value:
                results[key] = value

        return results


class CollectFtrackNukeStudioEntities(pyblish.api.ContextPlugin):
    """Collect the Ftrack project data.

    Offset to get collected "trackItem" instances.
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Ftrack Entities"
    hosts = ["nukestudio"]

    def get_instance(self, instances, label, family):
        for instance in instances:
            if (instance.data["label"] == label and
               instance.data["family"] == family):
                return instance
        return None

    def process(self, context):

        instances = []
        for parent in context:
            if "trackItem" != parent.data["family"]:
                continue

            item = parent.data["item"]
            split = item.name().split("--")

            shot = None
            parent_instance = parent
            if "--" in item.name():
                # Get/Create sequence
                if len(split) == 2:
                    name = split[0]
                    family = "trackItem.ftrackEntity.sequence"
                    sequence = self.get_instance(instances, name, family)
                    if sequence is None:
                        sequence = context.create_instance(
                            name=name,
                            label=name,
                            parent=parent,
                            family=family,
                            families=["trackItem", "ftrackEntity", "sequence"]
                        )
                        instances.append(sequence)

                    parent_instance = sequence

                # Get/Create episode and sequence
                if len(split) == 3:
                    name = split[0]
                    family = "trackItem.ftrackEntity.episode"
                    episode = self.get_instance(instances, name, family)
                    if episode is None:
                        episode = context.create_instance(
                            name=name,
                            label=name,
                            parent=parent,
                            family=family,
                            families=["trackItem", "ftrackEntity", "episode"]
                        )
                        instances.append(episode)

                    label = "/".join([split[0], split[1]])
                    family = "trackItem.ftrackEntity.episode"
                    sequence = self.get_instance(instances, label, family)
                    if sequence is None:
                        sequence = context.create_instance(
                            name=split[1],
                            parent=episode,
                            label=label,
                            family="trackItem.ftrackEntity.sequence",
                            families=["trackItem", "ftrackEntity", "sequence"]
                        )
                        instances.append(sequence)

                    parent_instance = sequence

            # Create Ftrack shot instance
            label = "/".join(split)
            family = "trackItem.ftrackEntity.shot"
            shot = self.get_instance(instances, label, family)
            if shot is None:
                shot = context.create_instance(name=split[-1])
                shot.data["label"] = "/".join(split)
                shot.data["family"] = "trackItem.ftrackEntity.shot"
                shot.data["families"] = ["trackItem", "ftrackEntity", "shot"]
                shot.data["parent"] = parent_instance
                parent.data["shotInstance"] = shot
                shot.data["item"] = parent.data["item"]

                shot.data["handles"] = parent.data["handles"]
                shot.data["fstart"] = parent.data["startFrame"]
                shot.data["fend"] = parent.data["endFrame"]

                sequence = parent.data["item"].parent().parent()
                shot.data["fps"] = sequence.framerate().toFloat()

                if parent.data["item"].reformatState().type() == "disabled":
                    media_source = parent.data["item"].source().mediaSource()
                    shot.data["width"] = media_source.width()
                    shot.data["height"] = media_source.height()
                else:
                    shot.data["width"] = sequence.format().width()
                    shot.data["height"] = sequence.format().height()

                instances.append(shot)

                # Create Ftrack task instances.
                for tag in parent.data["item"].tags():
                    if ("tag.ftrack") not in tag.metadata().keys():
                        continue

                    metadata = tag.metadata().dict()

                    if "tag.type" in metadata.keys():
                        # Expect "task_name" instead of "name", because "name"
                        # can't be edited by the user.
                        name = metadata.get(
                            "tag.task_name", metadata["tag.type"].lower()
                        )
                        task = context.create_instance(name=name)
                        label = shot.data["label"] + "/" + name
                        task.data["label"] = label
                        task.data["type"] = metadata["tag.type"]
                        task.data["family"] = "trackItem.ftrackEntity.task"
                        task.data["families"] = [
                            "trackItem", "ftrackEntity", "task"
                        ]
                        task.data["parent"] = shot

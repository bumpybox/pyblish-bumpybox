import os
import tempfile

import pyblish.api
import ftrack
import pymel

import ftrack_locations


class BumpyboxMayaVersionUpScene(pyblish.api.Action):

    label = "Version Up"
    icon = "wrench"
    on = "all"

    def process(self, context, plugin):

        file_path = os.path.join(
            tempfile.gettempdir(), "pyblish-bumpybox.mb"
        )
        pymel.core.system.saveAs(file_path)

        task = ftrack.Task(context.data["ftrackData"]["Task"]["id"])

        asset = task.getParent().createAsset(
            task.getName(),
            "scene",
            task=task
        )

        location = ftrack_locations.get_old_location()
        components = asset.getVersions()[-1].getComponents(location=location)
        version = asset.createVersion(taskid=task.getId())

        # Recreating all components on new version
        for component in components:
            version.createComponent(
                name=component.getName(),
                path=component.getFilesystemPath(),
                location=location
            )

        asset.publish()
        path = version.getComponent(
            name=pyblish.api.current_host(), location=location
        ).getFilesystemPath()

        pymel.core.system.openFile(path, force=True)


class BumpyboxMayaRepairScene(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        file_path = os.path.join(
            tempfile.gettempdir(), "pyblish-bumpybox.mb"
        )
        pymel.core.system.saveAs(file_path)

        ftrack_data = context.data["ftrackData"]
        task = ftrack.Task(ftrack_data["Task"]["id"])
        component_name = pyblish.api.current_host()
        location = ftrack_locations.get_old_location()

        asset = task.getParent().createAsset(
            task.getName(),
            "scene",
            task=task
        )

        version = None
        component = None
        if asset.getVersions():
            version = asset.getVersions()[-1]
            try:
                component = version.getComponent(name=component_name)
            except:
                version = asset.createVersion(taskid=task.getId())
        else:
            version = asset.createVersion(taskid=task.getId())

        if not component:
            component = version.createComponent(
                name=component_name, path=file_path,
                location=location
            )
        component = location.getComponent(component.getId())

        asset.publish()

        if os.path.exists(component.getFilesystemPath()):
            pymel.core.system.openFile(
                component.getFilesystemPath(), force=True
            )
        else:
            version = asset.createVersion(taskid=task.getId())
            component = version.createComponent(
                name=component_name, path=file_path,
                location=location
            )
            component = location.getComponent(component.getId())
            asset.publish()
            pymel.core.system.openFile(
                component.getFilesystemPath(), force=True
            )


class BumpyboxMayaValidateScene(pyblish.api.ContextPlugin):

    order = pyblish.api.ValidatorOrder
    label = "Scene"
    actions = [BumpyboxMayaRepairScene, BumpyboxMayaVersionUpScene]
    hosts = ["maya"]

    def process(self, context):

        ftrack_data = context.data["ftrackData"]
        task = ftrack.Task(ftrack_data["Task"]["id"])
        component_name = pyblish.api.current_host()

        assets = task.getAssets(
            assetTypes=["scene"],
            names=[ftrack_data["Task"]["name"]],
            componentNames=[component_name]
        )

        if not assets:
            raise ValueError("No existing Ftrack asset found.")

        component = assets[0].getVersions()[-1].getComponent(
            name=component_name
        )

        current = context.data["currentFile"]
        expected = component.getFilesystemPath()
        msg = "Scene path is not correct. Current: \"{0}\" Expected: \"{1}\""
        assert expected == current, msg.format(current, expected)

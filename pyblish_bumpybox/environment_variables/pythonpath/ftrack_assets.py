import os

import maya.cmds as mc
import pymel.core

import ftrack
from ftrack_connect_maya.connector.mayaassets import GenericAsset
from ftrack_connect.connector import FTAssetHandlerInstance, HelpFunctions


# Define ftrack Assets
class CacheAsset(GenericAsset):

    def importAsset(self, iAObj=None):
        if os.path.splitext(iAObj.filePath)[1] not in [".abc"]:
            raise ValueError("Uncognized file type.")

        namespace = iAObj.componentName

        if iAObj.options["mayaNamespace"] and iAObj.options["nameSpaceStr"]:
            namespace = iAObj.options["nameSpaceStr"]

        if not iAObj.options["mayaNamespace"]:
            namespace = ":"

        new_nodes = mc.file(
            iAObj.filePath % 1,
            reference=True,
            namespace=namespace,
            returnNewNodes=True
        )
        self.newData = set(new_nodes)
        self.oldData = set()

        if iAObj.options["mayaTimeline"]:
            for node in new_nodes:
                if mc.nodeType(node) == "AlembicNode":
                    start_frame = mc.getAttr(node + ".startFrame")
                    end_frame = mc.getAttr(node + ".endFrame")
                    mc.playbackOptions(
                        minTime=start_frame,
                        animationStartTime=start_frame,
                        maxTime=end_frame,
                        animationEndTime=end_frame
                    )

        self.linkToFtrackNode(iAObj)

    def changeVersion(self, iAObj=None, applicationObject=None):
        result = GenericAsset.changeVersion(self, iAObj, applicationObject)
        return result

    @staticmethod
    def importOptions():
        xml = """
        <tab name="Options">
            <row name="{0}" accepts="maya">
                <option type="checkbox" name="mayaNamespace" value="True"/>
            </row>
            <row name="Custom Namespace" accepts="maya">
                <option type="string" name="nameSpaceStr" value=""/>
            </row>
            <row name="Change Timeline" accepts="maya">
                <option type="checkbox" name="mayaTimeline" value="False"/>
            </row>
        </tab>
        """
        return xml.format("Add Namespace\n(Component name by default)")


class ImageSequenceAsset(GenericAsset):

    def getStartEndFrames(self, component, iAObj):
        """Return start and end from *iAObj*."""

        if component.getSystemType() == "sequence":
            # Find out frame start and end from members if component
            # system type is sequence.
            members = component.getMembers(location=None)
            frames = [int(member.getName()) for member in members]
            start = min(frames)
            end = max(frames)
        else:
            start, end = HelpFunctions.getFileSequenceStartEnd(iAObj.filePath)

        return start, end

    def importAsset(self, iAObj=None):
        component = ftrack.Component(iAObj.componentId)
        start, end = self.getStartEndFrames(component, iAObj)
        new_nodes = []

        # Image plane
        if iAObj.options["importType"] == "Image Plane":

            first_image = iAObj.filePath % start

            # Getting camera
            new_camera = False
            if iAObj.options["attachCamera"]:
                cam = pymel.core.ls(selection=True)[0]
            else:
                cam = pymel.core.createNode("camera")
                new_camera = True

            if iAObj.options["renameCamera"]:
                asset_name = component.getVersion().getAsset().getName()
                pymel.core.rename(cam.getTransform(), asset_name)

            if new_camera:
                new_nodes.extend([
                    cam.name(),
                    cam.getTransform().name()
                ])

            if iAObj.options["resolutionGate"]:
                cam.displayResolution.set(1)

            cam.farClipPlane.set(iAObj.options["imagePlaneDepth"] * 10)

            # Setup scene
            if iAObj.options["changeResolution"]:
                defaultResolution = pymel.core.PyNode("defaultResolution")
                task = ftrack.Task(os.environ["FTRACK_TASKID"])

                width = task.getParent().get("width")
                defaultResolution.width.set(width)
                height = task.getParent().get("height")
                defaultResolution.height.set(height)

            # Create image plane
            visibility = True
            option = "Hidden from other cameras"
            if iAObj.options["imagePlaneVisibility"] == option:
                visibility = False

            image_plane_transform, image_plane_shape = pymel.core.imagePlane(
                camera=cam, fileName=first_image, showInAllViews=visibility
            )
            image_plane_shape.useFrameExtension.set(1)
            image_plane_shape.depth.set(iAObj.options["imagePlaneDepth"])

            new_nodes.extend([
                image_plane_transform.name(),
                image_plane_shape.name()
            ])

            # Create ground plane
            if iAObj.options["createGround"]:
                ground_transform, ground_shape = pymel.core.polyPlane(
                    name="ground",
                    height=iAObj.options["groundSize"],
                    width=iAObj.options["groundSize"]
                )

                ground_shader = pymel.core.shadingNode(
                    "lambert", asShader=True
                )
                visiblity = iAObj.options["groundVisibility"] / 100
                ground_shader.transparency.set(visiblity, visiblity, visiblity)
                pymel.core.select(ground_transform)
                pymel.core.hyperShade(assign=ground_shader.name())

                new_nodes.extend([
                    ground_transform.name(),
                    ground_shape.name(),
                    ground_shader.name()
                ])

        self.newData = set(new_nodes)
        self.oldData = set()

        self.linkToFtrackNode(iAObj)

    def changeVersion(self, iAObj=None, applicationObject=None):
        raise ValueError("Change version not implemented yet.")

    @staticmethod
    def importOptions():
        xml = """
        <tab name="Options">
            <row name="Import Type" accepts="maya">
                <option type="radio" name="importType">
                    <optionitem name="Image Plane" value="True"/>
                    <optionitem name="File Node"/>
                </option>
            </row>
            <row name="Image Plane Settings" accepts="maya">
            </row>
            <row name="Attach to selected camera" accepts="maya">
                <option type="checkbox" name="attachCamera" value="False"/>
            </row>
            <row name="Rename camera\n(Asset name by default)" accepts="maya">
                <option type="checkbox" name="renameCamera" value="True"/>
            </row>
            <row name="Image plane depth" accepts="maya">
                <option type="float" name="imagePlaneDepth" value="10000"/>
            </row>
            <row name="Visibility" accepts="maya">
                <option type="radio" name="imagePlaneVisibility">
                    <optionitem name="Hidden from other cameras" value="True"/>
                    <optionitem name="Show in other cameras"/>
                </option>
            </row>
            <row name="Resolution Gate" accepts="maya">
                <option type="checkbox" name="resolutionGate" value="True"/>
            </row>
            <row name="Change Resolution" accepts="maya">
                <option type="checkbox" name="changeResolution" value="True"/>
            </row>
            <row name="Create Ground Plane" accepts="maya">
                <option type="checkbox" name="createGround" value="False"/>
            </row>
            <row name="Ground Plane Size\n(Squared 150x150)" accepts="maya">
                <option type="float" name="groundSize" value="150"/>
            </row>
            <row name="Ground Plane Visibility (%)" accepts="maya">
                <option type="float" name="groundVisibility" value="50"/>
            </row>
        </tab>
        """
        return xml


class MovieAsset(GenericAsset):

    def getStartEndFrames(self, component, iAObj):
        """Return start and end from *iAObj*."""

        if component.getSystemType() == "sequence":
            # Find out frame start and end from members if component
            # system type is sequence.
            members = component.getMembers(location=None)
            frames = [int(member.getName()) for member in members]
            start = min(frames)
            end = max(frames)
        else:
            start, end = HelpFunctions.getFileSequenceStartEnd(iAObj.filePath)

        return start, end

    def importAsset(self, iAObj=None):
        component = ftrack.Component(iAObj.componentId)
        start, end = self.getStartEndFrames(component, iAObj)
        new_nodes = []

        # Image plane
        if iAObj.options["importType"] == "Image Plane":

            movie_path = iAObj.filePath % start

            # Getting camera
            new_camera = False
            if iAObj.options["attachCamera"]:
                cam = pymel.core.ls(selection=True)[0]
            else:
                cam = pymel.core.createNode("camera")
                new_camera = True

            if iAObj.options["renameCamera"]:
                asset_name = component.getVersion().getAsset().getName()
                pymel.core.rename(cam.getTransform(), asset_name)

            if new_camera:
                new_nodes.extend([
                    cam.name(),
                    cam.getTransform().name()
                ])

            if iAObj.options["resolutionGate"]:
                cam.displayResolution.set(1)

            cam.farClipPlane.set(iAObj.options["imagePlaneDepth"] * 10)

            # Setup scene
            if iAObj.options["changeResolution"]:
                defaultResolution = pymel.core.PyNode("defaultResolution")
                task = ftrack.Task(os.environ["FTRACK_TASKID"])

                width = task.getParent().get("width")
                defaultResolution.width.set(width)
                height = task.getParent().get("height")
                defaultResolution.height.set(height)

            # Create image plane
            visibility = True
            option = "Hidden from other cameras"
            if iAObj.options["imagePlaneVisibility"] == option:
                visibility = False

            image_plane_transform, image_plane_shape = pymel.core.imagePlane(
                camera=cam, showInAllViews=visibility
            )
            image_plane_shape.depth.set(iAObj.options["imagePlaneDepth"])
            # Need to get "type" by string, because its a method as well.
            pymel.core.Attribute(image_plane_shape + ".type").set(2)
            image_plane_shape.imageName.set(movie_path)
            image_plane_shape.useFrameExtension.set(1)

            new_nodes.extend([
                image_plane_transform.name(),
                image_plane_shape.name()
            ])

            # Create ground plane
            if iAObj.options["createGround"]:
                ground_transform, ground_shape = pymel.core.polyPlane(
                    name="ground",
                    height=iAObj.options["groundSize"],
                    width=iAObj.options["groundSize"]
                )

                ground_shader = pymel.core.shadingNode(
                    "lambert", asShader=True
                )
                visiblity = iAObj.options["groundVisibility"] / 100
                ground_shader.transparency.set(visiblity, visiblity, visiblity)
                pymel.core.select(ground_transform)
                pymel.core.hyperShade(assign=ground_shader.name())

                new_nodes.extend([
                    ground_transform.name(),
                    ground_shape.name(),
                    ground_shader.name()
                ])

        self.newData = set(new_nodes)
        self.oldData = set()

        self.linkToFtrackNode(iAObj)

    def changeVersion(self, iAObj=None, applicationObject=None):
        raise ValueError("Change version not implemented yet.")

    @staticmethod
    def importOptions():
        xml = """
        <tab name="Options">
            <row name="Import Type" accepts="maya">
                <option type="radio" name="importType">
                    <optionitem name="Image Plane" value="True"/>
                    <optionitem name="File Node"/>
                </option>
            </row>
            <row name="Image Plane Settings" accepts="maya">
            </row>
            <row name="Attach to selected camera" accepts="maya">
                <option type="checkbox" name="attachCamera" value="False"/>
            </row>
            <row name="Rename camera\n(Asset name by default)" accepts="maya">
                <option type="checkbox" name="renameCamera" value="True"/>
            </row>
            <row name="Image plane depth" accepts="maya">
                <option type="float" name="imagePlaneDepth" value="10000"/>
            </row>
            <row name="Visibility" accepts="maya">
                <option type="radio" name="imagePlaneVisibility">
                    <optionitem name="Hidden from other cameras" value="True"/>
                    <optionitem name="Show in other cameras"/>
                </option>
            </row>
            <row name="Resolution Gate" accepts="maya">
                <option type="checkbox" name="resolutionGate" value="True"/>
            </row>
            <row name="Change Resolution" accepts="maya">
                <option type="checkbox" name="changeResolution" value="True"/>
            </row>
            <row name="Create Ground Plane" accepts="maya">
                <option type="checkbox" name="createGround" value="False"/>
            </row>
            <row name="Ground Plane Size\n(Squared 150x150)" accepts="maya">
                <option type="float" name="groundSize" value="150"/>
            </row>
            <row name="Ground Plane Visibility (%)" accepts="maya">
                <option type="float" name="groundVisibility" value="50"/>
            </row>
        </tab>
        """
        return xml


def register_assets():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name="cache", cls=CacheAsset)
    assetHandler.registerAssetType(name="img", cls=ImageSequenceAsset)
    assetHandler.registerAssetType(name="mov", cls=MovieAsset)

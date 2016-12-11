import maya.cmds as mc

from ftrack_connect_maya.connector.mayaassets import GenericAsset
from ftrack_connect.connector import FTAssetHandlerInstance


# Define ftrack Assets
class CacheAsset(GenericAsset):

    def importAsset(self, iAObj=None):
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


def register_assets():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name='cache', cls=CacheAsset)

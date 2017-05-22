import nuke

import ftrack
from ftrack_connect_nuke.connector.nukeassets import GenericAsset
from ftrack_connect.connector import FTAssetHandlerInstance, HelpFunctions


# Define ftrack Assets
class SceneAsset(GenericAsset):

    def importAsset(self, iAObj=None):

        start, end = HelpFunctions.getFileSequenceStartEnd(iAObj.filePath)

        nuke.nodePaste(iAObj.filePath % start)

        if iAObj.options["importSettings"]:

            component = ftrack.Component(iAObj.componentId)
            parent = component.getVersion().getAsset().getParent()

            # Setup fps
            nuke.root()['fps'].setValue(parent.get('fps'))

            # Setup frame range
            nuke.root()['first_frame'].setValue(parent.get('fstart'))
            nuke.root()['last_frame'].setValue(parent.get('fend'))

            # Setup resolution
            width = parent.get("width")
            height = parent.get("height")
            fmt = None
            for f in nuke.formats():
                if f.width() == width and f.height() == height:
                    fmt = f

            if fmt:
                nuke.root()['format'].setValue(fmt.name())

        return

    @staticmethod
    def importOptions():
        xml = """
        <tab name="Options">
            <row name="Import Settings" accepts="nuke">
                <option type="checkbox" name="importSettings" value="False"/>
            </row>
        </tab>
        """
        return xml


def register_assets():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name="scene", cls=SceneAsset)

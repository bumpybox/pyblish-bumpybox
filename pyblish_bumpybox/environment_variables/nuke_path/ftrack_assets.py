import nuke

from ftrack_connect_nuke.connector.nukeassets import GenericAsset
from ftrack_connect.connector import FTAssetHandlerInstance, HelpFunctions


# Define ftrack Assets
class SceneAsset(GenericAsset):

    def importAsset(self, iAObj=None):

        start, end = HelpFunctions.getFileSequenceStartEnd(iAObj.filePath)

        nuke.nodePaste(iAObj.filePath % start)

        return


def register_assets():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name="scene", cls=SceneAsset)

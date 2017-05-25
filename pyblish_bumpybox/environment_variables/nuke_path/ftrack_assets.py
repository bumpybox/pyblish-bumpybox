import nuke

import ftrack
import ftrack_api
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


class LUTAsset(GenericAsset):

    def importAsset(self, iAObj=None):

        session = ftrack_api.Session()
        component = session.get("Component", iAObj.componentId)

        # Collect component data and Nuke display name.
        path = component["component_locations"][0]["resource_identifier"]
        colorspace_in = component["metadata"]["colorspace_in"]
        colorspace_out = component["metadata"]["colorspace_out"]

        display_name = ""
        for item in component["version"]["task"]["link"][:]:
            display_name += session.get(item['type'], item['id'])["name"] + "/"
        display_name = display_name[:-1]
        display_name += ": {0} > {1}".format(colorspace_in, colorspace_out)

        # Register the lut.
        values_syntax = {
            "linear": "linear",
            "srgb": "sRGB",
            "rec709": "rec709",
            "cineon": "Cineon",
            "gamma1.8": "Gamma1.8",
            "gamma2.2": "Gamma2.2",
            "gamma2.4": "Gamma2.4",
            "panalog": "Panalog",
            "redlog": "REDLog",
            "viperlog": "ViperLog",
            "alexav3logc": "AlexaV3LogC",
            "ploglin": "PLogLin",
            "slog": "SLog",
            "slog1": "SLog1",
            "slog2": "SLog2",
            "slog3": "SLog3",
            "clog": "CLog",
            "protune": "Protune",
            "redspace": "REDSpace"
        }

        node_data = "vfield_file {0} colorspaceIn {1} colorspaceOut {2}"

        if iAObj.options["importType"] == "ViewerProcess":
            nuke.ViewerProcess.register(
                display_name,
                nuke.createNode,
                (
                    "Vectorfield",
                    node_data.format(
                        path.replace("\\", "/"),
                        values_syntax[colorspace_in],
                        values_syntax[colorspace_out]
                    )
                )
            )
        elif iAObj.options["importType"] == "Vectorfield":
            nuke.nodes.Vectorfield(
                vfield_file=path.replace("\\", "/"),
                colorspaceIn=values_syntax[colorspace_in],
                colorspaceOut=values_syntax[colorspace_out]
            )
        else:
            raise ValueError("Unrecognized import type.")

        return

    @staticmethod
    def importOptions():
        xml = """
        <tab name="Options">
            <row name="Import As" accepts="nuke">
                <option type="radio" name="importType">
                    <optionitem name="ViewerProcess" value="True"/>
                    <optionitem name="Vectorfield"/>
                </option>
            </row>
        </tab>
        """
        return xml


def register_assets():
    assetHandler = FTAssetHandlerInstance.instance()
    assetHandler.registerAssetType(name="scene", cls=SceneAsset)
    assetHandler.registerAssetType(name="lut", cls=LUTAsset)

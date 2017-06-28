import pyblish.api


class ExtractFtrackNukeGizmo(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack gizmo component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Gizmo"
    families = ["gizmo"]

    def process(self, instance):

        instance.data["assettype_short"] = "nuke_gizmo"


class ExtractFtrackNukeLUT(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack lut component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack LUT"
    families = ["lut"]

    def process(self, instance):

        instance.data["component_name"] = "main"
        instance.data["assettype_short"] = "lut"

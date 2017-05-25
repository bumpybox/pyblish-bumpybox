import os
import itertools

import pyblish.api
import ftrack_locations


class BumpyboxCollectLUT(pyblish.api.ContextPlugin):
    """ Collecting the lut files in current directory. """

    label = "LUT"
    order = pyblish.api.CollectorOrder + 0.4
    hosts = ["ftrack"]

    def process(self, context):

        current_file = context.data("currentFile")

        # Skip if current file is not a directory
        if not os.path.isdir(current_file):
            return

        # Traverse directory and collect collections from json files.
        file_types = [".3dl", ".csp", ".cube", ".vf", ".lut"]
        lut_files = []
        gizmos = []
        for root, dirs, files in os.walk(current_file):
            for f in files:
                if os.path.splitext(f)[1] in file_types:
                    lut_files.append(os.path.join(root, f))
                if os.path.splitext(f)[1] == ".gizmo":
                    gizmos.append(os.path.join(root, f))

        colorspaces = [
            "linear",
            "srgb",
            "rec709",
            "cineon",
            "gamma1.8",
            "gamma2.2",
            "gamma2.4",
            "panalog",
            "redlog",
            "viperlog",
            "alexav3logc",
            "ploglin",
            "slog",
            "slog1",
            "slog2",
            "slog3",
            "clog",
            "protune",
            "redspace"
        ]
        for f in lut_files:
            found_colorspaces = []
            for colorspace in colorspaces:
                if colorspace in f.lower():
                    found_colorspaces.append(colorspace)

            combinations = []
            for combination in itertools.combinations(found_colorspaces, 2):
                combinations.append(list(combination))
                combinations.append(list(reversed(combination)))

            for combination in combinations:
                name = "{0} > {1}".format(combination[0], combination[1])
                instance = context.create_instance(name=name)

                label = "{0} ({1})".format(name, os.path.basename(f))
                instance.data["label"] = label

                instance.data["families"] = ["lut"]
                instance.data["publish"] = False

                # Get location
                session = context.data["ftrackSession"]
                location = ftrack_locations.get_new_location(session)

                # Add component
                components = []
                components.append({
                    "assettype_data": {"short": "lut"},
                    "assetversion_data": {
                        "version": 1
                    },
                    "component_data": {
                        "name": "main"
                    },
                    "component_path": f,
                    "component_overwrite": True,
                    "component_location": location
                })
                instance.data["ftrackComponentsList"] = components

        for f in gizmos:
            instance = context.create_instance(name=os.path.basename(f))

            instance.data["families"] = ["lut"]
            instance.data["publish"] = False

            # Get location
            session = context.data["ftrackSession"]
            location = ftrack_locations.get_new_location(session)

            # Add component
            components = []
            components.append({
                "assettype_data": {"short": "lut"},
                "assetversion_data": {
                    "version": 1
                },
                "component_data": {
                    "name": "main"
                },
                "component_path": f,
                "component_overwrite": True,
                "component_location": location
            })
            instance.data["ftrackComponentsList"] = components

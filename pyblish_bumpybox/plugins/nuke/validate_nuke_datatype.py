import nuke

import pyblish.api


class ValidateNukeDatatype(pyblish.api.InstancePlugin):
    """Validate output datatype matches with input."""

    order = pyblish.api.ValidatorOrder
    families = ["write"]
    label = "Datatype"
    optional = True
    targets = ["default", "process"]

    def process(self, instance):
        upstream_nodes = []

        def upstream(node):
            dependencies = nuke.dependencies(
                [node], nuke.INPUTS | nuke.HIDDEN_INPUTS | nuke.EXPRESSIONS
            )
            upstream_nodes.extend(dependencies)
            for dependency in dependencies:
                upstream(dependency)

        upstream(instance[0])

        float_bit_nodes = []
        for node in upstream_nodes:
            if node.Class() != "Read":
                continue

            bitsperchannel = node.metadata()["input/bitsperchannel"]
            if node.Class() == "Read" and bitsperchannel.startswith("32"):
                float_bit_nodes.append(node)

        if float_bit_nodes:
            msg = (
                "There are 32-bit inputs upstream: {0}. Consider changing the"
                " output to 32-bit to preserve data.".format(float_bit_nodes)
            )
            assert instance[0]["datatype"].value().startswith("32"), msg

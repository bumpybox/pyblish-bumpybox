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

        float_bit_nodes = []
        for node in self.upstream(instance[0]):
            bitsperchannel = node.metadata()["input/bitsperchannel"]
            if node.Class() == "Read" and bitsperchannel.startswith("32"):
                float_bit_nodes.append(node)

        if float_bit_nodes:
            msg = (
                "There are 32-bit inputs upstream: {0}. Consider changing the"
                " output to 32-bit to preserve data.".format(float_bit_nodes)
            )
            assert instance[0]["datatype"].value().startswith("32"), msg

    def upstream(self, startNode=None, nodes=None):
        if nodes is None:
            nodes = set([])
        node = startNode
        if not node:
            return
        else:
            upNodes = nuke.dependencies(node)
            for n in upNodes:
                nodes.add(n)
                if n.Class() == "Group":
                    group = nuke.toNode(n.name())
                    with group:
                        outputs = nuke.allNodes('Output')
                        for o in outputs:
                            self.upstream(o, nodes=nodes)
                self.upstream(n, nodes=nodes)
        return list(nodes)

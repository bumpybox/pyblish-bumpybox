import pyblish.api
import pymel


class CollectSets(pyblish.api.ContextPlugin):
    """ Collects all sets in scene """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        for s in pymel.core.ls(type="objectSet"):

            if str(s) in ["defaultLightSet", "defaultObjectSet",
                          "initialParticleSE", "initialShadingGroup"]:
                continue

            for fmt in ["mb", "ma", "abc"]:

                instance = context.create_instance(name=str(s))
                family = "cache.local." + fmt
                instance.data["family"] = family
                instance.data["families"] = ["cache.*", "cache.local.*"]
                instance.data["set"] = s

                instance.data["publish"] = False
                try:
                    attr = getattr(s, family.replace(".", "_"))
                    instance.data["publish"] = attr.get()
                except:
                    msg = "Attribute \"{0}\"".format(family.replace(".", "_"))
                    msg += " does not exists. Defaulting to inactive publish"
                    self.log.info(msg)

                for m in s.members():
                    instance.add(m)

import pyblish.api


class LatestVersion(pyblish.api.Action):

    families = ['read']

    def process(self, context):

        for instance in context:
            if instance.data['family'] in self.families:
                self.log.info(instance)
                self.log.info(instance.data['__published__'])

    def version_get(self, string, prefix, suffix = None):

      if string is None:
        raise ValueError, "Empty version string - no match"

      regex = "[/_.]"+prefix+"\d+"
      matches = re.findall(regex, string, re.IGNORECASE)
      if not len(matches):
        msg = "No \"_"+prefix+"#\" found in \""+string+"\""
        raise ValueError, msg
      return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())

    def getFirst(self, versions, path, name):
        for v in reversed(versions):
            for f in os.listdir(os.path.join(path, v)):
                if f == name:
                    return v

class UpdateReadNodes(pyblish.api.Plugin):

    actions = [LatestVersion]

    def process(self, context):
        pass

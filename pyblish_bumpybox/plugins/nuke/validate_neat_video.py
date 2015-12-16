import pyblish.api
import nuke


class ValidateNeatVideo(pyblish.api.Validator):
    """Fails publish if Neat Video node is present in scene"""

    families = ['deadline.render']
    label = 'Neat Video'

    def process(self, instance):
        for node in nuke.allNodes():
            if node.Class().lower().startswith('ofxcom.absoft.neatvideo'):
                if not node['disable'].getValue():
                    msg = 'Neat Video is active in file: "%s"' % node.name()
                    raise ValueError(msg)

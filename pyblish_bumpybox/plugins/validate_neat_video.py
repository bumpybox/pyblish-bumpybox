import os

import pyblish.api
import nuke


@pyblish.api.log
class ValidateNeatVideo(pyblish.api.Validator):
    """Fails publish if Neat Video node is present in scene"""

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Neat Video'

    def process(self, instance):
        for node in nuke.allNodes():
            if node.Class() == 'OFXcom.absoft.neatvideo_v2':
                if not node['disable'].getValue():
                    msg = 'Neat Video is active in file: "%s"' % node.name()
                    raise ValueError(msg)

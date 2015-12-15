import os
import re
import tempfile

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils


class ExtractEXR(pyblish.api.Validator):

    families = ['nuke']
    label = 'Transcode to EXR'

    def process(self, instance):

        item = instance[0]
        file_path = item.source().mediaSource().fileinfos()[0].filename()
        fps = item.sequence().framerate().toFloat()
        first_frame = int(item.sourceIn() + 1)
        last_frame = int(item.sourceOut() + 1)

        instance.data['nukeWriter'] = hiero.core.nuke.ScriptWriter()

        root_node = hiero.core.nuke.RootNode(first_frame, last_frame)
        instance.data['nukeWriter'].addNode(root_node)

        read_node = hiero.core.nuke.ReadNode(file_path,
                                width=item.parent().parent().format().width(),
                                height=item.parent().parent().format().height(),
                                firstFrame=first_frame, lastFrame=last_frame)
        read_node.setKnob('colorspace', item.sourceMediaColourTransform())
        instance.data['nukeWriter'].addNode(read_node)

        write_path = utils.get_path(instance, 'exr', self.log, sequence=True)
        write_node = hiero.core.nuke.WriteNode(write_path, inputNode=read_node)
        write_node.setKnob('file_type', 'exr')
        instance.data['nukeWriter'].addNode(write_node)

        script_path = os.path.join(tempfile.gettempdir(), str(instance) + '.nk')
        instance.data['nukeWriter'].writeToDisk(script_path)

        # adding deadline data
        job_data = {'Group': 'nuke_9','Pool': 'medium', 'Plugin': 'Nuke',
                    'OutputFilename0': write_path, 'ChunkSize': 10,
                    'Frames': '{0}-{1}'.format(first_frame, last_frame)}

        plugin_data = {'NukeX': False, 'Version': '9.0',
                        'EnforceRenderOrder': True, 'SceneFile': ''}

        data = {'job': job_data, 'plugin': plugin_data,
                'auxiliaryFiles': [script_path]}
        instance.set_data('deadlineData', value=data)

        #assert False, 'stop'

import os

import nuke
import pyblish.api


@pyblish.api.log
class CollectDeadlineWriteNodes(pyblish.api.Collector):
    """Selects all write nodes"""

    def process(self, context):

        # storing plugin data
        plugin_data = {'EnforceRenderOrder': True}

        plugin_data['NukeX'] = nuke.env['nukex']

        plugin_data['Version'] = nuke.NUKE_VERSION_STRING.split('v')[0]

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() == 'Write' and not node['disable'].getValue():
                instance = context.create_instance(name=node.name())
                instance.set_data('family', value='deadline.render')

                output = node['file'].getValue()

                # setting job data
                job_data = {}
                if instance.has_data('deadlineData'):
                    job_data = instance.data('deadlineData')['job'].copy()

                # output_file = os.path.basename(output)
                output_file = output

                if '%' in output_file:
                    padding = int(output_file.split('%')[1][0:2])
                    padding_string = '%0{0}d'.format(padding)
                    tmp = '#' * padding
                    output_file = output_file.replace(padding_string, tmp)

                job_data['OutputFilename0'] = output_file

                #instance.set_data('deadlineJobData', value=job_data)

                # frame range
                start_frame = int(nuke.root()['first_frame'].getValue())
                end_frame = int(nuke.root()['last_frame'].getValue())
                if node['use_limit'].getValue():
                    start_frame = int(node['first'].getValue())
                    end_frame = int(node['last'].getValue())

                frames = '%s-%s\n' % (start_frame, end_frame)
                instance.set_data('deadlineFrames', value=frames)

                # setting plugin data
                plugin_data = plugin_data.copy()
                plugin_data['WriteNode'] = node.name()

                #instance.set_data('deadlinePluginData', value=plugin_data)
                data = {'job': job_data, 'plugin': plugin_data}
                instance.set_data('deadlineData', value=data)

                # adding ftrack data to activate processing
                instance.set_data('ftrackComponents', value={})
                instance.set_data('ftrackAssetType', value='img')

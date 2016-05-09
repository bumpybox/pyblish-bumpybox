import os

import pyblish.api
import pyblish_standalone
import ftrack


class ExtractLevelSplit(pyblish.api.InstancePlugin):

    label = 'Deadline'
    families = ['render']
    order = pyblish.api.ExtractorOrder - 0.1

    def process(self, instance):
        job_data = {}
        job_data['Name'] = str(instance)
        job_data['Frames'] = '%s-%s' % (instance.data('start'),
                                        instance.data('end'))
        job_data['ChunkSize'] = 25
        job_data['Group'] = 'celaction'
        job_data['Pool'] = 'medium'
        job_data['Plugin'] = 'CelAction'

        # get output filename
        ftrack_data = instance.context.data('ftrackData')
        task = ftrack.Task(ftrack_data['Task']['id'])

        path = [ftrack_data['Project']['root']]
        path.append('renders')
        path.append('img_sequences')
        for p in reversed(task.getParents()[:-1]):
            path.append(p.getName())

        task_name = task.getName().replace(' ', '_').lower()
        path.append(task_name)

        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)
        path.append(version_string)
        path.append(str(instance))

        filename = [task.getParent().getName(), task_name, version_string]
        filename = '.'.join(filename)
        filename = filename + '_####.png'
        path.append(filename)

        output_path = os.path.join(*path).replace('\\', '/')
        job_data['OutputFilename0'] = output_path

        # plugin data
        plugin_data = {}

        path = os.path.dirname(pyblish_standalone.kwargs['path'][0])
        filename = os.path.basename(pyblish_standalone.kwargs['path'][0])
        args = '<QUOTE>%s<QUOTE>' % os.path.join(path, 'publish', filename)
        args += ' -a'

        if instance.has_data('levelSplit'):
            args += ' -l'

        args += ' -s <STARTFRAME>'
        args += ' -e <ENDFRAME>'
        args += ' -d <QUOTE>%s<QUOTE>' % os.path.dirname(output_path)
        args += ' -x %s' % instance.data('x')
        args += ' -y %s' % instance.data('y')
        args += ' -r <QUOTE>%s<QUOTE>' % output_path.replace('_####', '')
        args += ' -= AbsoluteFrameNumber=on -= PadDigits=4'
        args += ' -= ClearAttachment=on'

        plugin_data['Arguments'] = args

        plugin_data['StartupDirectory'] = ''

        # adding to instance
        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)

        # creating output path
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # ftrack data
        path = output_path.replace('####', '%04d')
        components = {str(instance): {'path': path}}
        instance.set_data('ftrackComponents', value=components)

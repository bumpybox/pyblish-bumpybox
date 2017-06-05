import os

import pyblish.api
import ftrack


class ExtractTVPaintDeadline(pyblish.api.Extractor):

    label = 'Deadline'
    families = ['render']
    order = pyblish.api.Extractor.order - 0.1

    def process(self, instance, context):

        job_data = {}
        job_data['Name'] = instance.data["name"]

        ftrack_data = instance.context.data('ftrackData')

        job_data['ChunkSize'] = 50
        appVersion = context.data('kwargs')['data']['applicationVersion']
        appVersion = appVersion.split('.')[0]
        job_data['Group'] = 'tvpaint_%s' % appVersion
        job_data['Pool'] = 'medium'
        job_data['Plugin'] = 'TVPaint'

        # get output filename
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
        path.append(instance.data["name"])

        filename = [task.getParent().getName(), task_name, version_string]
        filename = '.'.join(filename)
        filename = filename + '.####.png'
        path.append(filename)

        output_path = os.path.join(*path).replace('\\', '/')
        job_data['OutputFilename0'] = output_path

        job_data['Frames'] = '1'

        # plugin data
        plugin_data = {}

        plugin_data['SceneFile'] = context.data('kwargs')['data']['scene']
        plugin_data['Version'] = appVersion
        plugin_data['OutputFormat'] = 'PNG'
        plugin_data['OutputFile'] = output_path.replace('.####', '.0001')
        plugin_data['JobModeBox'] = 'Single Layer'
        plugin_data['Build'] = 'None'
        plugin_data['Build0'] = 'None'
        plugin_data['Build1'] = '32bit'
        plugin_data['Build2'] = '64bit'
        plugin_data['LayerName'] = instance.data["name"]
        plugin_data['UseCameraBox'] = False
        plugin_data['AlphaSaveModeBox'] = 'PreMultiply'

        # adding to instance
        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)

        # creating output path
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # ftrack data
        path = output_path.replace('####', '%04d')
        components = {instance.data["name"]: {'path': path}}
        instance.set_data('ftrackComponents', value=components)

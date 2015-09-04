import os

import pyblish.api
import ftrack


class ExtractDeadline(pyblish.api.Extractor):

    label = 'Render Farm'
    families = ['render']
    order = pyblish.api.Extractor.order - 0.1
    optional = True

    def process(self, instance, context):

        # check if its a movie
        movie_check = False
        if os.path.splitext(instance.data('path'))[1] == '.mov':
            movie_check = True

        job_data = {}
        job_data['Name'] = str(instance)
        job_data['Frames'] = '%s-%s' % (instance.data('start'),
                                                        instance.data('end'))
        job_data['ChunkSize'] = 10
        if movie_check:
            job_data['ChunkSize'] = 1000000
        job_data['Group'] = 'ae_cc_2015'
        job_data['Pool'] = 'medium'
        job_data['Plugin'] = 'AfterEffects'

        # get output filename
        ftrack_data = instance.context.data('ftrackData')
        task = ftrack.Task(ftrack_data['Task']['id'])

        path = [ftrack_data['Project']['root']]
        path.append('renders')
        if movie_check:
            path.append('movies')
        else:
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

        if not movie_check:
            filename += '_####'

        filename += os.path.splitext(instance.data('path'))[1]
        path.append(filename)

        output_path = os.path.join(*path).replace('\\', '/')
        job_data['OutputFilename0'] = output_path

        # plugin data
        plugin_data = {}

        plugin_data['SceneFile'] = context.data('currentFile')
        plugin_data['Comp'] = str(instance)
        plugin_data['Output'] = output_path.replace('####', '[####]')
        v = context.data('environmentArgs')['version'][0][0][0:4]
        plugin_data['Version'] = v

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

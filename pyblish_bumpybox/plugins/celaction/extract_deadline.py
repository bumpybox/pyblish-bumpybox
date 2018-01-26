from pyblish import api


class ExtractDeadline(api.ContextPlugin):

    label = 'Deadline'
    families = ['render']
    order = api.ExtractorOrder

    def process(self, instance):
        import os

        import pyblish_standalone
        import pipeline_schema

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        job_data['Name'] = instance.data["name"]
        job_data['Frames'] = '%s-%s' % (instance.data('start'),
                                        instance.data('end'))
        job_data['ChunkSize'] = 10
        job_data['Group'] = 'celaction'
        job_data['Pool'] = 'medium'
        job_data['Plugin'] = 'CelAction'

        name = os.path.basename(instance.context.data["currentFile"])
        name = os.path.splitext(name)[0] + " - " + instance.data["name"]
        job_data["Name"] = name

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')

        # get output filename
        data = pipeline_schema.get_data()
        data['extension'] = 'png'
        data['output_type'] = 'img'
        data['name'] = instance.data["name"]
        data['version'] = version
        output_path = pipeline_schema.get_path('output_sequence', data)
        job_data['OutputFilename0'] = output_path.replace('%04d', '####')

        # plugin data
        render_name_separator = '.'
        path = os.path.dirname(pyblish_standalone.kwargs['path'][0])
        filename = os.path.basename(pyblish_standalone.kwargs['path'][0])
        args = '<QUOTE>%s<QUOTE>' % os.path.join(path, 'publish', filename)
        args += ' -a'

        # not rendering a movie if outputting levels
        # also changing the RenderNameSeparator for better naming
        # ei. "levels.v001_1sky.0001.png" > "levels_1sky.v001.0001.png"
        if instance.has_data('levelSplit'):
            args += ' -l'
            instance.data.pop("movie", None)

            version_string = pipeline_schema.get_path('version', data)
            output_path = output_path.replace('.' + version_string, '')
            job_data['OutputFilename0'] = output_path.replace('%04d', '####')

            render_name_separator = '.%s.' % version_string

        args += ' -s <STARTFRAME>'
        args += ' -e <ENDFRAME>'
        args += ' -d <QUOTE>%s<QUOTE>' % os.path.dirname(output_path)
        args += ' -x %s' % instance.data('x')
        args += ' -y %s' % instance.data('y')
        args += ' -r <QUOTE>%s<QUOTE>' % output_path.replace('.%04d', '')
        args += ' -= AbsoluteFrameNumber=on -= PadDigits=4'
        args += ' -= ClearAttachment=on'

        plugin_data['Arguments'] = args

        plugin_data['StartupDirectory'] = ''
        plugin_data['RenderNameSeparator'] = render_name_separator

        # adding to instance
        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)

        # creating output path
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # ftrack data
        components = {instance.data["name"]: {'path': output_path}}
        instance.set_data('ftrackComponents', value=components)

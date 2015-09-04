import os
import subprocess

import pyblish.api


class ExtractRender(pyblish.api.Extractor):

    label = 'Render Local'
    families = ['render']
    order = pyblish.api.Extractor.order - 0.1
    optional = True

    def process(self, instance, context):

        args = [r'C:\Program Files\Adobe\Adobe After Effects CC 2015\Support Files\aerender.exe']
        args.append('-project')
        args.append(context.data('environmentArgs')['scene'][0][0])
        args.append('-comp')
        args.append(str(instance))

        subprocess.call(args)

        output_path = context.data('environmentArgs')['render'][0][1]
        name = context.data('environmentArgs')['render'][0][0]
        component = {name: {'path': output_path}}
        instance.set_data('ftrackComponents', value=component)

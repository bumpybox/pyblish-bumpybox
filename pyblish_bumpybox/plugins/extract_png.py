import os

import pyblish.api
import pyseq
import shutil
import ftrack


class ExtractPNG(pyblish.api.Extractor):
    """
    """

    families = ['png']
    optional = True
    hosts = ['ftrack']
    label = 'Copy PNG'

    def process(self, context, instance):

        ftrack_data = context.data('ftrackData')

        root = ftrack_data['Project']['root']

        task = ftrack.Task(ftrack_data['Task']['id'])
        parent_name = task.getParent().getName()

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        version_name = 'v' + str(context.data('version')).zfill(3)

        # making directories
        path = os.path.join(root, 'renders', 'img_sequences', parent_name,
                                        task_name, version_name, str(instance))
        if not os.path.exists(path):
            os.makedirs(path)

        # copy files
        component_path = None
        try:
            seq = pyseq.uncompress(instance.data('path'), fmt='%h%p%t %R')
            root = os.path.dirname(seq.path())
            component_path = os.path.join(path, seq.format('%h%p%t %R'))

            for f in seq:
                src = os.path.join(root, f)
                dst = os.path.join(path, f)

                shutil.copy(src, dst)
        except:
            root = os.path.dirname(instance.data('path'))
            f = os.path.basename(instance.data('path'))
            src = os.path.join(root, f)
            dst = os.path.join(path, f)
            component_path = dst

            shutil.copy(src, dst)

        components = instance.data('ftrackComponents')
        components[str(instance)]['path'] = component_path
        instance.set_data('ftrackComponents', value=components)

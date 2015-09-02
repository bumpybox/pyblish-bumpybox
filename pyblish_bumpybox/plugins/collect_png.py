import os

import pyblish.api
import pyseq
import ftrack


class CollectPNG(pyblish.api.Collector):
    """"""

    order = pyblish.api.Selector.order + 0.2
    hosts = ['ftrack']

    def process(self, context):

        files = [os.path.join(root, name)
                 for root, dirs, files in os.walk(os.getcwd())
                 for name in files
                 if name.endswith('.png')]

        for seq in pyseq.get_sequences(files):
            name = seq.head()

            # stripping the last character if its a symbol
            # for cleaner names
            if name[-1] in '{}()[].,:;+-_*/&|<>=~$':
                name = name[:-1]

            instance = context.create_instance(name=name)
            instance.set_data('family', value='png')
            path = os.path.join(os.path.dirname(seq.path()),
                                                seq.format(fmt='%h%p%t %R'))
            instance.set_data('path', value=path)

            path = os.path.join(seq.dirname, seq.format('%h%p%t %R'))
            components = {name: {'path': path}}
            instance.set_data('ftrackComponents', value=components)
            instance.set_data('ftrackAssetType', value='img')

            ftrack_data = context.data('ftrackData')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)

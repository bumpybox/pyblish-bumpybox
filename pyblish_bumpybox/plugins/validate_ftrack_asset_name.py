import os
import platform

import pyblish.api


@pyblish.api.log
class ValidateFtrackAssetName(pyblish.api.Validator):
    """ Modifies ftrack asset name """

    families = ['deadline.render']
    label = 'Ftrack Asset Name'

    def process(self, context, instance):

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        ftrack_data = context.data('ftrackData')

        if ftrack_data['Project']['code'] != 'the_call_up':
            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)

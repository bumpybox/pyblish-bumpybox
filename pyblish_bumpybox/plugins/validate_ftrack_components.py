import os

import pyblish.api
import ftrack


@pyblish.api.log
class ValidateFtrackComponents(pyblish.api.Validator):
    """ Validates the components submitted to Ftrack """

    order = pyblish.api.Validator.order + 0.1
    optional = True
    label = 'Ftrack Components'

    def process(self, instance):

        # skipping instance if ftrackData isn't present
        if not instance.context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        ftrack_data = instance.context.data('ftrackData')

        # skipping the call up project
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # skipping instance if asset version isn't present
        if 'AssetVersion' not in ftrack_data:
            self.log.info('No AssetVersion present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents present. Skipping this instance')
            return

        version_id = ftrack_data['AssetVersion']['id']
        asset_version = ftrack.AssetVersion(id=version_id)
        online_components = asset_version.getComponents()
        local_components = instance.data('ftrackComponents')

        for local_c in local_components:
           local_component = local_components[local_c]
           for online_c in online_components:

               # checking name matching
               if local_c == online_c.getName():

                   # checking value matching
                   path = local_component['path']
                   if path != online_c.getFile():
                       msg = "Component exists, but values aren't the same:"
                       msg += "\n\nComponent: %s" % local_c
                       msg += "\n\nLocal value: %s" % path
                       msg += "\n\nOnline value: %s" % online_c.getFile()
                       raise ValueError(msg)
                   else:
                       self.log.info('Component exists: %s' % local_c)

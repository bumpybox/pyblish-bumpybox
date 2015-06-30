import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateMayaRenderer(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    hosts = ['maya']
    version = (0, 1, 0)
    optional = True
    label = 'Renderer'

    def process(self, instance):

        self.log.info(instance.data('deadlineJobData'))
        self.log.info(instance.data('deadlinePluginData'))

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        # validate renderer
        msg = "Render Farm can't handle hardware renders on: %s" % str(instance)
        renderer = instance.data('deadlinePluginData')['Renderer']
        assert 'hardware' not in renderer.lower(), msg

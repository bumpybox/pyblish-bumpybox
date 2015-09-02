import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateRenderer(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Renderer'

    def process(self, instance):

        self.log.info(instance.data('deadlineData')['job'])
        self.log.info(instance.data('deadlineData')['plugin'])

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        # validate renderer
        msg = "Render Farm can't handle hardware renders on: %s" % str(instance)
        renderer = instance.data('deadlineData')['plugin']['Renderer']
        assert 'hardware' not in renderer.lower(), msg

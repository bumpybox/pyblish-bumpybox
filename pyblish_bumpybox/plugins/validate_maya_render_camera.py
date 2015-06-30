import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateMayaRenderCamera(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    hosts = ['maya']
    optional = True
    label = 'Render Camera'

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # validate non native camera active
        check = True
        for c in pymel.core.ls(type='camera'):
            if c.getParent().name() in ['persp', 'top', 'side', 'front']:
                if c.renderable.get():
                    check = False

        msg = 'Renderable Cameras is incorrect. Expected non default camera.'
        assert check, msg

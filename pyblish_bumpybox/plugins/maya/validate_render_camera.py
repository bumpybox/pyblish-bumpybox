import os

import pymel
import pyblish.api
import ftrack


class ValidateRenderCamera(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Camera'

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # validate non native camera active
        render_cameras = []
        for c in pymel.core.ls(type='camera'):
            if c.renderable.get():
                render_cameras.append(c)

        msg = 'No renderable camera selected.'
        assert render_cameras, msg

        check = True
        for c in render_cameras:
            if c.getParent().name() in ['persp', 'top', 'side', 'front']:
                check = False

        msg = 'Renderable Cameras is incorrect. Expected non default camera.'
        assert check, msg

        msg = "Can't render multiple cameras. Please use a render layer instead"
        assert len(render_cameras) == 1, msg

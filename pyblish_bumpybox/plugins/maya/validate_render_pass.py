import os

import pyblish.api
import pymel


class ValidateRenderPass(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Pass'

    def process(self, instance):

        data = instance.data('data')
        check = True

        self.log.info(instance)
        self.log.info(data)
        if data['renderpasses']:
            if 'imageFormat' in data:
                self.log.info(data['imageFormat'])
                if data['imageFormat'] != 51.0:
                    check = False
            else:
                drg = pymel.core.PyNode('defaultRenderGlobals')
                if drg.imageFormat.get() != 51.0:
                    check = False

        msg = '%s has render passes, ' % instance
        msg += 'but is using the wrong image format. Needs to be EXR'
        assert check, msg

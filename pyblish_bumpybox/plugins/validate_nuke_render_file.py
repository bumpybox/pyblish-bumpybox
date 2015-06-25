import os

import pyblish.api
import ftrack
import nuke


@pyblish.api.log
class ValidateNukeRenderFile(pyblish.api.Validator):
    """ Validates the output path for nuke renders """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Render File'
    optional = True

    def process(self, instance):

        # on going project specific exception
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        path = instance.data('deadlineJobData')['OutputFilename0']
        node = nuke.toNode(str(instance))

        # validate extension
        msg = 'Output extension needs to be ".exr",'
        msg += ' currently "%s"' % os.path.splitext(path)[-1]
        assert os.path.splitext(path)[-1] == '.exr', msg

        # validate compression
        msg = 'Compression needs to be "none"'
        assert node['compression'].value() == 'none', msg

        # validate colour space
        msg = 'Colour space needs to be "linear"'
        assert node['colorspace'].value() == 'default (linear)', msg

    def repair(self, instance):

        node = nuke.toNode(str(instance))

        output = os.path.splitext(node['file'].value())[0]
        node['file'].setValue(output + '.exr')
        node['compression'].setValue('none')
        node['colorspace'].setValue('default (linear)')

import os

import nuke
import pyblish.api
import ftrack


class ValidateMetadata(pyblish.api.Validator):
    """ Validates the path of the nuke script """

    families = ['deadline.render']
    label = 'Metadata'
    optional = True

    def process(self, instance):

        if 'metadata' in instance[0].knobs().keys():
            msg = 'Metadata needs to be set to "all metadata".'
            assert instance[0]['metadata'].value() == 'all metadata', msg

    def repair(self, instance):

        if 'metadata' in instance[0].knobs().keys():
            instance[0]['metadata'].setValue('all metadata')

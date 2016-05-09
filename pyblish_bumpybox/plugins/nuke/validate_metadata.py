import pyblish.api


class RepairValidateMetadata(pyblish.api.Action):

    label = 'Repair'
    icon = 'wrench'
    on = 'failed'

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:
            if 'metadata' in instance[0].knobs().keys():
                instance[0]['metadata'].setValue('all metadata')


class ValidateMetadata(pyblish.api.InstancePlugin):
    """ Validates write nodes 'metadata' attribute to be 'all metadata' """
    order = pyblish.api.ValidatorOrder
    families = ['deadline.render']
    label = 'Metadata'
    optional = True
    actions = [RepairValidateMetadata]

    def process(self, instance):

        if 'metadata' in instance[0].knobs().keys():
            msg = 'Metadata needs to be set to "all metadata".'
            assert instance[0]['metadata'].value() == 'all metadata', msg

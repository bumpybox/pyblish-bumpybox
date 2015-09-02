import pyblish.api


@pyblish.api.log
class ExtractDeadlineDraft(pyblish.api.Extractor):
    """ Gathers Draft related data for Deadline
    """

    order = pyblish.api.Extractor.order + 0.41
    families = ['deadline.render']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True
    label = 'Draft to Deadline'

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()

        # setting extra info key values
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        extra_info_key_value['DraftExtraArgs'] = ''
        extra_info_key_value['DraftVersion'] = ''
        extra_info_key_value['DraftUsername'] = ''
        extra_info_key_value['DraftUploadToShotgun'] = 'False'
        extra_info_key_value['DraftEntity'] = ''

        if 'nuke' in pyblish.api.current_host():
            import nuke
            width = nuke.root().format().width()
            height = nuke.root().format().height()
        else:
            width = None
            height = None

        extra_info_key_value['DraftFrameWidth'] = width
        extra_info_key_value['DraftFrameHeight'] = height

        job_data['ExtraInfoKeyValue'] = extra_info_key_value

        data = instance.data('deadlineData')
        data['job'] = job_data
        instance.set_data('deadlineData', value=data)

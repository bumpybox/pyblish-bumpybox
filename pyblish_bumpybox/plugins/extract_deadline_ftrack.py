import getpass

import pyblish.api
import ftrack


class ExtractDeadlineFtrack(pyblish.api.Extractor):
    """ Gathers Ftrack related data for Deadline """

    order = pyblish.api.Extractor.order + 0.4
    optional = True
    label = 'Ftrack to Deadline'
    hosts = ["nuke", "maya", "standalone"]

    def process(self, context, instance):

        if not context.has_data('ftrackData'):
            return

        for member in ["ftrackAsset", "ftrackAssetVersion"]:
            if member not in instance.data.keys():
                return

        job_data = {}
        plugin_data = {}
        if 'deadlineData' in instance.data:
            job_data = instance.data['deadlineData']['job'].copy()
            plugin_data = instance.data['deadlineData']['plugin'].copy()

        # getting data
        username = getpass.getuser()

        ftrack_data = context.data('ftrackData')

        project_name = ftrack_data['Project']['code']
        project_id = ftrack_data['Project']['id']

        task_name = ftrack_data['Task']['name']
        task_id = ftrack_data['Task']['id']

        asset_name = instance.data('ftrackAsset')['name']
        asset_id = instance.data('ftrackAsset')['id']

        version_id = instance.data('ftrackAssetVersion')['id']
        version_used_id = ''

        if instance.has_data('ftrackVersionUsedID'):
            version_id = ''
            version_used_id = instance.data('ftrackVersionUsedID')

        version_number = context.data('version')

        component_name = None
        if instance.has_data('ftrackComponents'):
            try:
                component_name = instance.data('ftrackComponents').keys()[0]
            except:
                pass

        # setting extra info
        extra_info = []
        if 'ExtraInfo' in job_data:
            extra_info = job_data['ExtraInfo']

        extra_info.extend([task_name, project_name, asset_name,
                          version_number, username])

        job_data['ExtraInfo'] = extra_info

        # setting extra info key values
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        extra_info_key_value['FT_TaskName'] = task_name
        extra_info_key_value['FT_Description'] = ''
        extra_info_key_value['FT_VersionId'] = version_id
        extra_info_key_value['FT_VersionUsedId'] = version_used_id
        extra_info_key_value['FT_ProjectId'] = project_id
        extra_info_key_value['FT_AssetName'] = asset_name
        extra_info_key_value['FT_AssetId'] = asset_id
        extra_info_key_value['FT_TaskId'] = task_id
        extra_info_key_value['FT_ProjectName'] = project_name
        extra_info_key_value['FT_Username'] = username
        extra_info_key_value['FT_VersionNumber'] = version_number
        extra_info_key_value['FT_ComponentName'] = component_name

        job_data['ExtraInfoKeyValue'] = extra_info_key_value

        # commenting to store full ftrack path
        comment = ""
        task = ftrack.Task(instance.context.data["ftrackData"]["Task"]["id"])
        for p in reversed(task.getParents()):
            comment += p.getName() + "/"
        comment += task.getName()
        comment = "Ftrack path: \"{0}\"".format(comment)

        job_data["Comment"] = comment

        # setting data
        data = {'job': job_data, 'plugin': plugin_data}
        instance.data['deadlineData'] = data

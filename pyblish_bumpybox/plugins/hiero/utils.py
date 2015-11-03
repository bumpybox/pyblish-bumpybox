import os
import re


def get_path(instance, ext, log, tag=None, sequence=True):
    import ftrack

    path = []
    filename = []

    # get ftrack data
    ftrack_data = instance.context.data('ftrackData')
    project = ftrack.Project(id=ftrack_data['Project']['id'])
    path.append(ftrack_data['Project']['root'])
    path.append('renders')
    path.append('transcode')

    try:
        name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
        path.append(name)
    except:
        log.info('No episode found.')

    try:
        name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
        path.append(name)
    except:
        log.info('No sequences found.')

    try:
        name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
        path.append(name)
    except:
        log.info('No shot found.')

    task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
    path.append(task_name)
    filename.append(task_name)

    # get version data
    version = 1
    if instance.context.has_data('version'):
        version = instance.context.data('version')
    version_string = 'v%s' % str(version).zfill(3)
    path.append(version_string)

    path.append(instance[0].parent().name())
    path.append(instance[0].name())

    filename.append(re.sub('[^\w\-_\. ]', '_', instance[0].name()))
    if tag:
        filename.append(tag)
    filename.append(version_string)
    if sequence:
        filename.append('%04d')
    filename.append(ext)

    path.append('.'.join(filename))

    return os.path.join(*path).replace('\\', '/')

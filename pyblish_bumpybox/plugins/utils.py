import os
import re
import platform


def GetTaskFilename(task_id, ext):

    import ftrack_api

    session = ftrack_api.Session()
    task = session.query('Task where id is "%s"' % task_id).one()
    path = []
    parents = task['link']
    project = session.query('Project where id is "%s"' % parents[0]['id'])

    disk = project.one()['disk']['windows']
    if platform.system().lower() != 'windows':
        disk = project.one()['disk']['unix']
    path.append(disk)

    path.append(project.one()['root'])

    root_folder = []
    for p in parents[1:]:
        tc = session.query('TypedContext where id is "%s"' % p['id']).one()
        path.append(tc['name'].lower())

        if tc['object_type']['name'] == 'Episode':
            root_folder.append('episodes')
        if tc['object_type']['name'] == 'Sequence':
            root_folder.append('sequences')
        if tc['object_type']['name'] == 'Shot':
            root_folder.append('shots')
    root_folder.append('tasks')
    path.insert(2, root_folder[0])

    filename = [parents[-2]['name'], parents[-1]['name'], 'v001', ext]
    path.append('.'.join(filename))

    return os.path.join(*path).replace('\\', '/')


def version_get(string, prefix, suffix=None):
    """Extract version information from filenames used by DD (and Weta, apparently)
    These are _v# or /v# or .v# where v is a prefix string, in our case
    we use "v" for render version and "c" for camera track version.
    See the version.py and camera.py plugins for usage."""

    if string is None:
        raise ValueError("Empty version string - no match")

    regex = "[/_.]"+prefix+"\d+"
    matches = re.findall(regex, string, re.IGNORECASE)
    if not len(matches):
        msg = "No \"_"+prefix+"#\" found in \""+string+"\""
        raise ValueError(msg)
    return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())


def version_set(string, prefix, oldintval, newintval):
    """Changes version information from filenames used by DD (and Weta, apparently)
    These are _v# or /v# or .v# where v is a prefix string, in our case
    we use "v" for render version and "c" for camera track version.
    See the version.py and camera.py plugins for usage."""

    regex = "[/_.]"+prefix+"\d+"
    matches = re.findall(regex, string, re.IGNORECASE)
    if not len(matches):
        return ""

    # Filter to retain only version strings with matching numbers
    matches = filter(lambda s: int(s[2:]) == oldintval, matches)

    # Replace all version strings with matching numbers
    for match in matches:
        # use expression instead of expr so 0 prefix does not make octal
        fmt = "%%(#)0%dd" % (len(match) - 2)
        newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
        string = re.sub(match, newfullvalue, string)
    return string


def get_version_up(path):
    """ Returns the next version of the path """

    (prefix, v) = version_get(path, 'v')
    v = int(v)
    return version_set(path, prefix, v, v + 1)


def next_nonexisting_version(path):
    """ Versions path up, until finding the first non-existing path """

    while True:
        if os.path.exists(path):
            path = get_version_up(path)
        else:
            return path

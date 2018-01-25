import os

from pyblish import api, plugin


plugin.ALLOW_DUPLICATES = True


def get_all_plugins():

    search_directory = os.path.abspath(
        os.path.join(__file__, "..", "..", "pyblish_bumpybox", "plugins")
    )
    directories = [search_directory]
    for root, dirs, files in os.walk(search_directory):
        for d in dirs:
            directories.append(os.path.join(root, d))

    hosts = [
        "nukeassist",
        "nuke",
        "maya",
        "nukestudio",
        "hiero",
        "houdini",
        "celaction"
    ]
    for host in hosts:
        api.register_host(host)

    return api.discover(paths=directories)

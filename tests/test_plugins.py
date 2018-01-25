import os
import logging

from pyblish import api, plugin


plugin.ALLOW_DUPLICATES = True


def test_plugins_load():

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("pyblish")
    log_file = __file__.replace(".py", ".log")
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)

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

    api.discover(paths=directories)

    logs = []
    with open(log_file, "r") as the_file:
        logs.extend(the_file.readlines())

    handler.close()
    os.remove(log_file)

    assert not logs

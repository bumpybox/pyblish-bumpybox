import os
import logging
import inspect

from pyblish import api
import lib


def test_plugins_load():

    logger = logging.getLogger("pyblish")
    logger.setLevel(logging.DEBUG)
    log_file = __file__.replace(".py", ".log")
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)

    lib.get_all_plugins()

    logs = []
    with open(log_file, "r") as the_file:
        logs.extend(the_file.readlines())

    handler.close()
    logger.removeHandler(handler)
    os.remove(log_file)
    logger.setLevel(logging.INFO)

    assert not logs


def test_argument_signature():

    failed_plugins = []
    for plugin in lib.get_all_plugins():
        args = inspect.getargspec(plugin.process).args

        if (isinstance(plugin(), api.InstancePlugin) and
           args != ["self", "instance"]):
            failed_plugins.append(plugin)

        if (isinstance(plugin(), api.ContextPlugin) and
           args != ["self", "context"]):
            failed_plugins.append(plugin)

    print ("Failed plugins:")
    for plugin in failed_plugins:
        print plugin

    assert not failed_plugins

import os
import logging

import lib


def test_plugins_load():

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("pyblish")
    log_file = __file__.replace(".py", ".log")
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)

    lib.get_all_plugins()

    logs = []
    with open(log_file, "r") as the_file:
        logs.extend(the_file.readlines())

    handler.close()
    os.remove(log_file)

    assert not logs

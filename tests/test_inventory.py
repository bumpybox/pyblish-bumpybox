import lib

from pyblish_bumpybox import inventory


def test_plugins_use_inventory_order():

    failed_plugins = []
    for plugin in lib.get_all_plugins():
        code_line = "order = inventory.get_order(__file__, \"{0}\")".format(
            plugin.__name__
        )
        with open(plugin.__module__, "r") as the_file:
            if code_line not in the_file.read():
                failed_plugins.append(plugin)

                print "\"{0}\" is missing:\n{1}".format(plugin, code_line)

    assert not failed_plugins


def test_inventory_order_match():

    errors = []
    for plugin in lib.get_all_plugins():
        try:
            name = inventory.get_variable_name(
                plugin.__module__, plugin.__name__
            )
            assert plugin.order == inventory.__dict__[name]
        except Exception as e:
            errors.append(e)

    for e in errors:
        print e

    assert not errors

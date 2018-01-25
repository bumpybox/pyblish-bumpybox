import lib

from pyblish_bumpybox import inventory


def test_class_name_attribute_existence():

    failed_plugins = []
    for plugin in lib.get_all_plugins():
        if "class_name" not in plugin.__dict__.keys():
            failed_plugins.append(plugin)

    print "Failed plugins:"
    for plugin in failed_plugins:
        print plugin

    assert not failed_plugins


def test_inventory_match():

    errors = []
    for plugin in lib.get_all_plugins():
        try:
            name = inventory.get_variable_name(
                plugin.__module__, plugin.__name__
            )
            assert plugin.order == inventory.__dict__[name]
        except KeyError:
            name = inventory.get_variable_name(
                plugin.__module__, plugin.__name__
            )
            errors.append(
                KeyError("\"{0}\" not found in inventory.".format(name))
            )
        except Exception as e:
            errors.append(e)

    for e in errors:
        print e

    assert not errors

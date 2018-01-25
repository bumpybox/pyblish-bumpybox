import lib


def test_class_name_attribute_existence():

    failed_plugins = []
    for plugin in lib.get_all_plugins():
        if "class_name" not in plugin.__dict__.keys():
            failed_plugins.append(plugin)

    print "Failed plugins:"
    for plugin in failed_plugins:
        print plugin

    assert not failed_plugins

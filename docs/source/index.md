## Welcome to pyblish-bumpybox documentation.

### Installation

This package is dependent on:

- [pyblish-base](https://github.com/pyblish/pyblish-base)
- [pyblish-lite](https://github.com/pyblish/pyblish-lite)
- [pyblish-maya](https://github.com/pyblish/pyblish-maya)
- [pyblish-nuke](https://github.com/pyblish/pyblish-nuke)
- [pyblish-houdini](https://github.com/pyblish/pyblish-houdini)
- [pyblish-standalone](https://github.com/pyblish/pyblish-standalone)
- [clique](https://gitlab.com/4degrees/clique)
- [pyperclip](https://github.com/asweigart/pyperclip)

Please refer to the individual packages for installation.

You also need to setup the environment before launching any application:

```
PYTHONPATH = "[pyblish-bumpybox repository path];[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/pythonpath"
HIERO_PLUGIN_PATH = "[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/hiero_plugin_path"
NUKE_PATH = "[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/nuke_path"
HOUDINI_PATH = "[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/houdini_path"
```

The plugins needs to be added to ```PYBLISHPLUGINPATH``` before launching any application. They are categorized into ```[host]\[task]```, so depending on which application are you working, you need to modify ```PYBLISHPLUGINPATH```. For example for a modeling task in Maya ```PYBLISHPLUGINPATH``` would look like this;

```
PYBLISHPLUGINPATH = "[pyblish-bumpybox repository path]/pyblish_bumpybox/plugins;[pyblish-bumpybox repository path]/pyblish_bumpybox/plugins/maya;[pyblish-bumpybox repository path]/pyblish_bumpybox/plugins/maya/modeling"
```

```eval_rst
.. toctree::
   :maxdepth: 2
   :hidden:

   workflow
   maya
   houdini
   instances
```

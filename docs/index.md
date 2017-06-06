# Installation

This package is dependent on:

- [pyblish-base](https://github.com/pyblish/pyblish-base)
- [pyblish-qml](https://github.com/pyblish/pyblish-qml) or [pyblish-lite](https://github.com/pyblish/pyblish-lite)
- [pyblish-maya](https://github.com/pyblish/pyblish-maya)
- [pyblish-nuke](https://github.com/pyblish/pyblish-nuke)
- [pyblish-houdini](https://github.com/pyblish/pyblish-houdini)
- [clique](https://gitlab.com/4degrees/clique)
- [pyperclip](https://github.com/asweigart/pyperclip)

Please refer to the individual packages for installation.

The plugins needs to be added to ```PYBLISHPLUGINPATH``` before launching any application. They are categorized into ```[host]\[task]```, so depending on which application you are working with, you need to modify ```PYBLISHPLUGINPATH```. For example for a modeling task in Maya ```PYBLISHPLUGINPATH``` would look like this;

```
PYBLISHPLUGINPATH = "[pyblish-grill repository path]/pyblish_grill/plugins;[pyblish-grill repository path]/pyblish_grill/plugins/maya;[pyblish-grill repository path]/pyblish_grill/plugins/maya/modeling"
```

# Workflows

- [General Workflow](general_workflow.md)
- [Maya](maya.md)
- [Houdini](houdini.md)
- [Nuke](nuke.md)

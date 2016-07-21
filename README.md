# pyblish-bumpybox

## Install

This package is dependent on:

- [pyblish-base](https://github.com/pyblish/pyblish-base)
- [pyblish-maya](https://github.com/pyblish/pyblish-maya)
- [pyblish-nuke](https://github.com/pyblish/pyblish-nuke)
- [pyblish-houdini](https://github.com/pyblish/pyblish-houdini)
- [pyblish-standalone](https://github.com/pyblish/pyblish-standalone)
- [pipeline-schema](https://github.com/Bumpybox/pipeline-schema)

Please refer to the individual packages for installation.

You also need to setup the environment before launching any application:

- ```PYTHONPATH```: ```[pyblish-bumpybox repository path];[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/pythonpath```
- ```PYBLISHPLUGINPATH```:  ```[pyblish-bumpybox repository path]/pyblish_bumpybox/plugins```
- ```HIERO_PLUGIN_PATH```:  ```[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/hiero_plugin_path```
- ```NUKE_PATH```:  ```[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/nuke_path```
- ```HOUDINI_PATH```:  ```[pyblish-bumpybox repository path]/pyblish_bumpybox/environment_variables/houdini_path```

## Usage

## Families

All the instances presented when publishing are categorized into three levels; ```Output Type```, ```Processing Location``` and ```File Type```. This is visualized through the families (sections in the UI), separated by a dot: ```[Output Type].[Processing Location].[File Type]```.

Examples of families:

- ```cache.local.alembic```
- ```cache.farm.vdb```
- ```img.local.exr```
- ```img.farm.png```
- ```render.local.ifd```
- ```render.farm.ass```

**Output Type**

This is a categorization of different files outputs. It generalizes workflows across different hosts (applications), so the user knows what it expected of the output. 

Examples of output types:

- ```cache``` : point caches, simulation caches etc.
- ```img```: any image type output.
- ```render```: render dependent files like ```ifd```, ```ass```, ```vrscene``` etc.

**Processing Location**

The ```Processing Location``` describes where the extraction will take place. Currently there are only two locations; ```local``` and ```farm```:

- ```local```: extraction happens on the local machine.
- ```farm```: data is send to a farm for extraction.


**File Type**

```File Type``` describes the end file type. This can be as specific as the extension of the file type; ```alembic``` and ```exr```, or slightly more generic like; ```geometry```. 

Examples of file types:

- ```alembic```
- ```geometry```
- ```exr```
- ```ifd```

# Houdini

The Houdini publishing pipeline includes the following nodes; ```Mantra```, ```Alembic```, ```Geometry```, ```Dynamics```.

To publish a nodes output, the workflow is the same for all output nodes. Create the node in the ```out``` context, and publish with ```File > Publish```.

You can disable a node for publishing by bypassing it, or hitting ```Shift + B``` with the node selected. When you enable/disable a node for publishing in the GUI, it will follow the same behaviour and bypass the specified nodes.

<iframe width="560" height="315" src="https://www.youtube.com/embed/245hB9_QSWk" frameborder="0" allowfullscreen></iframe>

### Instances

When publishing you will be presented with all the instances that were found in the scene. There are three main types of instances you will encounter; ```local```, ```farm``` and ```output```.

#### ```local```

This instance represents any node that will be processed on the local machine ei. the machine you publish from. They will be labelled with the name of the node like this; ```name - type - local```.

Examples:

- ```mantra1 - mantra - local```
- ```alembic1 - alembic - local```
- ```geometry1 - geometry - local```

#### ```farm```

This instance represents any node that will be processed remotely ei. by a render farm or other computing management like cloud computing. They will be labelled with the name of the node like this; ```name - type - farm```.

Examples:

- ```mantra1 - mantra - farm```
- ```alembic1 - alembic - farm```
- ```geometry1 - geometry - farm```

#### ```output```

This instance represents any nodes output that already exists ei. alembic files from an alembic node or image files from a mantra node. They will be labelled with the name of the node and the collection of files like this; ```node - collection```.

Examples:

- ```mantra1 - task_name.v001_mantra1_vm_picture.%04d.exr [1-2]```
- ```alembic1 - task_name.v001_alembic2_filename.%04d.abc [1]```
- ```geometry - task_name.v001_geometry2_sopoutput.%04d.bgeo.sc [1-2]```

### Takes

You can render specific takes in a scene, by pointing the output node to the take. Find the ```Render With Take``` parameter and choose which take to render.

<iframe width="560" height="315" src="https://www.youtube.com/embed/yvjXr78FdyY" frameborder="0" allowfullscreen></iframe>

### Farm Rendering

You can submit output nodes to a farm, for remote processing. Create a network box, add the output nodes and name the network box starting with ```farm```. All nodes for farm submission will have ```farm``` in their name, ei. ```mantra1 - farm```.

*NOTE: Distributed simulation with ```Dynamics``` nodes are not currently supported.*

<iframe width="560" height="315" src="https://www.youtube.com/embed/IgsguXI_IqM" frameborder="0" allowfullscreen></iframe>

You can have multiple network boxes that submits to the farm, as long as their name all starts with ```farm```.

*NOTE: Copy/pasting nodes can unassign them from a network box. Just drag'n'drop the output node out of the network box, and back inside to reassign.*

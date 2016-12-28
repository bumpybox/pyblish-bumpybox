# Houdini

The Houdini publishing pipeline includes the following nodes; ```Mantra```, ```Alembic```, ```Geometry```, ```Dynamics```.

To publish a nodes output, the workflow is the same for all output nodes. Create the node in the ```out``` context, and publish with ```File > Publish```.

You can disable a node for publishing by bypassing it, or hitting ```Shift + B``` with the node selected. When you enable/disable a node for publishing in the GUI, it will follow the same behaviour and bypass the specified nodes.

<iframe width="560" height="315" src="https://www.youtube.com/embed/245hB9_QSWk" frameborder="0" allowfullscreen></iframe>

### Instances

Please read about the instances you can encounter [here](instances.md)

### Takes

You can render specific takes in a scene, by pointing the output node to the take. Find the ```Render With Take``` parameter and choose which take to render.

<iframe width="560" height="315" src="https://www.youtube.com/embed/yvjXr78FdyY" frameborder="0" allowfullscreen></iframe>

### Remote Rendering

You can submit output nodes to a remote, for remote processing. Create a network box, add the output nodes and name the network box starting with ```remote```. All nodes for remote submission will have ```remote``` in their name, ei. ```mantra1 - remote```.

*NOTE: Distributed simulation with ```Dynamics``` nodes are not currently supported.*

<iframe width="560" height="315" src="https://www.youtube.com/embed/sGYEApiuoh4" frameborder="0" allowfullscreen></iframe>

You can have multiple network boxes that submits to the remote, as long as their name all starts with ```remote```.

*NOTE: Copy/pasting nodes can unassign them from a network box. Just drag'n'drop the output node out of the network box, and back inside to reassign.*

# Nuke

From Nuke you can publish various output formats. To publish an output format, you'll need to setup the scene first. Different output formats has different workflows for setting up the scene:

Output Format | Section
--- | ---
Image Sequence | [Write Node](#write-node)
Gizmo | [Group](#group)
LUT | [Group](#group)

## Write Node

To publish an image sequence from a write node, you just need to create one. The name of the write node will be the name of the output.

When you create a write node, some default settings and file path will be setup. By default the image format will be validated to EXR.

<iframe width="560" height="315" src="https://www.youtube.com/embed/NXydycPNzwk" frameborder="0" allowfullscreen></iframe>

If you want a different output format, you just need to input the extension and setup the formats settings.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_qvu4VfbUC8" frameborder="0" allowfullscreen></iframe>

Disabling a write node will disable it for publishing. Similarly if you disable a write node instances in the UI, it will get disabled in the Nuke script.

## Group

To publish a gizmo, you'll need to setup a group. Please read about creating groups [here](http://help.thefoundry.co.uk/nuke/8.0/content/user_guide/configuring_nuke/creating_sourcing_gizmos.html)

To publish a LUT, you'll need to setup a group. Please read the ```To Create a Viewer Process Gizmo``` section [here](http://help.thefoundry.co.uk/nuke/8.0/content/user_guide/configuring_nuke/using_gizmo_viewer_process.html)

## Remote Rendering/Processing

To send the processing of a node to a farm or the cloud, you need to encapsulate the write nodes with a backdrop, that has a name starting with ```remote```. You can have multiple backdrops in the Nuke script.

<iframe width="560" height="315" src="https://www.youtube.com/embed/exfn1nCQTYI" frameborder="0" allowfullscreen></iframe>

You can read more about the supported remote processing solutions [here](remote.md)

# [BACK](index.md)

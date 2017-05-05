# Nuke

From Nuke you can publish image sequences with the write node.

## Write Node

To publish an image sequence from a write node, you just need to create one. The name of the write node will be the name of the output.

By default the image format will be validated to EXR.

<iframe width="560" height="315" src="https://www.youtube.com/embed/NXydycPNzwk" frameborder="0" allowfullscreen></iframe>

If you want a different output format, you just need to input the extension and setup the formats settings.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_qvu4VfbUC8" frameborder="0" allowfullscreen></iframe>

## Remote Rendering/Processing

To send the processing of a node to a farm or the cloud, you need to encapsulate the write nodes with a backdrop, that has a name starting with ```remote```. You can have multiple backdrops in the Nuke script.

<iframe width="560" height="315" src="https://www.youtube.com/embed/exfn1nCQTYI" frameborder="0" allowfullscreen></iframe>

# Nuke

From Nuke you can publish image sequences with the write node.

## Write Node

To publish an image sequence from a write node, you just need to create one. The name of the write node will be the name of the output.

By default the image format will be validated to EXR.

<iframe width="560" height="315" src="https://www.youtube.com/embed/NXydycPNzwk" frameborder="0" allowfullscreen></iframe>

If you want a different output format, you just need to input the extension and setup the formats settings.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_qvu4VfbUC8" frameborder="0" allowfullscreen></iframe>

Disabling a write node will disable it for publishing. Similarly if you disable a write node instances in the UI, it will get disabled in the Nuke script.

## Remote Rendering/Processing

To send the processing of a node to a farm or the cloud, you need to encapsulate the write nodes with a backdrop, that has a name starting with ```remote```. You can have multiple backdrops in the Nuke script.

<iframe width="560" height="315" src="https://www.youtube.com/embed/exfn1nCQTYI" frameborder="0" allowfullscreen></iframe>

You can read more about the supported remote processing solutions here: http://pyblish-bumpybox.readthedocs.io/en/latest/remote.html

## Ftrack

When launching Nuke from Ftrack there will be an initial setup of the script, depending on the custom attributes that are available. These custom attributes will be queried from the parent entity of the task.

```eval_rst
==========================  =================  ==========================
Description                 Ftrack Attributes  Nuke Project Settings Knob
==========================  =================  ==========================
First frame of frame range  fstart             first_frame
Last frame of frame range   fend               last_frame
Frame rate                  fps                fps
Resolution width            width              format
Resolution height           height             format
==========================  =================  ==========================
```

Once these settings are set, they will not be set again. You can force the settings to be applied on start up, by unchecking the attributes in the ```Ftrack``` tab of Project Settings.

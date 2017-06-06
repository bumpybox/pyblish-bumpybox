# Remote

pyblish-bumpybox currently supports two remote processing solutions; ```Deadline```and ```RoyalRender```.

Please follow each applications workflow for settings up the scenes for remote processing.

## RoyalRender

Submission to RoyalRender is currently supported for Maya and Nuke.

### Available Parameters

Parameter | Application | Instance Type | Where To Access
--- | ---
Priority | Maya | RenderLayer | Attribute on the renderlayer node
Priority | Nuke | Write Node | Knob in the "RoyalRender" tab on the write node

## Deadline

Submission to Deadline is currently supported for; Maya, Nuke and Houdini.

### Available Parameters

Parameter | Application | Instance Type | Where To Access
--- | ---
Priority | Maya | RenderLayer | Attribute on the renderlayer node
Priority | Nuke | Write Node | Knob in the "Deadline" tab on the write node
Priority | Houdini | All instances | Attribute in the "Deadline" tab on the nodes
Chunk Size | Maya | RenderLayer | Attribute on the renderlayer node
Chunk Size | Nuke | Write Node | Knob in the "Deadline" tab on the write node
Chunk Size | Houdini | All instances | Attribute in the "Deadline" tab on the nodes
Pool | Maya | RenderLayer | Attribute on the renderlayer node
Pool | Nuke | Write Node | Knob in the "Deadline" tab on the write node
Pool | Houdini | All instances | Attribute in the "Deadline" tab on the nodes
Concurrent Tasks | Maya | RenderLayer | Attribute on the renderlayer node
Concurrent Tasks | Nuke | Write Node | Knob in the "Deadline" tab on the write node
Concurrent Tasks | Houdini | All instances | Attribute in the "Deadline" tab on the nodes

# [BACK](index.md)

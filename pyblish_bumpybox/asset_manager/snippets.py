import os
import re

import nuke

def getConnectedNodes(node):
    '''
    Returns a two-tuple of lists. Each list is made up of two-tuples in the
    form ``(index, nodeObj)`` where 'index' is an input index and 'nodeObj'
    is a Nuke node.

    The first list contains the inputs to 'node', where each 'index' is the
    input index of 'node' itself.

    The second contains its outputs, where each 'index' is the input index that
    is connected to 'node'.
    '''
    inputNodes = [(i, node.input(i)) for i in range(node.inputs())]
    outputNodes = []
    for depNode in nuke.dependentNodes(nuke.INPUTS | nuke.HIDDEN_INPUTS, node):
        for i in range(depNode.inputs()):
            if depNode.input(i) == node:
                outputNodes.append((i, depNode))
    return (inputNodes, outputNodes)

def swapOutNode(targetNode, newNode):
    '''
    Mostly mimics the Ctrl + Shift + drag-and-drop node functionality in Nuke.

    'targetNode': The node (or node name) to be replaced.
    'newNode': The node (or node name) that will replace it.
    '''
    if isinstance(targetNode, basestring):
        targetNode = nuke.toNode(targetNode)
    if isinstance(newNode, basestring):
        newNode = nuke.toNode(newNode)
    if not (isinstance(targetNode, nuke.Node) and isinstance(newNode, nuke.Node)):
        return
    sourcePos = (newNode.xpos(), newNode.ypos())
    targetPos = (targetNode.xpos(), targetNode.ypos())
    oldSel = nuke.selectedNodes()
    inputNodes, outputNodes = getConnectedNodes(targetNode)
    nukescripts.clear_selection_recursive()
    targetNode.setSelected(True)
    nuke.extractSelected()
    targetNode.setSelected(False)
    newNode.setXYpos(*targetPos)
    targetNode.setXYpos(*sourcePos)
    for inNode in inputNodes:
        newNode.setInput(*inNode)
    for index, node in outputNodes:
        node.setInput(index, newNode)
    for node in oldSel:
        node.setSelected(True)
    return True

def version_get(string, prefix, suffix = None):
  """Extract version information from filenames used by DD (and Weta, apparently)
  These are _v# or /v# or .v# where v is a prefix string, in our case
  we use "v" for render version and "c" for camera track version.
  See the version.py and camera.py plugins for usage."""

  if string is None:
    raise ValueError, "Empty version string - no match"

  regex = "[/_.]"+prefix+"\d+"
  matches = re.findall(regex, string, re.IGNORECASE)
  if not len(matches):
    msg = "No \"_"+prefix+"#\" found in \""+string+"\""
    raise ValueError, msg
  return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())

def getFirst(path, regex):
    versions = os.listdir(path)
    versions.sort()
    for v in reversed(versions):
        for f in os.listdir(os.path.join(path, v)):
            matches = re.findall(regex, f, re.IGNORECASE)
            if len(matches):
                return os.path.join(path, v, f)

node = nuke.selectedNode()

basename = os.path.basename(node['file'].value())
version_string = ''.join(version_get(basename, 'v'))
basename = basename.replace(version_string, 'v[0-9]{3}')

f = node['file'].value()
versions_path =  os.path.abspath(os.path.join(f, '..', '..'))

path = getFirst(versions_path, basename)


new_node = nuke.createNode('Camera2', 'file {%s} read_from_file True'  % path)
new_node['frame_rate'].setValue(node['frame_rate'].value())

new_node.setXpos(node.xpos())
new_node.setYpos(node.ypos())

swapOutNode(node, new_node)
nuke.delete(node)

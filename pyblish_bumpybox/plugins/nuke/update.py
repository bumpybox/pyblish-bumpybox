import os
import re
import traceback

import nuke
import nukescripts
import pyblish.api
from PySide import QtGui


def message_box(context, text, title, warning=False):

    box = QtGui.QMessageBox()
    box.setText(text)
    context.data['messageBox'] = box
    box.setWindowTitle(title)
    if warning:
        box.setIcon(QtGui.QMessageBox.Warning)
    box.show()


class ReadGeo(pyblish.api.Action):

    label = 'Update ReadGeo'

    def process(self, context):

        errors = False
        for node in nuke.allNodes():
            if node.Class() not in ['ReadGeo2', 'ReadGeo']:
                continue

            try:
                basename = os.path.basename(node['file'].value())
                version_string = ''.join(self.version_get(basename, 'v'))
                basename = basename.replace(version_string, 'v[0-9]{3}')

                f = node['file'].value()
                versions_path =  os.path.abspath(os.path.join(f, '..', '..'))

                path = self.getFirst(versions_path, basename)


                new_node = nuke.createNode('ReadGeo2', 'file {%s}' % path)
                new_node['frame_rate'].setValue(node['frame_rate'].value())

                # selecting the same items
                sceneView = new_node['scene_view']

                allItems = sceneView.getAllItems()
                sceneView.setImportedItems(allItems)
                sceneView.setSelectedItems(allItems)

                sceneView.setSelectedItems(node['scene_view'].getSelectedItems())

                new_node.setXpos(node.xpos())
                new_node.setYpos(node.ypos())

                self.swapOutNode(node, new_node)
                nuke.delete(node)
            except:
                errors = True
                self.log.error(traceback.format_exc())

        if errors:
            message_box(context, 'ReadGeo update completed with errors!',
                        'Update', warning=True)
        else:
            message_box(context, 'ReadGeo update completed successfully!',
                        'Update', warning=False)

    def version_get(self, string, prefix, suffix = None):
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

    def getConnectedNodes(self, node):
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

    def swapOutNode(self, targetNode, newNode):
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
        inputNodes, outputNodes = self.getConnectedNodes(targetNode)
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

    def getFirst(self, path, regex):
        versions = os.listdir(path)
        versions.sort()
        for v in reversed(versions):
            for f in os.listdir(os.path.join(path, v)):
                matches = re.findall(regex, f, re.IGNORECASE)
                if len(matches):
                    return os.path.join(path, v, f)


class Camera(pyblish.api.Action):

    label = 'Update Camera'

    def process(self, context):

        errors = False
        for node in nuke.allNodes():
            if node.Class() not in ['Camera2']:
                continue

            try:
                basename = os.path.basename(node['file'].value())
                version_string = ''.join(self.version_get(basename, 'v'))
                basename = basename.replace(version_string, 'v[0-9]{3}')

                f = node['file'].value()
                versions_path =  os.path.abspath(os.path.join(f, '..', '..'))

                path = self.getFirst(versions_path, basename)


                new_node = nuke.createNode('Camera2', 'file {%s} read_from_file True'  % path)
                new_node['frame_rate'].setValue(node['frame_rate'].value())

                new_node.setXpos(node.xpos())
                new_node.setYpos(node.ypos())

                self.swapOutNode(node, new_node)
                nuke.delete(node)
            except:
                errors = True
                self.log.error(traceback.format_exc())

        if errors:
            message_box(context, 'Camera update completed with errors!',
                        'Update', warning=True)
        else:
            message_box(context, 'Camera update completed successfully!',
                        'Update', warning=False)

    def version_get(self, string, prefix, suffix = None):
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

    def getConnectedNodes(self, node):
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

    def swapOutNode(self, targetNode, newNode):
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
        inputNodes, outputNodes = self.getConnectedNodes(targetNode)
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

    def getFirst(self, path, regex):
        versions = os.listdir(path)
        versions.sort()
        for v in reversed(versions):
            for f in os.listdir(os.path.join(path, v)):
                matches = re.findall(regex, f, re.IGNORECASE)
                if len(matches):
                    return os.path.join(path, v, f)


class Read(pyblish.api.Action):

    label = 'Update Read'

    def process(self, context):

        errors = False
        for node in nuke.allNodes():
            if node.Class() != 'Read':
                continue

            try:
                f = node['file'].value()
                version = self.version_get(f, 'v')
                name = os.path.basename(os.path.dirname(f))
                versions_path =  os.path.abspath(os.path.join(f, '..', '..', '..'))
                versions = os.listdir(versions_path)
                versions.sort()
                v = self.getFirst(versions, versions_path, name)
                node['file'].setValue(f.replace('v' + version[1], v))
            except:
                errors = True
                self.log.error(traceback.format_exc())

        if errors:
            message_box(context, 'Read update completed with errors!',
                        'Update', warning=True)
        else:
            message_box(context, 'Read update completed successfully!',
                        'Update', warning=False)

    def version_get(self, string, prefix, suffix = None):
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

    def getFirst(self, versions, path, name):
        for v in reversed(versions):
            for f in os.listdir(os.path.join(path, v)):
                if f == name:
                    return v


class Update(pyblish.api.Plugin):

    actions = [Camera, ReadGeo, Read]

    def process(self, context):
        pass

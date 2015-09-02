# hfKillComponentShading v2.05 by henry foster (henry@toadstorm.com), 04/08/2013
#
# this script nukes per-face shading on polygon meshes. component shading breaks everything and is terrible so this cleans
# things nicely. it also deletes history on objects it cleans, so be warned.
# usage: self.hfHighlightBadShaded() highlights and returns objects with per-face shading.
# self.hfSplitBadShaded() looks for a list of bad shading engines. it's meant to be used with self.hfHighlightBadShaded()'s first return value.
# this function will actually break objects apart based on per-face shading.
# self.hfRepairShadingConnections() takes a list of broken objects and breaks all shading connections, then rebuilds them. this needs
# to be run after running self.hfSplitBadShaded.
#

import pymel
import maya.cmds as cmds
import maya.mel as mel
import pyblish.api


class ValidateComponentShading(pyblish.api.Validator):
    """"""

    families = ['scene']
    optional = True
    label = 'Component Shading'

    def hfHighlightBadShaded(self):
        meshes = cmds.ls(type='mesh')
        badMeshes = []
        badEngines = []
        warn = []
        # any meshes that are instanced should be left out, since these will return false positives.
        instances = []
        for i in meshes:
            parent = cmds.listRelatives(i,ap=1)
            if len(parent) > 1:
                # this shape has multiple parents, so it's instanced
                instances.append(i)
        meshes = [f for f in meshes if f not in instances]
        for mesh in meshes:
            engines = cmds.listConnections(mesh, type='shadingEngine')
            # print('checking mesh: ')
            # print(mesh)
            if engines != None:
                if len(engines) > 1:
                    badMeshes.append(mesh)
                    badEngines.extend(engines)

        badEngines = list(set(badEngines))
        return badEngines, badMeshes

    def hfSplitBadShaded(self, engines):
        modifiedShapes = []
        for sg in engines:
            print('checking shading group: '+sg)
            cmds.hyperShade(objects=sg)
            components = cmds.ls(sl=1)
            uniqueShapes = []
            for entry in components:
                uniqueShapes.append(entry.split('.')[0])
                # remove whole shapes (not components) from the list.
                if entry.rfind('.f') == -1:
                    components.remove(entry)
            if len(components) > 0:
                components.sort()
                # remove duplicates from uniqueShapes.
                uniqueShapes = list(set(uniqueShapes))
                modifiedShapes.extend(uniqueShapes)
                # print('\nunique shapes under shading group: ')
                # print(uniqueShapes)
                for shape in uniqueShapes:
                    cmds.select(cl=1)
                    # get the total num of faces for the shape for later use.
                    totalFaces = cmds.polyEvaluate(shape, f=1)
                    for comp in components:
                        testStr = shape+'.f['
                        if testStr in comp:
                            # the current component is a member of the current mesh we're splitting and it has the shader we want.
                            cmds.select(comp, add=1)
                    selFaces = cmds.ls(sl=1)
                    # print 'selection:'
                    # print selFaces
                    # extract the selected faces if we aren't selecting every face of the current mesh.
                    if len(selFaces) < int(totalFaces) and len(selFaces) > 0:
                        cmds.polyChipOff(selFaces, kft=1, dup=0)
                        cmds.delete(shape,ch=1)
                    # now the mesh is broken into shells. separate it if possible.
                    if cmds.polyEvaluate(shape, s=1) > 1:
                        newObjects = cmds.polySeparate(shape, ch=0)
                        modifiedShapes.extend(newObjects)
                        # print('split new shapes: ')
                        # print(newObjects)
                        cmds.select(newObjects)
                        # print(cmds.ls(sl=1))
                        cmds.delete(ch=1)
        cmds.select(cl=1)
        # now in order to return all the new meshes we made, we should sort through uniqueShapes and remove anything that no longer
        # exists. anything that's been split, etc.
        modifiedShapes = list(set(modifiedShapes))
        returnShapes = []
        for shape in modifiedShapes:
            if cmds.objExists(shape) == 0:
                modifiedShapes.remove(shape)
            else:
                meshNodes = cmds.listRelatives(shape, s=1)
                if meshNodes != None:
                # if we are not testing an xform, meshNodes will be a 'NoneType' object so we should include an exception.
                    returnShapes.extend(meshNodes)

        return returnShapes

    def hfRepairShadingConnections(self, meshes):
        for mesh in meshes:
            shaders = cmds.listConnections(mesh, t='shadingEngine')
            # we are assuming that the first shading connection is correct. we are also assuming that we don't
            # want to use initialShadingGroup unless there are no other shaders connected.
            for shader in shaders:
                if shader == "initialShadingGroup":
                    shaders.remove(shader)
            if len(shaders) < 1:
                shaders.append("initialShadingGroup")
            # so now shaders[0] is the guy we want. nuke all shadingEngine conections from the mesh to shadingEngines.
            conns = cmds.listConnections(mesh, c=1, p=1, t='shadingEngine')
            for conn in conns:
                cmds.delete(conn, icn=1)
            # now apply shaders[0] to the mesh.
            cmds.select(mesh)
            cmds.hyperShade(assign=shaders[0])
        cmds.select(cl=1)
        #cmds.warning('\nRemoved component shading on '+str(len(meshes))+' objects.')

    def hfSplitByShader(self):
        badEngines, badMeshes = self.hfHighlightBadShaded()
        if badEngines != None and len(badEngines) > 0:
            splitObjects = self.hfSplitBadShaded(badEngines)
            self.hfRepairShadingConnections(splitObjects)
            cmds.warning('Cleanup complete! '+str(len(splitObjects))+' objects split and cleaned.')
            # return splitObjects
        else:
            cmds.warning('No component shading detected.')
            # return('No component shading detected.')

    def hfFixBadShading(self):
        badEngines, badMeshes = self.hfHighlightBadShaded()
        if badEngines != None and len(badEngines) > 0:
            self.hfRepairShadingConnections(badMeshes)
            cmds.warning('Cleanup complete! '+str(len(badMeshes))+' objects cleaned.')
            return badMeshes
        else:
            cmds.warning('No component shading detected.')
            return 0

    def hfCheckShading(self):
        badEngines, badMeshes = self.hfHighlightBadShaded()
        if badEngines != None and len(badEngines) > 0:
            msg = 'badEngines: ' + str(badEngines)
            self.log.error(msg)
            msg = 'badMeshes: ' + str(badMeshes)
            self.log.error(msg)

            return False
        else:
            self.log.info('No component shading detected.')
            return True

    def process(self, instance):

        msg = 'Found objects with component shading.'
        assert self.hfCheckShading(), msg

    def repair(self, instance):

        self.hfFixBadShading()

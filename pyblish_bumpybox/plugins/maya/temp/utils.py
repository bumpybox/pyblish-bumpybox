"""
hfKillComponentShading v2.05 by henry foster (henry@toadstorm.com),04/08/2013

this script nukes per-face shading on polygon meshes. component shading breaks
everything and is terrible so this cleans things nicely. it also deletes
history on objects it cleans, so be warned.

usage: hfHighlightBadShaded() highlights and returns objects with per-face
shading.
hfSplitBadShaded() looks for a list of bad shading engines. it's meant to
be used with hfHighlightBadShaded()'s first return value. this function
will actually break objects apart based on per-face shading.
hfRepairShadingConnections() takes a list of broken objects and breaks all
shading connections, then rebuilds them. this needs to be run after running
hfSplitBadShaded.
"""
import os
import maya.cmds as cmds


def hfHighlightBadShaded():
    meshes = cmds.ls(type='mesh')
    badMeshes = []
    badEngines = []
    # any meshes that are instanced should be left out, since these will
    # return false positives.
    instances = []
    for i in meshes:
        parent = cmds.listRelatives(i, ap=1)
        if len(parent) > 1:
            # this shape has multiple parents, so it's instanced
            instances.append(i)
    meshes = [f for f in meshes if f not in instances]
    for mesh in meshes:
        engines = cmds.listConnections(mesh, type='shadingEngine')
        # print('checking mesh: ')
        # print(mesh)
        if engines is not None:
            if len(engines) > 1:
                badMeshes.append(mesh)
                badEngines.extend(engines)

    badEngines = list(set(badEngines))
    return badEngines, badMeshes


def hfSplitBadShaded(engines):
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
                        # the current component is a member of the current mesh
                        # we're splitting and it has the shader we want.
                        cmds.select(comp, add=1)
                selFaces = cmds.ls(sl=1)
                # print 'selection:'
                # print selFaces
                # extract the selected faces if we aren't selecting every face
                # of the current mesh.
                if len(selFaces) < int(totalFaces) and len(selFaces) > 0:
                    cmds.polyChipOff(selFaces, kft=1, dup=0)
                    cmds.delete(shape, ch=1)
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
    # now in order to return all the new meshes we made, we should sort through
    # uniqueShapes and remove anything that no longer exists.
    # anything that's been split, etc.
    modifiedShapes = list(set(modifiedShapes))
    returnShapes = []
    for shape in modifiedShapes:
        if cmds.objExists(shape) == 0:
            modifiedShapes.remove(shape)
        else:
            meshNodes = cmds.listRelatives(shape, s=1)
            if meshNodes is not None:
                # if we are not testing an xform, meshNodes will be a
                # 'NoneType' object so we should include an exception.
                returnShapes.extend(meshNodes)

    return returnShapes


def hfRepairShadingConnections(meshes):
    for mesh in meshes:
        shaders = cmds.listConnections(mesh, t='shadingEngine')
        # we are assuming that the first shading connection is correct.
        # we are also assuming that we don't want to use initialShadingGroup
        # unless there are no other shaders connected.
        for shader in shaders:
            if shader == "initialShadingGroup":
                shaders.remove(shader)
        if len(shaders) < 1:
            shaders.append("initialShadingGroup")
        # so now shaders[0] is the guy we want. nuke all shadingEngine
        # conections from the mesh to shadingEngines.
        conns = cmds.listConnections(mesh, c=1, p=1, t='shadingEngine')
        for conn in conns:
            cmds.delete(conn, icn=1)
        # now apply shaders[0] to the mesh.
        cmds.select(mesh)
        cmds.hyperShade(assign=shaders[0])
    cmds.select(cl=1)


def hfSplitByShader():
    badEngines, badMeshes = hfHighlightBadShaded()
    if badEngines is not None and len(badEngines) > 0:
        splitObjects = hfSplitBadShaded(badEngines)
        hfRepairShadingConnections(splitObjects)
        cmds.warning('Cleanup complete! ' + str(len(splitObjects)) +
                     ' objects split and cleaned.')
    else:
        cmds.warning('No component shading detected.')


def hfFixBadShading():
    badEngines, badMeshes = hfHighlightBadShaded()
    if badEngines is not None and len(badEngines) > 0:
        hfRepairShadingConnections(badMeshes)
        cmds.warning('Cleanup complete! ' + str(len(badMeshes)) +
                     ' objects cleaned.')
        return badMeshes
    else:
        cmds.warning('No component shading detected.')
        return 0


def hfCheckShading(log):
    badEngines, badMeshes = hfHighlightBadShaded()
    if badEngines is not None and len(badEngines) > 0:
        msg = 'badEngines: ' + str(badEngines)
        log.error(msg)
        msg = 'badMeshes: ' + str(badMeshes)
        log.error(msg)

        return False
    else:
        log.info('No component shading detected.')
        return True


def texture_path(instance):
    node = instance[0]
    src = node.fileTextureName.get()

    current_dir = os.path.dirname(instance.context.data('currentFile'))

    dst = os.path.join(current_dir, 'maps', os.path.basename(src))
    return dst.replace('\\', '/')


def get_path(context):
    import ftrack

    ftrack_data = context.data('ftrackData')

    project = ftrack.Project(id=ftrack_data['Project']['id'])
    root = project.getRoot()
    task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
    version_number = context.data('version')
    version_name = 'v%s' % (str(version_number).zfill(3))

    path = [root, 'renders', 'img_sequences']

    task = ftrack.Task(ftrack_data['Task']['id'])
    for p in reversed(task.getParents()[:-1]):
        path.append(p.getName())

    path.append(task_name)
    path.append(version_name)

    return os.path.join(*path).replace('\\', '/')


def get_project_path(context, log):
    path = []

    # get ftrack data
    ftrack_data = context.data('ftrackData')
    path.append(ftrack_data['Project']['root'])
    child_path = []
    parent = False

    try:
        name = ftrack_data['Asset_Build']['name'].replace(' ', '_').lower()
        path.append('library')
        asset_type = ftrack_data['Asset_Build']['type'].lower()
        path.append(asset_type)
        path.append(name)
    except:
        log.info('No asset build found.')

    try:
        name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
        path.append('episodes')
        child_path.append(name)
        parent = True
    except:
        log.info('No episode found.')

    try:
        name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
        child_path.append(name)

        if not parent:
            path.append('sequences')

        parent = True
    except:
        log.info('No sequences found.')

    try:
        name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
        child_path.append(name)

        if not parent:
            path.append('shots')
    except:
        log.info('No shot found.')

    path.extend(child_path)

    task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
    path.append(task_name)

    return os.path.join(*path).replace('\\', '/')

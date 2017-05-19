import imp
import os

import pymel.core as pm
import maya.cmds as mc
import maya.mel as mm

import pyblish.api
import pyblish_lite


# Quiet load alembic plugins
pm.loadPlugin("AbcExport.mll", quiet=True)
pm.loadPlugin("AbcImport.mll", quiet=True)


# Set project to workspace next to scene file.
def pyblish_bumpybox_set_workspace():
    work_dir = os.path.dirname(os.path.abspath(pm.system.sceneName()))
    workspace = os.path.join(work_dir, "workspace")

    if not os.path.exists(workspace):
        os.makedirs(workspace)

    pm.system.Workspace.open(work_dir)

    rules = [
        "3dPaintTextures",
        "ASS",
        "ASS Export",
        "Alembic",
        "BIF",
        "CATIAV4_ATF",
        "CATIAV5_ATF",
        "DAE_FBX",
        "DAE_FBX export",
        "Fbx",
        "IGES_ATF",
        "INVENTOR_ATF",
        "JT_ATF",
        "NX_ATF",
        "OBJ",
        "OBJexport",
        "PROE_ATF",
        "SAT_ATF",
        "STEP_ATF",
        "STL_ATF",
        "alembicCache",
        "audio",
        "autoSave",
        "bifrostCache",
        "clips",
        "depth",
        "diskCache",
        "eps",
        "fileCache",
        "fluidCache",
        "furAttrMap",
        "furEqualMap",
        "furFiles",
        "furImages",
        "furShadowMap",
        "illustrator",
        "images",
        "iprImages",
        "mayaAscii",
        "mayaBinary",
        "mel",
        "move",
        "movie",
        "offlineEdit",
        "particles",
        "renderData",
        "sceneAssembly",
        "scripts",
        "shaders",
        "sound",
        "sourceImages",
        "teClipExports",
        "templates",
        "timeEditor",
        "translatorData"
    ]

    for item in rules:
        pm.Workspace.fileRules[item] = "workspace"

    # Scene is needs to be directly in the project folder,
    # so people can open old versions and save as new versions.
    pm.Workspace.fileRules["scene"] = ""

    pm.system.Workspace.save()


pm.evalDeferred("pyblish_bumpybox_set_workspace()")


# Pyblish callbacks for presisting instance states to the scene.
def toggle_instance(instance, new_value, old_value):

    node = instance[0]

    families = instance.data.get("families", [])
    if "cache" in families or "scene" in families:
        attrs = []
        for attr in node.listAttr(userDefined=True):
            attrs.append(attr.name(includeNode=False))

        attr_list = list(set(attrs) & set(families))

        if attr_list:
            node.attr(attr_list[0]).set(new_value)

    if "renderlayer" in instance.data.get("families", []):

        node.renderable.set(new_value)

    if "playblast" in instance.data.get("families", []):

        node.getTransform().publish.set(new_value)

    if "file" in instance.data.get("families", []):

        node.publish.set(new_value)


pyblish.api.register_callback("instanceToggled", toggle_instance)

# Register pyblish_lite.
pyblish.api.register_gui("pyblish_lite")

# pyblish_lite settings
pyblish_lite.settings.InitialTab = "overview"


# Adding pyblish-bumpybox menu
def pyblish_bumpybox_menu_init():

    gMainWindow = mm.eval("$temp1=$gMainWindow")
    if mc.menu("pyblish-bumpybox", exists=True):
        mc.deleteUI("pyblish-bumpybox")

    menu = mc.menu(
        "pyblish-bumpybox",
        parent=gMainWindow,
        tearOff=False,
        label="pyblish-bumpybox"
    )

    mc.menuItem(
        "processingLocation",
        label="Processing Location",
        parent=menu,
        command=(
            "from pyblish_bumpybox.maya import processing_location;" +
            "processing_location.show()"
        )
    )


mc.evalDeferred("pyblish_bumpybox_menu_init()")

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_maya")

    import ftrack_assets
    import ftrack_init
    ftrack_assets.register_assets()
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)

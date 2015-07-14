import pymel
import pyblish.api


@pyblish.api.log
class ValidateModelingNodes(pyblish.api.Validator):
    """"""

    families = ['scene']

    defaultTypes = '''
    globalCacheControl
    renderLayer
    strokeGlobals
    transform
    ikSystem
    objectSet
    dynController
    displayLayer
    defaultRenderUtilityList
    materialInfo
    postProcessList
    shadingEngine
    sequenceManager
    renderLayerManager
    hyperGraphInfo
    defaultTextureList
    aiAOVDriver
    shaderGlow
    mentalrayGlobals
    defaultRenderingList
    lambert
    hardwareRenderGlobals
    aiOptions
    renderGlobalsList
    hyperLayout
    mesh
    displayLayerManager
    defaultShaderList
    lightList
    mentalrayOptions
    hardwareRenderingGlobals
    hwRenderGlobals
    particleCloud
    viewColorManager
    lightLinker
    partition
    dof
    camera
    aiAOVFilter
    mentalrayItemsList
    defaultLightList
    renderQuality
    time
    renderGlobals
    resolution
    mentalrayFramebuffer
    script
    '''

    def get_types(self):
        types = []
        for node in pymel.core.ls():
            types.append(node.type())

        for t in set(types):
            print t

    def process(self, instance):

        check = True
        for node in pymel.core.ls():
            if node.type() not in self.defaultTypes:
                msg = 'Found non modeling node in scene: %s' % node.name()
                self.log.error(msg)

                check = False

        assert check, 'Non modeling nodes in scene.'

    def repair(self, instance):

        for node in pymel.core.ls():
            if node.type() not in self.defaultTypes:
                try:
                    pymel.core.delete(node)
                except:
                    self.log.info("Couldn't delete node: %s" % node.name())

import os

import pyblish.api
import pymel
import pymel.core


class CollectRenderlayers(pyblish.api.Collector):
    """ Gathers all renderlayers
    TODO:
        - support frame range overrides
            - getting some odd returned values from the renderlayer adjustments
    """

    imageFormats = {'svg': 62, 'psd': 36, 'bmp': 20, 'sgi': 13, 'eps': 9,
                    'tif': 4, 'psd': 31, 'iff': 7, 'pic': 1, 'ai': 61,
                    'yuv': 12, 'mov': 22, 'sgi': 5, 'sgi': 21, 'als': 6,
                    'imf': 50, 'qif': 34, 'dds': 35, 'jpeg': 8, 'gif': 0,
                    'iff': 10, 'swft': 63, 'pict': 33, 'exr': 51, 'tif': 3,
                    'cin': 11, 'avi': 23, 'tga': 19, 'png': 32}

    def getFPS(self):

        options = {'pal': 25, 'game': 15, 'film': 24, 'ntsc': 30, 'show': 48,
                   'palf': 50, 'ntscf': 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        return options[option]

    def process(self, context):

        # getting output path
        render_globals = pymel.core.PyNode('defaultRenderGlobals')
        start_frame = render_globals.startFrame.get()

        # getting job data
        job_data = {}
        if context.has_data('deadlineData'):
            job_data = context.data('deadlineData')['job'].copy()

        # storing plugin data
        plugin_data = {'UsingRenderLayers': 1}

        tmp = str(pymel.core.system.Workspace.getPath().expand())
        plugin_data['ProjectPath'] = tmp

        plugin_data['Version'] = pymel.versions.flavor()
        plugin_data['Build'] = pymel.versions.bitness()

        drg = pymel.core.PyNode('defaultRenderGlobals')

        # arnold specifics
        if drg.currentRenderer.get() == 'arnold':
            plugin_data['Animation'] = 1

        # getting render layers data
        data = {}
        render_cams = []
        for layer in pymel.core.ls(type='renderLayer'):

            # skipping defaultRenderLayers
            if layer.name().endswith('defaultRenderLayer'):
                continue

            if 'defaultRenderLayer' in layer.name() and layer.isReferenced():
                continue

            layer_data = {}
            render_cams = []
            if layer.adjustments.get(multiIndices=True):
                for count in layer.adjustments.get(multiIndices=True):
                    if not layer.adjustments[count].plug.connections():
                        continue

                    if layer.adjustments[count].plug.connections()[0] == drg:
                        attr = layer.adjustments[count].plug.connections(plugs=True)[0]
                        layer_data[attr.name(includeNode=False)] = layer.adjustments[count].value.get()

                    for cam_attr in layer.adjustments[count].plug.connections(plugs=True, type='camera'):
                        if cam_attr.endswith('renderable') and layer.adjustments[count].value.get() == 1.0:
                            render_cams.append(pymel.core.PyNode(cam_attr.split('.')[0]))

                layer_data['renderpasses'] = layer.connections(type='renderPass')
            else:
                layer_data['renderpasses'] = layer.connections(type='renderPass')

            layer_data['cameras'] = render_cams
            data[layer.name()] = layer_data

        self.log.info(data)

        # getting path
        paths = [str(pymel.core.system.Workspace.getPath().expand())]
        try:
            paths.append(str(pymel.core.system.Workspace.fileRules['images']))
        except:
            pass

        tmp = pymel.core.rendering.renderSettings(firstImageName=True)[0]
        paths.append(str(tmp))

        path = os.path.join(*paths)

        padding = render_globals.extensionPadding.get()
        firstFrame = int(render_globals.startFrame.get())
        stringFrame = str(firstFrame).zfill(padding)
        if stringFrame in os.path.basename(path):
            tmp = '#' * padding
            basename = os.path.basename(path).replace(stringFrame, tmp)
            dirname = os.path.dirname(path)
            path = os.path.join(dirname, basename)

        extension = os.path.splitext(os.path.basename(path))[1]
        path = path.replace(extension, '{ext}')

        current_layer = pymel.core.nodetypes.RenderLayer.currentLayer()
        if current_layer.name() == 'defaultRenderLayer':
            path = path.replace('masterLayer', '{layer}')
        else:
            path = path.replace(current_layer.name(), '{layer}')

        # getting frames
        start_frame = int(render_globals.startFrame.get())
        end_frame = int(render_globals.endFrame.get())

        for layer in data:

            instance = context.create_instance(name=layer)
            instance.set_data('family', value='deadline.render')

            instance.set_data('data', value=data[layer])

            publish_state = pymel.core.PyNode(layer).renderable.get()
            instance.data['publish'] = publish_state

            # getting layer name
            if layer == 'defaultRenderLayer':
                layer_name = 'masterLayer'
            else:
                layer_name = layer

            # setting plugin_data
            plugin_data = plugin_data.copy()
            plugin_data['RenderLayer'] = layer_name

            try:
                plugin_data['Renderer'] = data[layer]['currentRenderer']
            except:
                plugin_data['Renderer'] = drg.currentRenderer.get()

            # setting job data
            job_data = job_data.copy()

            # getting frames
            start_frame = int(render_globals.startFrame.get())
            end_frame = int(render_globals.endFrame.get())

            if 'endFrame' in data[layer]:
                end_frame = int(data[layer]['endFrame'] * self.getFPS())
            if 'startFrame' in data[layer]:
                start_frame = int(data[layer]['startFrame'] * self.getFPS())

            frames = '%s-%s' % (start_frame, end_frame)
            instance.set_data('deadlineFrames', value=frames)

            ext = extension[1:]
            try:
                for key in self.imageFormats:
                    fmt = int(data[layer]['imageFormat'])
                    if self.imageFormats[key] == fmt:
                        ext = key
            except:
                pass
            ext = '.' + ext

            safe_layer_name = layer.replace(':', '_')
            job_data['OutputFilename0'] = path.format(layer=safe_layer_name,
                                                      ext=ext)

            deadline_data = {'job': job_data, 'plugin': plugin_data}
            instance.set_data('deadlineData', value=deadline_data)

            # adding ftrack data to activate processing
            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='img')

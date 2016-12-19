# Maya

The Maya publishing pipeline includes the following nodes; ```Set```, ```RenderLayer``` (legacy).

To publish any nodes output you have to first setup the scene, and then go to ```File > Publish```. Please see the individual node's setup section below.

### Set

To publish any objects in there scene (DAG nodes), you first have to collect what you want to publish in a set. The name of the set will determine the name of the output.

Once you have collected some nodes in a set, you can publish and choose what output format you want published. The current supported output formats are; ```Alembic```, ```MayaAscii``` and ```MayaBinary```.

<iframe width="560" height="315" src="https://www.youtube.com/embed/F6_4sVSxHGg" frameborder="0" allowfullscreen></iframe>

Which output format you decide on, is stored in the scene so you don't have to setup the scene again. This data is stored as attributes on the set.

### RenderLayer (Legacy)

To publish any renderlayer's output, you have to create a renderlayer. The default ```masterLayer``` will not be considered for publishing.

The renderable state of a renderlayer determines whether it gets published or not. The enabled/disabled state in the UI reflects into the scene, so you can save the scene and be sure its the same publish next time you open it.

Currently you can only render a single camera per renderlayer. You will be prompted to change this while publishing.

<iframe width="560" height="315" src="https://www.youtube.com/embed/lC0IJKjP3iw" frameborder="0" allowfullscreen></iframe>

### Instances

Please read about the instances you can encounter [here](instances.md)

### Remote Rendering/Processing

To send a scene off to be processed on another machine, with a render farm or cloud computing, you'll need to enable the ```Remote``` attribute. You can either add this attribute manually or once opening the Pyblish UI it'll add this attrbute.

On ```Set```s you will find this easily in the channelbox, once the ```Set``` is selected.

On ```RenderLayer```s (legacy) you will have to select the ```RenderLayer``` first to access the ```Remote``` attribute. To select a ```RenderLayer``` either select it in the renderlayers overview and go to ```Layers > Attributes```, or select it in the ```Outliner``` by disabling ```Display > DAG Objects Only``` whereby you can select the renderlayer in the ```Outliner```.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_CtifGbiOQ4" frameborder="0" allowfullscreen></iframe>

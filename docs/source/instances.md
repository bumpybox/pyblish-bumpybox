# Instances

When publishing you will be presented with all the instances that were found in the scene. There are three main types of instances you will encounter; ```local```, ```remote``` and ```output```.

#### ```local```

This instance represents any node that will be processed on the local machine ei. the machine you publish from. They will be labelled with the name of the node like this; ```name - type - local```.

Examples:

- ```mantra1 - mantra - local```
- ```alembic1 - alembic - local```
- ```geometry1 - geometry - local```
- ```set1_alembic - alembic - local```
- ```set1_mayaAscii - mayaAscii - local```
- ```set1_mayaBinary - mayaBinary - local```
- ```defaultRenderLayer1 - renderlayer - local```

#### ```remote```

This instance represents any node that will be processed remotely ei. by a render remote or other computing management like cloud computing. They will be labelled with the name of the node like this; ```name - type - remote```.

Examples:

- ```mantra1 - mantra - remote```
- ```alembic1 - alembic - remote```
- ```geometry1 - geometry - remote```
- ```set1_alembic - alembic - remote```
- ```set1_mayaAscii - mayaAscii - remote```
- ```set1_mayaBinary - mayaBinary - remote```
- ```defaultRenderLayer1 - renderlayer - remote```

#### ```output```

This instance represents any nodes output that already exists ei. alembic files from an alembic node or image files from a mantra node. They will be labelled with the name of the node and the collection of files like this; ```node - collection```.

Examples:

- ```mantra1 - task_name.v001_mantra1_vm_picture.%04d.exr [1-2]```
- ```alembic1 - task_name.v001_alembic2_filename.%04d.abc [1]```
- ```geometry - task_name.v001_geometry2_sopoutput.%04d.bgeo.sc [1-2]```
- ```defaultRenderLayer1 - maya_defaultRenderLayer1.%04d.png [1-10]```
- ```set1_alembic - maya_set1_alembic.%04d.abc [1]```
- ```set1_mayaAscii - maya_set1_mayaAscii.%04d.abc [1]```
- ```set1_mayaBinary - maya_set1_mayaBinary.%04d.abc [1]```

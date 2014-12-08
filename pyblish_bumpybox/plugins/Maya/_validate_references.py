import os
import re

import maya.cmds as cmds

refs = cmds.ls(type='reference')

for ref in refs:
    #getting reference data
    path = cmds.referenceQuery(ref, f=True)
    name = os.path.basename( path )

    #generate regex file version pattern
    versionPattern = r'(([v])([0-9]{3})).*'
    startStr = re.findall(versionPattern, name)[0][0]
    startStr = name.split(startStr)[0]
    pattern = r'(\b' + startStr + ')' + versionPattern

    #finding versions
    versions = []
    for f in os.listdir(os.path.dirname(path)):
        if re.match(pattern, f):
            versions.append(f)

    #finding latest version
    count = 0
    latestName = None
    for version in versions:
         versionNumber = re.findall(versionPattern, version)[0][-1]
         if count < int(versionNumber):
             count = int(versionNumber)
             latestName = version

    #validation
    if latestName != name:
        print 'Validation failed!'
        print 'Current version is not the latest!'
        print 'Current version: "{0}"'.format(name)
        print 'Latest version: "{0}"'.format(latestName)
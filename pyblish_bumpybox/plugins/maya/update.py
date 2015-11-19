import os
import re
import traceback

import pymel
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


class Reference(pyblish.api.Action):

    label = 'Update Reference'

    def process(self, context):

        errors = False
        try:
            for node in pymel.core.ls(type='reference'):
                if 'sharedReferenceNode' in node.name():
                    continue

                if node.isReferenced():
                    continue

                file_ref = pymel.core.system.FileReference(node)
                try:
                    self.log.info(file_ref.path)
                except:
                    continue

                if not file_ref.isLoaded():
                    continue

                file_ref =  pymel.core.system.FileReference(node)
                basename = os.path.basename(file_ref.path)

                if self.get_latest_version(node) != basename:
                    new_basename = self.get_latest_version(node)
                    new_path = os.path.join(os.path.dirname(file_ref.path),
                                                                    new_basename)

                    file_ref.replaceWith(new_path)
        except:
            errors = True
            self.log.error(traceback.format_exc())

        if errors:
            message_box(context, 'Reference update completed with errors!',
                        'Update', warning=True)
        else:
            message_box(context, 'Reference update completed successfully!',
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


    def version_set(self, string, prefix, oldintval, newintval):
      """Changes version information from filenames used by DD (and Weta, apparently)
      These are _v# or /v# or .v# where v is a prefix string, in our case
      we use "v" for render version and "c" for camera track version.
      See the version.py and camera.py plugins for usage."""

      regex = "[/_.]"+prefix+"\d+"
      matches = re.findall(regex, string, re.IGNORECASE)
      if not len(matches):
        return ""

      # Filter to retain only version strings with matching numbers
      matches = filter(lambda s: int(s[2:]) == oldintval, matches)

      # Replace all version strings with matching numbers
      for match in matches:
        # use expression instead of expr so 0 prefix does not make octal
        fmt = "%%(#)0%dd" % (len(match) - 2)
        newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
        string = re.sub(match, newfullvalue, string)
      return string

    def get_latest_version(self, node):

        file_ref =  pymel.core.system.FileReference(node)
        basename = os.path.basename(file_ref.path)
        version_string = self.version_get(basename, 'v')[1]
        version = int(version_string)
        head = basename.split(version_string)[0]
        ext = os.path.splitext(basename)[1]

        max_version = version
        path = basename
        for f in os.listdir(os.path.dirname(file_ref.path)):
            if ext != os.path.splitext(f)[1]:
                continue

            # fail safe against files without version numbers
            try:
                f_version_string = self.version_get(f, 'v')[1]
            except:
                continue

            if head != f.split(f_version_string)[0]:
                continue

            v = int(self.version_get(f, 'v')[1])
            if max_version < v:
                max_version = v
                path = f

        return path


class Update(pyblish.api.Plugin):

    actions = [Reference]

    def process(self, context):

        pass

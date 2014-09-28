import os
import shutil

import pyblish.api


@pyblish.api.log
class ConformAll(pyblish.api.Extractor):
    """
    """

    families = ['all']
    hosts = ['maya']
    version = (0, 1, 0)

    def removeEmptyFolders(self, path, removeRoot=True):
        'Function to remove empty folders'
        if not os.path.isdir(path):
            return
        
        # remove empty subfolders
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self.removeEmptyFolders(fullpath)
        
        # if folder empty, delete it
        files = os.listdir(path)
        if len(files) == 0 and removeRoot:
            self.log.info('Removing empty folder: {0}'.format(path))
            os.rmdir(path)

    def process_instance(self, instance):
        """
        """
        commit_dir = instance.data('commit_dir')
        filename = instance.data('filename')
        filepath = os.path.join(commit_dir, filename)
        cwd = instance.context.data('cwd')
        parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))
        relative_dir = os.path.relpath(commit_dir, cwd)
        root_publish = os.path.join(cwd, relative_dir.split(os.sep)[0])

        self.log.info('Conforming {0} to {1}'.format(filepath, parent_dir))
        shutil.copy(filepath, parent_dir)
        os.remove(filepath)

        self.log.info('Clearing cache...')
        self.removeEmptyFolders(root_publish)
        
        self.log.info("Conform successful.")

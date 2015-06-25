import ftrack

import pyblish.api
import pyblish_qml


@pyblish.api.log
class SelectContextLabel(pyblish.api.Selector):
    """
    """

    order = pyblish.api.Selector.order + 0.2

    def process(self, context):

        # skipping instance if ftrackData isn't present
        if not context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        ftrack_data = context.data('ftrackData')

        # setting context label
        task = ftrack.Task(ftrack_data['Task']['id'])
        path = [task.getName()]
        for p in task.getParents():
            path.append(p.getName())

        path = ' / '.join(list(reversed(path)))
        pyblish_qml.settings.WindowTitle = path

import os

import pyblish.api


pyblish.api.register_host('aftereffects')


class CollectEnviromentArgs(pyblish.api.Collector):
    """ Collects all keyword arguments passed from the terminal """

    order = pyblish.api.Collector.order - 0.1

    def process(self, context):

        data = {}
        args = os.environ['PYBLISHARGUMENTS']
        self.log.info(args)
        for arg in args.split('--'):
            if arg:
                if '"' in arg:
                    key = arg.split('"')[0].replace(' ', '')
                    values = []
                    for v in arg.split('"')[1:]:
                        if v not in ['', ' ']:
                            values.append(v)

                    if key in data:
                        data[key].append(values)
                    else:
                        data[key] = [values]

        context.set_data('environmentArgs', value=data)

        # adding scene to context
        path = ''
        try:
            path = data['scene'][0][0]
        except:
            self.log.warning('No scene found!')

        context.set_data('currentFile', value=path)

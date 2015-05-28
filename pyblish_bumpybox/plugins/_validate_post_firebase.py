import datetime
import requests

import pyblish.api


@pyblish.api.log
class PostValidatorFirebase(pyblish.api.Validator):

    order = pyblish.api.Validator.order + 0.5
    families = ['*']
    hosts = ['nuke']
    optional = True

    def process_context(self, context):
        """TODO:
        - Add nuke node data"""
        results = context.data("results")
        endpoint = "https://pyblish.firebaseio.com/bait/failures.json"
        time = datetime.datetime.today().strftime("%a %b %d %H:%M:%S %Y")

        self.log.info("Were there any errors?")

        errors = False
        for result in results:
            if result.get("error"):
                errors = True

        if errors:
            self.log.info("Yes there were, writing to: %s" % endpoint)

            instances = list()
            for instance in context:
                data = {}
                for knob in instance[0].allKnobs():
                    key = knob.name()
                    value = knob.value()
                    if not key:
                        continue
                    data[key] = value

                instances.append({"name": instance.name, "data": data})

            firebase = {
                "time": time,
                "data": context.data(),
                "children": instances
            }
            response = requests.post(endpoint, json=firebase)

            if not response.status_code == 200:
                raise pyblish.api.ValidationError(
                    "Could not post data to Firebase")

            self.log.info("Results successfully posted to firebase")
        else:
            self.log.info("No errors")

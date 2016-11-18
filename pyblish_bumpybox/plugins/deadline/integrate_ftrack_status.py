import pyblish.api


class BumpyboxDeadlineIntegrateFtrackStatus(pyblish.api.ContextPlugin):

    order = pyblish.api.IntegratorOrder - 0.1
    label = "Ftrack Status"

    def process(self, context):

        instances = {}
        instances_order = []
        instances_no_order = []

        for instance in context:

            if not instance.data.get("publish", True):
                continue

            # skipping instance if not part of the family
            if "deadline" not in instance.data.get("families", []):
                msg = "No \"deadline\" family assigned. "
                msg += "Skipping \"%s\"." % instance
                self.log.info(msg)
                continue

            if "order" in instance.data("deadlineData"):
                order = instance.data("deadlineData")["order"]
                instances_order.append(order)
                if order in instances:
                    instances[order].append(instance)
                else:
                    instances[order] = [instance]
            else:
                instances_no_order.append(instance)

        instances_order = list(set(instances_order))
        instances_order.sort()

        new_context = []
        for order in instances_order:
            for instance in instances[order]:
                new_context.append(instance)

        if not instances_order:
            new_context = instances_no_order

        if not new_context:
            return

        for instance in new_context[:-1]:
            data = instance.data["deadlineData"]["job"]
            if "ExtraInfoKeyValue" in data:
                data["ExtraInfoKeyValue"]["FT_StatusUpdate"] = False
            instance.data["ftrackStatusUpdate"] = False

        data = new_context[-1].data["deadlineData"]["job"]
        if "ExtraInfoKeyValue" in data:
            data["ExtraInfoKeyValue"]["FT_StatusUpdate"] = True
        new_context[-1].data["ftrackStatusUpdate"] = True

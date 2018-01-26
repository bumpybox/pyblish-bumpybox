from pyblish import api


class InstancePlugin(api.InstancePlugin):

    class_name = ""


class ContextPlugin(api.ContextPlugin):

    class_name = "default"


class Collector(api.Collector):

    class_name = "default"


class Validator(api.Validator):

    class_name = "default"


class Extractor(api.Extractor):

    class_name = "default"


Action = api.Action

Subset = api.Subset
Exact = api.Exact

CollectorOrder = api.CollectorOrder
ValidatorOrder = api.ValidatorOrder
ExtractorOrder = api.ExtractorOrder
IntegratorOrder = api.IntegratorOrder

register_host = api.register_host
log = api.log

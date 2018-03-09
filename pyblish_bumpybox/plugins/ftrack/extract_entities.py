from pyblish import api
from pyblish_bumpybox import inventory


class ExtractProject(api.ContextPlugin):
    """Extract an Ftrack project from context.data["ftrackProjectData"]"""

    order = inventory.get_order(__file__, "ExtractProject")
    label = "Ftrack Project"
    hosts = ["nukestudio"]

    def process(self, context):

        session = context.data["ftrackSession"]

        data = {}
        for key, value in context.data["ftrackProjectData"].iteritems():
            if not value:
                continue

            data[key] = value

        # Get project from data
        query = "Project where "
        for key, value in data.iteritems():
            query += "{0} is \"{1}\" and ".format(key, value)
        query = query[:-5]

        project = session.query(query).first()

        # Create project if it does not exist
        if not project:
            self.log.info("Creating project with data: {0}".format(data))
            project = session.create("Project", data)
            session.commit()

        context.data["ftrackProject"] = project


def ensure_entity(instance, entity_type):

    session = instance.context.data["ftrackSession"]

    parent_entity = instance.data["parent"].data.get("entity", None)
    if parent_entity is None:
        parent_entity = instance.context.data["ftrackTask"]["parent"]

    # Query existence of entity
    entity = session.query(
        '{0} where parent.id is "{1}" and name is "{2}"'.format(
            entity_type,
            parent_entity["id"],
            instance.data["name"]
        )
    ).first()
    # Create entity if non-existent
    if not entity:
        entity = session.create(
            entity_type,
            {
                "parent": parent_entity,
                "name": instance.data["name"]
            }
        )

    return entity


class ExtractEpisode(api.InstancePlugin):
    """Creates ftrack episodes by the name of the instance."""

    order = inventory.get_order(__file__, "ExtractEpisode")
    families = ["ftrackEntity", "episode"]
    match = api.Subset
    label = "Ftrack Episode"
    optional = True

    def process(self, instance):

        instance.data["entity"] = ensure_entity(instance, "Episode")
        instance.data["item"] = instance.data["parent"].data["item"]


class ExtractSequence(api.InstancePlugin):
    """Creates ftrack sequences by the name of the instance."""

    order = inventory.get_order(__file__, "ExtractSequence")
    families = ["ftrackEntity", "sequence"]
    match = api.Subset
    label = "Ftrack Sequence"
    optional = True

    def process(self, instance):

        instance.data["entity"] = ensure_entity(instance, "Sequence")
        instance.data["item"] = instance.data["parent"].data["item"]


class ExtractShot(api.InstancePlugin):
    """Creates ftrack shots by the name of the instance."""

    order = inventory.get_order(__file__, "ExtractShot")
    families = ["ftrackEntity", "shot"]
    match = api.Subset
    label = "Ftrack Shot"
    optional = True

    def process(self, instance):
        entity = None

        # If parent of task is a shot, we'll grab that.
        if instance.context.data["ftrackTask"]["parent"].entity_type == "Shot":
            entity = instance.context.data["ftrackTask"]["parent"]
        else:
            entity = ensure_entity(instance, "Shot")

        instance.data["entity"] = entity

        instance.data["item"] = instance.data["parent"].data["item"]

        # Assign attributes to shot
        attributes = {
            "handles": instance.data["handles"],
            "fstart": instance.data["fstart"],
            "fend": instance.data["fend"],
            "fps": instance.data["fps"],
            "width": instance.data["width"],
            "height": instance.data["height"],
        }

        for key, value in attributes.iteritems():
            try:
                entity["custom_attributes"][key] = value
            except Exception as e:
                self.log.warning("Could not set the attribute: " + str(e))

        # Assign thumbnail if available
        if "thumbnail" in instance.data.keys():
            entity.create_thumbnail(instance.data["thumbnail"])


class ExtractAssetDataNukeStudio(api.ContextPlugin):
    """Changes the parent of the review component."""

    order = inventory.get_order(__file__, "ExtractAssetDataNukeStudio")
    label = "Ftrack Link Review"
    optional = True
    hosts = ["nukestudio"]

    def process(self, context):

        data = {}
        for instance in context:
            families = [instance.data["family"]]
            families += instance.data.get("families", [])

            name = instance.data["name"].split("--")[-1]
            instance_data = data.get(name, {})
            if "review" in families:
                instance_data["review"] = instance
            if "trackItem.ftrackEntity.shot" in families:
                instance_data["shot"] = instance

            data[name] = instance_data

        for name, instance_data in data.iteritems():
            if not instance_data:
                continue
            asset_data = instance_data["review"].data.get("asset_data", {})
            asset_data["parent"] = instance_data["shot"].data["entity"]
            instance_data["review"].data["asset_data"] = asset_data


class ExtractTasks(api.InstancePlugin):
    """Creates ftrack shots by the name of the instance."""

    order = inventory.get_order(__file__, "ExtractTasks")
    families = ["trackItem.ftrackEntity.task"]
    label = "Ftrack Tasks"
    optional = True

    def process(self, instance):
        session = instance.context.data["ftrackSession"]

        task_type = session.query(
            'Type where name is "{0}"'.format(instance.data["type"])
        ).one()

        query = (
            'Task where type.name is "{0}" and name is "{1}" and '
            'parent.id is "{2}"'
        )
        task = session.query(
            query.format(
                instance.data["type"],
                instance.data["name"],
                instance.data["parent"].data["entity"]["id"]
            )
        ).first()

        if not task:
            task = session.create(
                "Task",
                {
                    "name": instance.data["name"],
                    "type": task_type,
                    "parent": instance.data["parent"].data["entity"]
                }
            )

        instance.data["entity"] = task


class ExtractLinkAssetbuilds(api.ContextPlugin):
    """Link Assetbuilds to shot."""

    order = inventory.get_order(__file__, "ExtractLinkAssetbuilds")
    families = ["trackItem.ftrackEntity.assetbuild"]
    label = "Ftrack Link Assetbuilds"
    optional = True
    hosts = ["nukestudio"]

    def process(self, context):

        instances = []
        shots = []
        for instance in context:
            families = [instance.data["family"]]
            families += instance.data.get("families", [])
            if "trackItem.ftrackEntity.assetbuild" not in families:
                continue

            instances.append(instance)

            shot = instance.data["shot"].data["entity"]
            if shot not in shots:
                shots.append(shot)

        if not instances:
            return

        session = instance.context.data["ftrackSession"]

        # Clear existing links
        for shot in shots:
            for link in shot["incoming_links"]:
                session.delete(link)
                session.commit()

        # Create new links
        for instance in instances:
            assetbuild = session.get("AssetBuild", instance.data["id"])
            shot = instance.data["shot"].data["entity"]
            self.log.debug(
                "Creating link from {0} to {1}".format(
                    assetbuild["name"], shot["name"]
                )
            )
            session.create(
                "TypedContextLink", {"from": assetbuild, "to": shot}
            )


class ExtractCommit(api.ContextPlugin):
    """Commits the Ftrack session for entities."""

    order = inventory.get_order(__file__, "ExtractCommit")
    label = "Ftrack Commit"

    def process(self, context):

        context.data["ftrackSession"].commit()


class ExtractNukeStudio(api.InstancePlugin):
    """Sets the Ftrack data for NukeStudio components."""

    order = inventory.get_order(__file__, "ExtractNukeStudio")
    label = "Ftrack NukeStudio"
    families = ["trackItem.task"]
    hosts = ["nukestudio"]

    def process(self, instance):
        # Asset data
        data = instance.data.get("asset_data", {})
        parent = instance.data["parent"]
        data["parent"] = parent.data["shotInstance"].data["entity"]
        instance.data["asset_data"] = data

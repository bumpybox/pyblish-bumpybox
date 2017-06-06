# Ftrack

It is possible to publish existing output instances directly from Ftrack, without having to launch an application like Maya or Nuke.

For an output instance to be available in Ftrack, you will have to have published the local or remote instance first. You can read more about the different instances [here](http://pyblish-bumpybox.readthedocs.io/en/latest/workflow.html#output).

Common Workflow:

- Publish a remote instance to be processed on a farm.
- Wait for the processing to be done.
- Publish from Ftrack.
 - Launch Actions in Ftrack on the task.
 - Select the <img width="40" alt="portfolio_view" src="https://raw.githubusercontent.com/pyblish/pyblish-ftrack/master/pyblish_ftrack/ftrack_event_plugin_path/icon.png"> action.

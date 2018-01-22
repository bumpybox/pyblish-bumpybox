import pyblish.api


class CopyToClipboardAction(pyblish.api.Action):

    label = "Copy To Clipboard"
    on = "all"

    def process(self, context, plugin):
        import pyperclip

        header = "{:<10}{:<40} -> {}".format("Success", "Plug-in", "Instance")
        result = "{success:<10}{plugin.__name__:<40} -> {instance}"
        error = "{:<10}+-- EXCEPTION: {:<70}"
        record = "{:<10}+-- {level}: {message:<70}"

        results = list()
        for r in context.data["results"]:
            # Format summary
            results.append(result.format(**r))

            # Format log records
            for lr in r["records"]:
                lines = str(lr.msg).split("\n")
                msg = lines[0]
                for line in lines[1:]:
                    msg += "\t\t\t\t\t" + line
                data = record.format("", level=lr.levelname, message=msg)
                results.append(data)

            # Format exception (if any)
            if r["error"]:
                lines = str(r["error"]).split("\n")
                msg = lines[0]
                for line in lines[1:]:
                    msg += "\t\t\t\t\t" + line
                results.append(error.format("", msg))

        report = "{header}\n{line}\n{results}".format(
            header=header, results="\n".join(results), line="-" * 70
        )
        pyperclip.copy(report)


class Report(pyblish.api.ContextPlugin):
    """ Report plugin. """

    label = "Report"
    actions = [CopyToClipboardAction]

    def process(self, context):

        pass

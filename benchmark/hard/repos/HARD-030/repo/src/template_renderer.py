import re


class TemplateRenderError(Exception):
    pass


def render_template(template, context):
    def replace(match):
        name = match.group(1)
        try:
            return str(context[name])
        except KeyError as exc:
            raise TemplateRenderError(f"missing variable {name}") from exc

    return re.sub(r"{([A-Za-z_][A-Za-z0-9_]*)}", replace, template)

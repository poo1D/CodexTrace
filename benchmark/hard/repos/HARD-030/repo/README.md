# template-renderer

`render_template(template, context)` renders placeholders using values from `context`.

Syntax:

- `{name}` inserts `str(context["name"])`.
- Placeholder names contain letters, digits, and underscores, and must not start with a digit.
- `{{` renders a literal `{`.
- `}}` renders a literal `}`.
- Missing variables raise `TemplateRenderError` with the missing variable name and its line/column location.

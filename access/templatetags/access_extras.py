from django import template


register = template.Library()


@register.filter
def get_item(form, module_id):
    return form[f"module_{module_id}"]

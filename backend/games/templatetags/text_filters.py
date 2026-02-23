from django import template

register = template.Library()


@register.filter
def smart_truncate(content):
    if not content or len(content) <= 40:
        return content

    limit_soft = 35
    limit_hard = 50

    space_index = content.find(" ", limit_soft)

    if space_index != -1 and space_index <= limit_hard:
        return content[:space_index] + "..."

    if len(content) > limit_hard:
        return content[:limit_hard] + "..."

    return content
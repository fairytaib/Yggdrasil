# familytree/templatetags/tree_tags.py
from django import template
from familytree.models import Person
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def show_family_tree(person):
    def render_node(p):
        if not p:
            return ""

        children_html = "".join([
            render_node(child) for child in p.children.all()
            ])

        return f"""
        <li>
            <div class="person">
                {p.first_name} {p.last_name}
            </div>
            {"<ul>" + children_html + "</ul>" if children_html else ""}
        </li>
        """

    html = f"<ul>{render_node(person)}</ul>"
    return mark_safe(html)

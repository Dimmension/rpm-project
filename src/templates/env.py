from typing import Union, Any

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('src', 'templates'),
    autoescape=select_autoescape()
)


def render(template_name: str, **kwargs: Union[int, str, dict[str, Any]]) -> str:
    return env.get_template(template_name).render(**kwargs)

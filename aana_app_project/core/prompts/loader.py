from jinja2 import Environment, PackageLoader, Template


def get_prompt_template(name: str) -> Template:
    """Load a prompt template by name.

    Use this function to load a prompt templates for LLMs:

    ```python
    from aana_app_project.core.prompts.loader import get_prompt_template

    template = get_prompt_template("test")
    prompt = template.render(your_variable="your_value")
    ```

    Args:
        name (str): The name of the prompt template.

    Returns:
        Template: The prompt template.
    """
    env = Environment(loader=PackageLoader(
        "aana_app_project", "core", "prompts"))
    template = env.get_template(f"{name}.j2")
    return template

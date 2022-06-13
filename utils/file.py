import jinja2
import os

def get_content_from_template(name:str,**kwargs) -> str:
    """
    Returns a string representation of a templated file with given variables rendered in.
    """
    # load the template engine to search in templates folder
    templateLoader = jinja2.FileSystemLoader(searchpath=os.environ["JJ_TEMPLATE_FOLDER_PATH"])
    templateEnv = jinja2.Environment(loader=templateLoader)

    # render the template with the variables
    template = templateEnv.get_template(name)
    return template.render(**kwargs)

from os import path
import yaml # pip install pyyaml

def yaml_include(loader, node):
    with open(node.value) as file:
        return load(file, master=loader)

yaml.add_constructor("!include", yaml_include, Loader=yaml.SafeLoader)

def load(stream, Loader=yaml.SafeLoader, master=None):
    loader = Loader(stream)
    if master is not None:
        loader.anchors = master.anchors
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()

def loadYaml(source):
    if not path.exists(source):
        return None
    with open(source, 'r') as file:
        return load(file)



from functools import partial
import logging
from pathlib import Path
from docgen.settings import settings
import yaml

logger = logging.getLogger(__name__)

def read_yml(path:Path):
    if not path.exists():
        return {}
    with open(path, 'r', encoding=settings.yml_encoding) as f:
        return yaml.safe_load(f) or {}
    logger.debug(f"{path} lu")
    
def to_yml( path:Path,data: dict):
    """
    Écrit un dictionnaire dans un fichier YAML.
    """
    with open(path, 'w', encoding=settings.yml_encoding) as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
    logger.debug(f"{path.name} mis à jour dans {path}")


def update_path(data,path,source,keys):
    parts = path.split(".")
    data = data
    for p in parts:
        if p:
            data = data[p]
    if isinstance(source,dict):
        getter = source.get
    else:
        getter = lambda k:getattr(source,k,None)
    for key in keys:
        if key not in data:
            value = getter(key)
            if value is not None:
                data[key] = value
            else:
                logger.debug(f"Clé '{key}' non trouvée dans {source}.")
        else:
            logger.debug(f"Clé '{key}' non trouvée dans le chemin '{path}'.")  


def nested_update(data,source,path_options={}):
    """
    Met à jour les clés dans un dictionnaire imbriqué.

    Si keys not None, keys doit avoir la même structure que source et data. Seul les clefs présentes seront considérées.
    """
    assert isinstance(data, dict), "data doit être un dictionnaire"
    assert isinstance(source,dict, "source doit être un dictionnaire")
    
    if isinstance(data, dict):
        for key in data.keys():
            value = data[key]
            if isinstance(value, dict):
                if key in source:
                    nested_update(value, source[key], None)
            else:
                src_value = source.get(key, None)
                if isinstance(value, list) and isinstance(src_value, list):
                    data[key].extend(src_value)
                
    else:
        logger.warning(f"Le type de données {type(data)} n'est pas un dictionnaire.")
import logging
import sys


logger = logging.getLogger('docgen')

def get_log_level(str_:bool=False) -> int | str:
    """
    Retourne le niveau de log actuel du logger 'docgen'.
    """
    int_ = logger.getEffectiveLevel()
    if str_:
        return logging.getLevelName(int_)
    return int_

def setup_logging(level,log_file=None,log_format=None):
    """
    Si logger n'a pas de handler et pas de level défini, on ajoute un handler par défaut et on le met à INFO.
    """
    logger = logging.getLogger('docgen')
    if logger.handlers:
        logger.handlers.clear()  # Clear existing handlers to avoid duplicates
    
    # If no handlers are set, add a default console handler
    # En présence d'un fichier on ne log en console que les infos et plus, sinon on log tout
    handler = logging.StreamHandler(sys.stdout)
    if log_file:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(level)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        if log_format:
            formatter = logging.Formatter(log_format)
        else:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    logger.setLevel(level) 
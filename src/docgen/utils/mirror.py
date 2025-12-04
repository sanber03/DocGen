import copy
import logging
from pathlib import Path
import shutil

from docgen.utils.path import has_been_modified
from tqdm import tqdm


logger = logging.getLogger(__name__)

class _BarController:
    def __init__(self,bar):
        self.bar = bar
        self.counter = 0
        self.next_total = None

    def update(self,message:str=None,next_total=None):
        if message:
            self.bar.set_description(message)
        if next_total is not None:
            self.end()
            self.next_total = next_total
            self.counter = 0
        elif self.counter<self.next_total:
            self.counter += 1
            self.bar.update(1)

    def end(self):
        if self.next_total is None:
            return
        self.bar.update(self.next_total - self.counter)

def mirror(source_dir:Path,dest_dir:Path,rm_orphans:bool=True,excluded: list[Path] = None,kept_orphans: list[Path] = None):
    _kept_orphans = copy.deepcopy(kept_orphans) or None
    # === DETERMINER LE REPERTOIRE SOURCE === 
    # === VÉRIFICATION CONFLIT FICHIER/DOSSIER ===
    """ 
    Problème évité : Si un FICHIER nommé .build existe, mkdir() plante
    Solution : Détecter le conflit et donner un message clair à l'utilisateur """
    if dest_dir.exists() and dest_dir.is_file():
        raise FileExistsError(
            f"Impossible de créer le répertoire '{dest_dir}' : un fichier de ce nom existe déjà."
            f"Veuillez renommer ou supprimer ce fichier avant de continuer."
        )

    dest_dir.mkdir(parents=True,exist_ok=True)

    if not source_dir.exists():
        raise FileNotFoundError(f"Le répertoire source '{source_dir}' n'existe pas.")
    
    
    # === COPIE RÉCURSIVE AVEC EXCLUSIONS ===
    logger.info(f"Synchronisation de {source_dir}")
    logger.info(f"\t vers {dest_dir}")

    with tqdm(desc="... synchronisation",total=100) as synchronize_bar:
        bar_controller = _BarController(synchronize_bar)
        bar_controller.update(next_total=50)


        """
        Conditions de copie :
        1. Fichier n'existe pas dans .build/ -> COPIER (nouveau)
        2. Fichier source plus récent -> COPIER (modifié)
        3. Fichier identique/plus ancien -> IGNORER (économie)
        
        st_mtime = timestamp de dernière modification
        Plus le nombre est grand = plus récent
        
        Exemples :
        - source mtime=1000, build mtime=800 -> 1000 > 800 = True -> COPIER
        - source mtime=500, build mtime=600 -> 500 > 600 = False -> IGNORER
        """
        def _recursive_copy(current_source):
            for item in current_source.iterdir():
                if item == dest_dir or dest_dir in item.parents:
                    continue
                if excluded and item in excluded:
                    continue
                relative_path = item.relative_to(source_dir)
                target = dest_dir / relative_path
                logger.debug(f"{item} -> {target}")
                bar_controller.update()
                if item.is_file():
                    # pour chaque fichier différentielle
                    if not target.exists() or has_been_modified(item, target, hash=False):
                        try:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, target) # Copy métadata dont mtime pour la bonne comparaison
                            logger.debug(f"Copié: {relative_path}")
                        except Exception as e:
                            logger.warning(f"Erreur copie {relative_path}: {e}")
                elif item.is_dir():
                    try:
                        target.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        logger.warning(f"Erreur création répertoire {relative_path}: {e}")
                    _recursive_copy(item)  # Appel récursif pour les sous-répertoires


        _recursive_copy(source_dir)
        
        # pour chaque fichier .build supprimé dans src on propage la suppression 
        
        # === DÉTECTION DES FICHIERS ORPHELINS ===
        """
        Principe : Tout fichier dans .build/ DOIT avoir un équivalent dans source.
                Si un fichier existe dans .build/ mais plus dans source -> orphelin à supprimer.
        
        Méthode (logique inverse) :
        1. Parcourir TOUS les éléments de build_dir/ (fichiers + dossiers)
        2. Pour chaque élément :
        - Calculer son chemin relatif par rapport à .build/
        - Reconstruire le chemin équivalent dans source  
        - Vérifier si cet équivalent existe encore
        - Si NON -> ajouter à la liste de suppression
        """
        bar_controller.update(next_total=50)
        if rm_orphans:
            items_to_remove = []
            for item in dest_dir.rglob("*"):
                if _kept_orphans and item in _kept_orphans:
                    continue
                if _kept_orphans and item.parent in _kept_orphans:
                    if item.is_dir():
                        _kept_orphans.append(item)
                    continue
                relative_path = item.relative_to(dest_dir)
                source_item = source_dir / relative_path
                
                if not source_item.exists():
                    items_to_remove.append((item, relative_path))

            # Supprimer d'abord les fichiers, puis les répertoires (ordre important)
            for item, relative_path in filter(lambda x:x[0].is_file(), items_to_remove):
                logger.debug(f"rm {relative_path}")
                bar_controller.update()
                try:
                    item.unlink()
                except Exception as e:
                    logger.warning(f"Erreur suppression {relative_path}: {e}")

            for item, relative_path in filter(lambda x:x[0].is_dir(), reversed(items_to_remove)): # parcours dans le sens inverse = du plus profond au moins profond
                logger.debug(f"rm {relative_path}")
                bar_controller.update()
                try:
                    if not any(item.iterdir()):  # Seulement si vide
                        item.rmdir()
                except Exception as e:
                    logger.warning(f"Erreur suppression {relative_path}: {e}")
        bar_controller.end()

if __name__=="__main__":
    from docgen.settings import settings
    logging.basicConfig(level=logging.DEBUG)
    mirror(settings.examples_path / "minimal_example",settings.examples_path / "minimal_example2")
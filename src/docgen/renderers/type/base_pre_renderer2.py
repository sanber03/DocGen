import copy
from dataclasses import dataclass
import logging
from docgen.renderers.renderer import Renderer
from docgen.renderers.type.abstract import TypeRenderer
from docgen.utils.mirror import mirror
from docgen.settings import settings
from docgen.quarto import run as quarto_run
from docgen.utils.yml import  to_yml

logger = logging.getLogger(__name__)


@dataclass
class BasePreRenderer2(TypeRenderer):
    """
    Base class for all pre-renderers-2, c'est à dire manipulant le _quarto.yml avant le rendu.

    En charge de :
    - Valider les formats, selon le type de projet, les formats peuvent être modifiés
    """
    formats: list[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.formats = self.validate_formats(self.formats)
        
    def validate_formats(self,formats) -> list[str]:
        """
        Retourne la liste des formats par défaut pour ce type de projet.
        """
        return settings._enforce_list(formats) or settings.get_default_formats()
    
    def get_files_to_render(self) -> list[str]|None:
        pass

    def prepare_quarto_yml_content(self)->dict:
        """
            En fonction des fonctionnalités demandée, pour le type de projet demandé et 
            les formats demandés, on modifie en place le quarto.yml
        """

        params = copy.deepcopy(self.parent.base_quarto_yml_content)
        
        # === INJECTION PARAMÈTRES PROJECT ===

        # PROBLÈME: Dès qu'un _quarto.yml existe, Quarto considère le répertoire comme un "projet"
        # et refuse --output-dir pour les fichiers individuels (quarto render fichier.md --output-dir).
        # SOLUTION ?!
            # 1. Accepter que ce soit un "projet" (on peut garder type: default)
            # 2. Mais spécifier project.render = [fichier_voulu] pour limiter le rendu
            # 3. Utiliser "quarto render" (sans nom de fichier) pour rendre le projet
            # 4. Quarto ne rendra que le fichier listé dans project.render
            # 5. --output-dir devient autorisé car c'est un rendu de "projet"

        #L'utilisateur peut faire "docgen render fichier.md" et on rend
        # seulement fichier.md avec --output-dir, tout en gardant le contexte du répertoire.
        
        params.setdefault("project", {})
        yml_project_type = params["project"].get("type", None)
        if yml_project_type is not None and yml_project_type != self.project_type:
            logger.warning(
                f"Le type de projet {yml_project_type} du fichier _quarto.yml est différent de celui demandé ({self.project_type}). ")
            logger.warning(
                "On utilise le type de projet demandé. Pour utiliser votre fichier _quarto.yml, retenir l'option --pt user."
            )
        params["project"]["type"] = self.project_type


        # On restreint le nombre de documents rendus
        to_render = None
        if 'render' not in params["project"]:
            to_render = self.get_files_to_render()
        if to_render is not None:
            params["project"]['render'] = to_render


        # Injecter chaque format demandé via CLI
        params.setdefault('format', {}) # S'assurer d'abord que la section 'format' existe
        if isinstance(params['format'], dict):
            for fmt in self.formats:
                params['format'][f"docgen-{fmt}"] = "default"

        # filters et shortcodes : il est nécessaire de citer l'extension sous filter pour avoir accès aux filters ET shortcodes de l'extension dynotec
        if "filters" not in params:
            params["filters"] = []
        pos = 0
        if "quarto" in params["filters"]:
            pos = params["filters"].index("quarto")
        params["filters"].insert(pos, "docgen") # Avant pos, soit avant quarto sinon au début
            
        return params



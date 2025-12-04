import copy
from dataclasses import dataclass
import logging
from docgen.renderers.renderer import Renderer
from docgen.utils.mirror import mirror
from docgen.settings import settings
from docgen.quarto import run as quarto_run
from docgen.utils.yml import  to_yml

logger = logging.getLogger(__name__)


@dataclass
class TypeRenderer:
    parent: Renderer
    project_type: str
    sub_output_dir: str = None

    def __post_init__(self):        
       
        # Construit un sous-dossier pour ce type de projet
        assert self.sub_output_dir is not None, "Le sous-dossier de sortie ne peut pas être None"
        self.output_dir = self.build_output_dir()

        # Dans le dossier de build, on impose le output_dir, en respectant la contrainte de quarto : 
        # output_dir doit être relatif au dossier de projet (ici le dossier de build qui un mirroir du projet)
        self._internal_output_dir = self.parent.build_dir / self.sub_output_dir
        

    def has_user_specified_output_dir(self) -> bool:
        return not self.parent.auto_output_dir
    
    def build_output_dir(self):
        """
        Build the output directory for this renderer.
        """
        result = self.parent.output_dir
        if not self.has_user_specified_output_dir():
            result = self.parent.output_dir / self.sub_output_dir
        return result

    @classmethod
    def from_type(cls, parent:Renderer, project_type:str, formats:list[str] = []):
        """
        Factory method to create a TypeRenderer based on the project type.
        """
        from .book import BookRenderer
        from .website import WebsiteRenderer
        from .manuscrit import ManuscriptRenderer
        from .default import DefaultRenderer
        from .user import UserRenderer

        if project_type == "website":
            return WebsiteRenderer(parent=parent, formats=formats)
        elif project_type == "book":
            return BookRenderer(parent=parent, formats=formats)
        elif project_type == "manuscript":
            return ManuscriptRenderer(parent=parent, formats=formats)
        elif project_type == "default":
            return DefaultRenderer(parent=parent, formats=formats)
        elif project_type == "user":
            # Pour l'utilisateur qui gère ses propres réglages Quarto
            return UserRenderer(parent=parent)
        raise ValueError(f"Type de projet {project_type} non supporté. Choisir parmi {settings.get_available_project_types()}")
    
    

    def prepare_quarto_yml_content(self)->dict:
        """
            En fonction des fonctionnalités demandée, pour le type de projet demandé et 
            les formats demandés, on modifie en place le quarto.yml
        """

        params = copy.deepcopy(self.parent.base_quarto_yml_content)
        
        return params
    
    
    def make_quarto_render_cmd_args(self) -> list[str]:
        """
        Prépare les arguments de la commande de rendu Quarto
        """
        cmd_args = ['render']
        
        # cmd_args.extend(['--to', format])
        # cmd_args.extend(["--no-clean"])

        cmd_args.extend([
            '--output-dir', str(self._internal_output_dir.relative_to(self.parent.build_dir)),
        ])

        cmd_args.extend(self.parent.quarto_log_xxx_cmd())

        return cmd_args    

    def mirror_output(self):
        """
        Synchronise le répertoire de sortie dans le build_dir vers le répertoire de sortie 
        de l'appel original.
        """

        # On ne supprime les orphelins que si ce explicitement demandé ou non
        # ou si 
        rm_orphans = False
        if "--no-clean" in self.parent.quarto_render_args:
            rm_orphans = False
        elif "--clean" in self.parent.quarto_render_args:
            rm_orphans = True
        elif self.parent.source_dir==self.output_dir:
            rm_orphans = False
        elif self.sub_output_dir is not None:
            rm_orphans = True
        mirror(
            self._internal_output_dir, 
            self.output_dir,
            rm_orphans=rm_orphans)

    def render(self):
        params = self.prepare_quarto_yml_content()
        to_yml(self.parent._in_mirror_quarto_yml, params)
            
        cmd = self.make_quarto_render_cmd_args()
        build_dir = self.parent.build_dir

        cp = quarto_run(
            cmd, 
            cwd=str(build_dir))
        if cp.returncode != 0:
            logger.error(f"Erreur lors du rendu: {cp.stderr}")
        else:
            self.mirror_output()
            logger.info(f"Rendu quarto opéré avec succès")
            logger.info(f"\t -> {self.output_dir}")
        self.parent.prevent_output_mirror()
        



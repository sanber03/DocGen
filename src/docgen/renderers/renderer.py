from dataclasses import field
import os
import logging
from pathlib import Path
import shutil
from typing import List
from docgen.extensions import add_extension
from docgen.outputs import GENERATED_PATH_IN_BUILD_DIR
from docgen.outputs.container import OutputsContainer
from docgen.regular_expressions import DynotecRegularExpressions
from docgen.renderers.pre.jinja import BasePreRendererJinja
from docgen.utils.path import hash_path, resolve_path
from docgen.utils.mirror import mirror
from docgen.settings import settings
from docgen.utils.source import markdown_file_iterator
from docgen.utils.yml import read_yml, to_yml
import yaml

logger = logging.getLogger(__name__)

PREVENT_OUTPUT_DIR_MIRROR_FILE = ".prevent_output_dir_mirror"

class ParsedItemContainers:
    not_included_files:list[Path] = field(default_factory=list)
    

class Renderer:
    def __init__(
        self,
        source: Path,
        
        project_types: list[str] = None,
        formats: list[str] = None,
        
        output_dir: Path = None,
        build_dir: str = None,
        
        jinja: bool = False,

        quarto_render_args: list[str] = None
        
        
    ):
        f"""
        Initialise le Renderer qui s'appuie sur un _quarto.yml crée automatiquement.

        Parameters:
            source (Path): répertoire ou fichier entrée (.qmd/.md)
            project_types (list[str], optional): types de projet à utiliser pour le rendu. Par défaut, utilise les types disponibles ({','.join(settings.get_default_project_types())}).
            formats (list[str], optional): formats à générer (peut être ignoré si défini dans _quarto.yml)
            output_dir (Path): répertoire de sortie. Le rendu sera dans un sous-répertoire ce dossier. (par défaut {settings.default_output_dir_name} dans le répertoire courant)
            build_dir (Path, optional): Dossier dans lequel dynotec travaille (mirroir de source dir) (par défaut le dossier est un dossier caché)
            jinja (bool): si True, active le pré-rendu Jinja pour les fichiers .qmd et .md
            quarto_render_args (list[str], optional): arguments supplémentaires à passer au rendu.

        """
        
        self.source = Path(source).resolve() if source else Path.cwd()

        self.auto_project_types = True
        self.project_types = None # nécessaire de l'instancier à None pour le bon fonctionnement de validate_projet_types
        self.project_types = self.validate_projet_types(project_types)

        self.auto_formats = formats is None
        self.formats = settings._enforce_list(formats) or settings.get_default_formats()
        
        self.source_dir = self.source if self.source.is_dir() else self.source.parent


        if build_dir is None:
            self.build_dir = settings.dynotec_home / "build" / hash_path(self.source_dir)
        else:
            self.build_dir = resolve_path(build_dir, relative_to=self.source_dir) # on prend le même comporement que quarto pour output-dir = reltaif to source_dir

        # Gestion du output_dir...
        # ... les valeurs obtenues ici sont potentielement modifiées 
        # ... par le _quarto.yml, cf. self.prepare_quarto_yml()
        self.auto_output_dir = True
        self.output_dir = None # nécessaire de l'instancier à None pour le bon fonctionnement de validate_output_dir
        self.output_dir = self.validate_output_dir(output_dir)
        
        self._quarto_yml = self.source_dir / "_quarto.yml"
        self._in_mirror_quarto_yml = self.build_dir / "_quarto.yml"

        self.variables_yaml_content = None
        self.base_quarto_yml_content = None

        self.pre_render_jinja = jinja
        self.quarto_render_args = quarto_render_args or []

        self.parsed_items = ParsedItemContainers()

    def validate_projet_types(self,project_types)->List[str]:
        result = settings._enforce_list(project_types) or settings.get_default_project_types()
        if 'user' in result and len(result)>1:
            raise ValueError("Le type de project 'user' n'est pas compatible avec d'autres types de projet")
        return result

    def validate_output_dir(self,output_dir,source:str = "") -> Path:
        backup_output_dir = self.output_dir
        backup_auto_output_dir = self.auto_output_dir

        self.auto_output_dir = output_dir is None
        if output_dir:
            output_dir = resolve_path(output_dir, relative_to=self.source_dir) # relatif au source_dir, comportement identifque à quarto
        
        result = output_dir or Path.cwd() / settings.default_output_dir_name

        if not backup_auto_output_dir and backup_output_dir != result:
            logger.warning(f"Le output-dir {result} de {source} est différent de "
                           f"celui retenu ({backup_output_dir}).")
            result = backup_output_dir
        
        if result == self.source_dir:
            # On interdit un output_dir identique au source_dir
             # Equivalent à "docgen render ." depuis le répertoire source
            self.auto_output_dir = False
            result = self.source_dir / settings.default_output_dir_name
            logger.warning(f"Le output_dir est identique au source_dir {self.source_dir}. "
                           f"On utilise {result} comme output_dir.")
        return result



    def prevent_output_mirror(self):
        """
        Ajouter un fichier pour empêcher le mirroir de output_dir vers build_dir.
        """
        if self.output_dir.exists():
            (self.output_dir / PREVENT_OUTPUT_DIR_MIRROR_FILE).write_text("DO NOT REMOVE THIS FILE. IT PREVENTS OUTPUT MIRRORING.")

    def mirror_src(self):
        """
        Synchronise le répertoire source vers build_dir :
        - Exclut les dossiers contenant le fichier PREVENT_OUTPUT_DIR_MIRROR_FILE
        - Exclut le dossier de build lui-même 
        """

        self.prevent_output_mirror()

        excluded = [self.build_dir]

        for d in self.source_dir.iterdir():
            if d.is_dir() and (d/PREVENT_OUTPUT_DIR_MIRROR_FILE).exists():
                excluded.append(d)

        mirror(self.source_dir, self.build_dir,
               excluded=excluded,
               kept_orphans=[
                   self.build_dir/GENERATED_PATH_IN_BUILD_DIR,])

        # On force la copie des fichiers que l'on modifie en place
        # - dans set_variables_yml
        # - dans sous_renderer.render
        for p in [self.source_dir / "_quarto.yml", self.source_dir / "_variables.yml"]:
            if p.exists():
                dest = self.build_dir / p.name
                shutil.copy2(p,dest)

    def quarto_log_xxx_cmd(self):
        """
        Prépare les arguments de la commande  Quarto en propageant les arguments de log...
        """
        cmd = []
        for pass_arg in ["--log-level","--log","--log-format"]:
            if pass_arg in self.quarto_render_args:
                pos = self.quarto_render_args.index(pass_arg)
                cmd.extend(self.quarto_render_args[pos:pos+2])
        return cmd

    def quarto_vanilla_cmd(self):
        """
        Prépare les arguments de la commande de rendu Quarto en propageant les 
        arguments communs à dynotec et quarto.
        """
        cmd_args = []
        if not self.auto_formats:
            if len(self.formats) > 1:
                logger.warning(f"Plusieurs formats demandés {','.join(self.formats)}. Quarto ne comprend pas cette syntaxe, seul le dernier sera retenu.")
            for fmt in self.formats:
                cmd_args.extend(['--to', fmt])

        if not self.auto_output_dir:
            # Puisque on travaille dans un mirror on ne répercute pas le output_dir
            # C'est lors du mirror output qu'il sera utilisé
            pass
        return cmd_args    
    
    
    def add_extension(self):       
        # Ajout via quarto add
        cmd = ["--no-prompt"]
        cmd.extend(self.quarto_log_xxx_cmd())
        cmd.append("--quiet")
        add_extension(self.build_dir, *cmd)

    def set_variables_yml(self,context:dict) -> dict:
        """
        Met à jour le _variables.yml dans le build_dir avec le contexte donné.
        Si le fichier n'existe pas, il est créé.
        On garde une référence au contenu pour l'utiliser ultérieurement.
        """
        p = self.build_dir / ('_variables.yml')
        dd = read_yml(p)
        dd.update(context)
        to_yml(p, dd)
        self.variables_yaml_content = dd

    def prepare_quarto_yml(self):
        """
        Modifications communes du _quarto.yml pour tous les types de projet, y compris --pt user
        Le fichier _quarto.yml n'est pas directement écrit à cette étapes.
        Ce sont les sous renderers qui s'en chargeront
        """
        params  = read_yml(self._in_mirror_quarto_yml)
        
        # On supprime un éventuel output-dir que l'on gère via le mirror et mirror_output
        if "project" in params and "output-dir" in params["project"]:
            self.output_dir = self.validate_output_dir(params["project"]["output-dir"],source="_quarto.yml")
            del params["project"]["output-dir"] # Car dans le build_dir on gère automatiquement le output-dir
        
        # On ajoute vars à params
        params["vars"] = self.variables_yaml_content


        # On garde un référence au contenu de base du _quarto.yml
        self.base_quarto_yml_content = params

            

    def resolve_path(self,path:Path,source:bool=False, build:bool=False) -> Path:
        """
        Résout le chemin du fichier source ou du build.
        """
        path = Path(path)
        if source:
            return resolve_path(path, relative_to=self.source_dir)
        elif build:
            return resolve_path(path, relative_to=self.build_dir)
        raise ValueError("Un chemin doit être resolved de puis source ou build")

    def pre_render(self):
        """
        Pre_render hors des scripts projets de Quarto.

        """
        included_files = set()

        jinja_renderer = BasePreRendererJinja()
        outputs_containers = OutputsContainer(build_dir=self.build_dir, source_dir=self.source_dir)


        # Applique le rendu jinja sur les fichiers .qmd et .md
        # ... le contenu est lu dans la source
        for file in markdown_file_iterator(self.build_dir):
            # .... filtres de certaines fichiers non concernés
            if self.build_dir/GENERATED_PATH_IN_BUILD_DIR in file.parents:
                continue
            _buildp=Path(file)
            _srcp = self.resolve_path(_buildp.relative_to(self.build_dir), source=True)
            content = _srcp.read_text(encoding="utf-8")
            
            # Rendu jinja si activé
            if self.pre_render_jinja:
                content = jinja_renderer.render_content(content, self.variables_yaml_content)

            outputs_containers.feed_from_content(content,file)
            _buildp.write_text(content, encoding="utf-8")

        outputs_containers.run()

        # On cherche les inclusions Quarto {{< include "fichier.qmd" >}}
        for file in markdown_file_iterator(self.build_dir):
            content = Path(file).read_text(encoding="utf-8")
            for match in DynotecRegularExpressions.quarto_include.finditer(content):
                included_file = match.group(1).strip()
                included_path = self.resolve_path(included_file, build=True)
                if included_path.is_file():
                    included_files.add(included_path)


        self.parsed_items.not_included_files = list(filter(
                lambda p: p.is_file() and self.resolve_path(p, build=True) not in included_files,
                markdown_file_iterator(self.build_dir))
                )

        
    def render(self,jinja_only_context={},**context):
        """
        Lance Quarto sur l'entrée dans le build directory.
        """
        logger.info("" + "="*50)
        logger.info(f"Préparation du rendu Quarto : {self.build_dir}")
        self.mirror_src()
        self.set_variables_yml(context)
        if 'user' not in self.project_types:
            self.add_extension()
        self.pre_render()
        self.prepare_quarto_yml()
        logger.info("" + "-"*10)

        # Création dossier de sortie parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

        from docgen.renderers.type.abstract import TypeRenderer
        for pt in self.project_types:
            logger.info("" + "="*50)
            logger.info(f"Rendu du type de projet {pt} et format(s) {','.join(self.formats)}")
            type_renderer = TypeRenderer.from_type(self, pt, self.formats)
            type_renderer.render()
            logger.info("" + "-"*10)



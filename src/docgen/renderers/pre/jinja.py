import os
from typing import Iterator
from docgen.regular_expressions import DynotecRegularExpressions
from docgen.utils.source import markdown_file_iterator
import yaml
import glob
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from docgen.logging_ import setup_logging

logger = logging.getLogger("docgen")


class BasePreRendererJinja:
    def __init__(self):

        self.jinja_env = Environment(
            autoescape=False,
            keep_trailing_newline=True
        )
    
    def prepare_content(self,text: str) -> str:
        # Échapper les syntaxe quarto pour éviter les erreurs de rendu
        s = DynotecRegularExpressions.shortcode_start.sub("{{'{{< '}}",text)
        s = DynotecRegularExpressions.shortcode_end.sub("{{' >}}'}}", s)
        return s
    
    def render_content(self, content: str, context: dict) -> str:
        content = self.prepare_content(content)
        template = self.jinja_env.from_string(content)
        rendered = template.render(**context)
        return rendered
        


# class QuartoPreRendererJinja(BasePreRendererJinja):
#     def __init__(self):
#         logger.debug("Variables d'environnement:")
#         logger.debug(f"QUARTO_PROJECT_RENDER_ALL: {os.environ.get('QUARTO_PROJECT_RENDER_ALL')}")
#         logger.debug(f"QUARTO_PROJECT_OUTPUT_DIR: {os.environ.get('QUARTO_PROJECT_OUTPUT_DIR')}")
#         logger.debug(f"QUARTO_PROJECT_INPUT_FILES: {os.environ.get('QUARTO_PROJECT_INPUT_FILES')}")
#         logger.debug(f"QUARTO_PROJECT_OUTPUT_FILES: {os.environ.get('QUARTO_PROJECT_OUTPUT_FILES')}")
#         logger.debug(f"DYNOTEC_ORIGINAL_CWD: {os.environ.get('DYNOTEC_ORIGINAL_CWD')}")
#         logger.debug(f"DYNOTEC_SOURCE_DIR: {os.environ.get('DYNOTEC_SOURCE_DIR')}")
#         logger.debug(f"DYNOTEC_FILE_DIR: {os.environ.get('DYNOTEC_BUILD_DIR')}")
#         logger.debug(f"Répertoire courant: {Path.cwd()}")

#         self.build_dir = os.environ.get("DYNOTEC_BUILD_DIR", None)
#         self.src_dir = os.environ.get("DYNOTEC_SOURCE_DIR", None)

#         if self.build_dir:
#             self.build_dir = Path(self.build_dir)
#         if self.src_dir:
#             self.src_dir = Path(self.src_dir)
        
#         if not self.build_dir or not self.src_dir or not self.build_dir.exists() or not self.src_dir.exists():
#             raise FileNotFoundError("Les fichiers build_dir et src_dir doivent être définis et exister.")

#         super().__init__()





#     def find_variables_file(self):
#         """
#         Cherche le fichier _variables.yml dans différents emplacements pertinents.
        
#         Args:
#             file_dir: Répertoire contenant les fichiers .qmd
            
#         Returns:
#             Path du fichier _variables.yml trouvé, ou None si non trouvé
#         """
#         # Liste des répertoires à vérifier, par ordre de priorité
#         search_dirs = [
#             self.build_dir,  # D'abord dans le répertoire des fichiers
#         ]
        
#         # Ajouter le répertoire original d'exécution s'il est défini
#         # On ne peut pas s'appuyer sereinement sur Path.cwd car il semble que quarto le détermine
#         # à partir du fichier _quarto.yml
#         original_cwd = os.environ.get("DYNOTEC_ORIGINAL_CWD")
#         if original_cwd:
#             search_dirs.append(Path(original_cwd))
        
#         # Chercher dans chaque répertoire
#         for directory in search_dirs:
#             vars_file = directory / "_variables.yml"
#             if vars_file.exists():
#                 return vars_file

#     def build_context(self):
#         vars_file = self.find_variables_file()
#         context = {}
#         if vars_file:
#             try:
#                 context = yaml.safe_load(vars_file.read_text(encoding="utf-8"))
#                 logger.info(f"Variables chargées depuis {vars_file}")
#             except Exception as e:
#                 logger.error(f"Erreur lors du chargement des variables: {e}")
#         else:
#             logger.warning("Aucun fichier _variables.yml trouvé")
#         return context
    

#     def files(self)->Iterator[Path]:
#         """
#         Retourne un itérateur sur les fichiers .qmd et .md dans le répertoire de build.
#         """
#         return markdown_file_iterator(self.build_dir)
    
#     def render_file(self, template_path: Path, context: dict):
#         """
#         Rendu du fichier avec le contexte Jinja.
#         """
#         content = template_path.read_text(encoding="utf-8")
#         return self.render_content(content, context)
    
#     def render(self):
#         """
#         Fonction principale de pré-rendu pour traiter les fichiers .qmd avec Jinja.
#         Mode RENDER SPECIFIC uniquement.
#         """
            
#         logger.info(f"Traitement des fichiers dans: {self.build_dir}")
        
#         # Chargement des variables
#         context = self.build_context()

#         # Traitement de tous les fichiers (.qmd et .md)
#         for filepath in self.files():
#             path = Path(filepath)
#             logger.info(f"Traitement du fichier: {path}")

#             try:
#                 rendered = self.render_file(path, context)
#                 path.write_text(rendered, encoding="utf-8")
#                 logger.info("Pré-rendu appliqué à %s", path.relative_to(self.build_dir))
#             except Exception as e:
#                 logger.error("Erreur Jinja sur %s : %s", path, e)
    


# if __name__ == "__main__":
#     # Boucle main utilitée par le script pre-renderer (obsolète)
#     setup_logging(logging.INFO)
#     pre_renderer = QuartoPreRendererJinja()
#     pre_renderer.render()


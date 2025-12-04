import argparse
from pathlib import Path
from docgen.renderers.renderer import Renderer
from docgen.cli.base import BaseCommand
from docgen.settings import settings


class RenderCommand(BaseCommand):
    name = "render"
    help = """Génère un rapport ou un site web à partir de quarto.  Les arguments autres que ceux cités ci-dessous sont directement passés à la commande `quarto render`."""

    def setup_parser(self, parser:argparse.ArgumentParser):
        parser.add_argument(
            "src",
            nargs='?',
            default=None,
            type=Path,
            help="Répertoire ou fichier principal (.qmd/.md). Si non spécifié, utilise le répertoire courant."
        )
        parser.add_argument(
            "--pt","--project-type",
            dest="project_type",
            action='append',
            choices=settings.get_available_project_types(),
            default=None,
            help="Types de projet à utiliser pour le rendu. Séparer plusieurs types par une virgule.")
        
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=None,
            help="Dossier de sortie pour les fichiers générés"
        )
        parser.add_argument(
            "--to",
            action='append',
            choices=settings.get_available_formats(),
            default=[],
            help=f"Formats à générer. Séparer plusieurs formats par une virgule."
        )
        parser.add_argument(
            "--jinja",
            action="store_true",
            help="Activer le pré-rendu Jinja pour les fichiers .qmd et .md"
        )

    def main(self, ns:argparse.Namespace,rest_args) -> None:
        renderer = Renderer(
            source=ns.src,
            project_types=ns.project_type,
            output_dir=ns.output_dir,
            formats=ns.to,
            jinja=ns.jinja,
            quarto_render_args=rest_args
        )
        renderer.render()


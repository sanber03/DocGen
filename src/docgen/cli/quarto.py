import argparse
import sys
from docgen.settings import settings
from docgen.cli.base import BaseCommand

import logging
logger = logging.getLogger(__name__)

class QuartoCommand(BaseCommand):
    name = "quarto"
    help="Utilise la version 'docgen' de Quarto, qui est installée par défaut avec dynotec. "
    description = f"""{help}
Plus d'informations en tapant 'docgen quarto --more-help' ou '-mh' ou en consultant la documentation de Quarto.
"""

    def pre_parse_args(self, args):
        if "quarto" in args:
            pos = args.index("quarto")
            if "-h" in args[pos:] or "--help" in args[pos:]:
                from docgen.quarto import run
                rest_args = args[pos+1:]
                run(rest_args)
                sys.exit(0)
        return args

    def main(self, ns:argparse.Namespace,rest_args) -> None:
        if rest_args:
            from docgen.quarto import run
            run(rest_args)



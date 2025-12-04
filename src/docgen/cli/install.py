import argparse
from docgen.cli.base import BaseCommand


class InstallCommand(BaseCommand):
    name = "install"
    help="Installe et configure l’environnement quarto (Quarto, TinyTeX, kernel, ...). Cette commande est réputée " \
    "lancée automatiquement par dynotec à la première utilisation, mais peut être utilisée manuellement si nécessaire."


    def main(self, ns:argparse.Namespace,rest_args) -> None:
        from docgen.quarto import install
        install()



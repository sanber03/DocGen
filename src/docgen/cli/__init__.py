import argparse
import logging
from anyio import Path
from docgen.quarto import install_once
from docgen.settings import settings
from docgen.logging_ import setup_logging
import sys
from docgen.cli.install import InstallCommand
from docgen.cli.render import RenderCommand
from docgen.cli.quarto import QuartoCommand
from docgen.utils.path import resolve_path

def cmd_iterator():
    """
    Itérateur pour parcourir les commandes dynotec.
    """
    yield InstallCommand()
    yield RenderCommand()
    yield QuartoCommand()

def create_parser()->argparse.ArgumentParser:

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--log-level",choices=["debug","info","warning","error","critical"],default=None,help="Niveau de log à afficher")
    common_parser.add_argument("--log-format",default=None,help="Format du log")
    common_parser.add_argument("--log",default=None,help="Fichier de log")

    parser = argparse.ArgumentParser(
        prog="docgen",
        description=f"docgen cli {settings.package_version}",
        parents=[common_parser])
    parser.add_argument("--version", action="version", version=f"docgen {settings.package_version}")


    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in cmd_iterator():
        cmd.add_parser(sub,parents=[common_parser])
    return parser

def pre_parse_args(args: list[str]=None) -> list[str]:
    """
    Pré-traite les arguments avant de les passer au parser.
    Peut être utilisé pour modifier les arguments ou ajouter des options globales.
    """
    if args is None:
        args = sys.argv[1:]
    for cmd in cmd_iterator():
        args = cmd.pre_parse_args(args)
    return args

def main(argv=None):
    setup_logging(logging.INFO)
    install_once()
    parser = create_parser()
    argv = pre_parse_args(argv)
    ns,rest_args = parser.parse_known_args(argv)

    # Niveau de verbosité
    log_level= ns.log_level
    if log_level is None:
        log_level = "info"
    level = getattr(logging,log_level.upper())
    if ns.log:
        p_log = Path(ns.log)
        if not p_log.is_absolute():
            p_log = resolve_path(p_log)
        p_log_quarto = p_log.with_stem(p_log.stem + "_quarto")
        ns.log = str(p_log)
    setup_logging(level,log_file=ns.log,log_format=ns.log_format)

    # Propagation à quarto
    if ns.log_level is not None:
        rest_args.extend(['--log-level', ns.log_level])
    if ns.log_format is not None:
        rest_args.extend(['--log-format', ns.log_format])
    if ns.log is not None:
        rest_args.extend(['--log', str(p_log_quarto)])

    # Boucle principale de la commande
    if 'main' in ns:
        ns.main(ns,rest_args)

if __name__ == "__main__":
    main()
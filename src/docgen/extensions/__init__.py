from pathlib import Path
from docgen.settings import settings
from docgen.quarto import run as quarto_run

ROOT = settings.package_directory / "extensions" / "docgen"
SRC = ROOT / "_extensions"
SRC_FILES = ROOT / "_extensions-files"

EXT_NAMES = ["docgen"]

def add_extension(dest:Path,*other_cmd):
    cmd = ["add",str(SRC)]
    cmd.extend(other_cmd)
    quarto_run(cmd, cwd=dest)
    set_path_to_files(dest)

def set_path_to_files(dest_dir:Path):
    dest = dest_dir / "_extensions"
    # On modifie le _extension.yml pour mettre à jour les chemins des fichiers
    for ext_name in EXT_NAMES:
        ext_path = dest / ext_name
        p__extension_yml = ext_path / "_extension.yml"
        p_files = SRC_FILES / ext_name
        if p__extension_yml.exists() and p_files.exists():
            content = p__extension_yml.read_text(encoding=settings.yml_encoding)
            content = content.replace("PATH_TO_FILES/",p_files.as_posix() + "/")
            p__extension_yml.write_text(content, encoding=settings.yml_encoding)
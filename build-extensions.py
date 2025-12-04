from __future__ import annotations

from dataclasses import dataclass
import os
import re
import shutil

from pathlib import Path


REG_YML_VERSION = re.compile(r"version:\s*([\d]+\.[\d]+\.[\d]+)")
REG_TOML_VERSION = re.compile(r"version\s*=\s*\"([\d]+\.[\d]+\.[\d]+)\"")

@dataclass
class Extension:
    path: Path
    name: str = None

    def __post_init__(self):
        self.name = self.path.name

    @property
    def _extension_yml(self) -> Path:
        return self.path / "_extensions" / self.name / "_extension.yml"

    def set_version(self, version: str) -> None:
        """
        Met à jour la version de l'extension dans le fichier _extension.yml.
        """
        extension_yml = self._extension_yml
        if not extension_yml.exists():
            raise FileNotFoundError(f"Le fichier {extension_yml} n'existe pas.")
        
        content = extension_yml.read_text(encoding='utf-8')
        content = REG_YML_VERSION.sub(r"version: {}".format(version), content)
        extension_yml.write_text(content, encoding='utf-8')
    


def build() -> None:
    poetry_path = Path(__file__).parent / "pyproject.toml"
    if not poetry_path.exists():
        raise FileNotFoundError(f"Le fichier {poetry_path} n'existe pas.")
    content = poetry_path.read_text(encoding='utf-8')
    m = REG_TOML_VERSION.search(content)
    if m:
        version = m.group(1)
    else:
        raise ValueError(f"Version non trouvée dans {poetry_path}. Assurez-vous que le format est correct.")

    extension_path = Path(__file__).parent / "src" / "dynotec" / "extensions"
    extension_names = ['dynotec']
    for name in extension_names:
        e = Extension(path=extension_path / name)
        e.set_version(version)



if __name__ == "__main__":
    build()

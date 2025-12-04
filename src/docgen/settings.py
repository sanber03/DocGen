from pathlib import Path
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
import importlib.resources
from importlib.metadata import version

try:
    _default_package_directory = importlib.resources.files("docgen")
except ImportError:
    _default_package_directory = None

try:
    _default_package_version = version("docgen")
except ImportError:
    _default_package_version = None

_DYNOTEC_HOME = Path.home() / "docgen"
_DYNOTEC_HOME.mkdir(parents=True, exist_ok=True)

_DYNOTEC_ENV_FILE = _DYNOTEC_HOME / ".env"

_ENV_PREFIX = "DYNOTEC_"


_DEFAULT_FORMATS = ["html"]
_AVAILABLE_FORMATS = ["pdf", "docx", "html"]

_DEFAULT_PROJECT_TYPES = ["default"]
_AVAILABLE_PROJECT_TYPES = ["default", "website", "book","manuscript","user"]

class DynotecSettings(BaseSettings):
    """
    Settings pour dynotec
    """

    model_config = SettingsConfigDict(env_prefix=_ENV_PREFIX,env_file=_DYNOTEC_ENV_FILE,extra="allow")

    dynotec_home: Path = _DYNOTEC_HOME

    package_directory: Path = _default_package_directory
    package_version: str = _default_package_version

    examples_path: Path = package_directory / "examples"

    # Install
    if sys.platform.startswith("win"):
        quarto_download_url: str = "https://github.com/quarto-dev/quarto-cli/releases/download/v1.7.32/quarto-1.7.32-win.zip"
    elif sys.platform.startswith("linux"):
        quarto_download_url: str = "https://github.com/quarto-dev/quarto-cli/releases/download/v1.7.32/quarto-1.7.32-linux-amd64.tar.gz"
    elif sys.platform.startswith("darwin"):
        quarto_download_url: str = "https://github.com/quarto-dev/quarto-cli/releases/download/v1.7.32/quarto-1.7.32-macos.tar.gz"
    local_quarto_path:Path = dynotec_home / 'quarto' / Path(quarto_download_url.split("/")[-1]).stem
    if sys.platform.startswith("win"):
        local_quarto_exe: Path = local_quarto_path / "bin" / "quarto.exe"
    else:
        local_quarto_exe: Path = local_quarto_path / "bin" / "quarto"
    ipykernel_name: str = "docgen_env"

    # Renderer
    default_project_types: str = ",".join(_DEFAULT_PROJECT_TYPES)
    available_project_types: str = ",".join(_AVAILABLE_PROJECT_TYPES)

    default_formats:str = ",".join(_DEFAULT_FORMATS)
    available_formats: str = ",".join(_AVAILABLE_FORMATS)
    
    yml_encoding: str = 'utf-8'
    default_output_dir_name: str = "docgen_output"

    build_dir_name: str|None = None

    def _enforce_list(self,value)->list[str]:
        if value is None:
            return value
        if isinstance(value,list):
            return list(set(value))  # Enlever les doublons
        return self._enforce_list(value.split(","))


    def get_available_formats(self) -> list[str]:
        """
        Retourne la liste des formats disponibles.
        """
        return self._enforce_list(self.available_formats)
    
    def get_default_formats(self) -> list[str]:
        """
        Retourne la liste des formats par défaut.
        """
        return self._enforce_list(self.default_formats)
    
    def get_available_project_types(self) -> list[str]:
        """
        Retourne la liste des types de projet disponibles.
        """
        return self._enforce_list(self.available_project_types)

    
    def get_default_project_types(self) -> list[str]:
        """
        Retourne le type de projet par défaut.
        """
        return self._enforce_list(self.default_project_types)




settings = DynotecSettings()


if __name__=="__main__":
    print(settings.get_available_formats())
    assert isinstance(settings.get_available_formats(),list)
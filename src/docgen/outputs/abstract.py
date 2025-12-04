from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
import re
from docgen.outputs import GENERATED_PATH_IN_BUILD_DIR
from docgen.outputs.descriptor import OutputPathDescriptor


@dataclass
class AbstractOutput:
    rematch:re.Match
    content_path:Path
    container: 'OutputsContainer' = field(init=False, default=None)
    sub_by: str = field(default='',init=False)


    @property
    def generated_dir(self) -> Path:
        """
        Retourne le chemin du dossier de génération des outputs.
        """
        return self.container.build_dir / GENERATED_PATH_IN_BUILD_DIR

    @classmethod
    @contextmanager
    def executor(cls):
        """
        Context manager to handle the execution of outputs.
        This can be overridden in subclasses for specific behavior.
        """
        yield

    
    def build(self):
        pass
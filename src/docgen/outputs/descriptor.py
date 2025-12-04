

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
from typing import ClassVar, Self

from docgen.outputs import GENERATED_PATH_IN_BUILD_DIR
from docgen.utils.path import resolve_path


@dataclass
class OutputPathDescriptor:
    """
    Determine un nouveau chemin dans dest_dir pour un chemin donnée:
    - si le chemin est relatif à source_dir, le nouveau chemin est relatif à dest_dir
    - si le chemin est hors de source_dir, le nouveau chemin est crée est relatif à dest_dir
    """

    absolute_path: Path = None
    
    absolute_new_stem: Path = None # New path in the dest directory
    relative_new_stem: Path = None # New path relative to the dest directory


    n_called: int = 0

    is_generated: bool = False

    _new_path_counter: ClassVar[dict] = {}

    @classmethod
    def next_path(cls,dest_dir)->Path:
        """
        Returns the next path to be used in the build directory.
        """
        cls._new_path_counter.setdefault(dest_dir, 0)
        cls._new_path_counter[dest_dir] = cls._new_path_counter[dest_dir]  + 1
        return Path(".") / GENERATED_PATH_IN_BUILD_DIR / f"auto_{cls._new_path_counter[dest_dir]}_"

    @classmethod
    def from_string(cls, s: str|Path,source_dir,dest_dir,force_generation: bool=False)-> Self:
        """
        Create an OutputPathDescriptor from a string path.
        
        s est un chemin absolu ou relatif à source_dir au format str ou Path lib
        """
        original_path = s
        if isinstance(s, str):
            original_path = s.strip()
        absolute_path = resolve_path(original_path,relative_to=source_dir)
        result = cls(
            absolute_path=absolute_path
        )
        to_test = absolute_path
        if absolute_path.is_file():
            to_test  = absolute_path.parent
        if to_test < source_dir or force_generation:
            result.relative_new_stem = cls.next_path(dest_dir)
            result.absolute_new_stem= resolve_path(result.relative_new_stem,relative_to=dest_dir)
            result.is_generated = True
        else:
            result.relative_new_stem = absolute_path.relative_to(source_dir)
        return result    


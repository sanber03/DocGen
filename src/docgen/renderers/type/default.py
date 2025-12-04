
from dataclasses import dataclass
import logging
from typing import List
from docgen.renderers.type.abstract import TypeRenderer
from docgen.renderers.renderer import Renderer
from docgen.renderers.type.base_pre_renderer2 import BasePreRenderer2

logger = logging.getLogger(__name__)

@dataclass
class DefaultRenderer(BasePreRenderer2):
    project_type:str = "default"
    sub_output_dir:str = "_default"

    def get_files_to_render(self)->List[str]|None:
        """
        Dans le cas du type par défault la liste des fichiers à render et tous sauf ceux inclus
        """
        files = []
        for file in self.parent.parsed_items.not_included_files:
            files.append(str(file.relative_to(self.parent.build_dir)))
        return files
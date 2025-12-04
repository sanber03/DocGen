
from dataclasses import dataclass
import logging
from docgen.renderers.type.abstract import TypeRenderer
from docgen.renderers.renderer import Renderer
from docgen.renderers.type.base_pre_renderer2 import BasePreRenderer2

logger = logging.getLogger(__name__)



@dataclass
class ManuscriptRenderer(BasePreRenderer2):
    project_type:str = "manuscript"
    sub_output_dir:str = "_manuscript"




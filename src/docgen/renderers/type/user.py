
from dataclasses import dataclass
import logging
from docgen.renderers.type.abstract import TypeRenderer

logger = logging.getLogger(__name__)


@dataclass
class UserRenderer(TypeRenderer):
    project_type:str = "user"
    sub_output_dir:str = "_user"

    def make_quarto_render_cmd_args(self):
        args = super().make_quarto_render_cmd_args()
        args.extend(self.parent.quarto_vanilla_cmd())
        return args

        
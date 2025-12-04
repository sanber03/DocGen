
from dataclasses import dataclass
import logging
from docgen.renderers.type.abstract import TypeRenderer
from docgen.renderers.renderer import Renderer
from docgen.renderers.type.base_pre_renderer2 import BasePreRenderer2
from docgen.utils.yml import to_yml


logger = logging.getLogger(__name__)

@dataclass
class WebsiteRenderer(BasePreRenderer2):
    project_type:str = "website"
    sub_output_dir:str = "_website"

    def validate_formats(self, formats):
        return list(set(["html"]) & set(super().validate_formats(formats)))

    def prepare_quarto_yml_content(self)-> dict:
        params = super().prepare_quarto_yml_content()   
        # Ajouter les paramètres spécifiques au livre

        if 'website' not in params:
            pages = []
            for file in self.parent.parsed_items.not_included_files:
                pages.append(file.relative_to(self.parent.build_dir))

            webp = {
                'title': "Website Title",
                "navbar": {
                    "right": [
                        {"href": str(p), "text": p.stem}
                        for p in pages
                    ]
                }
            }
            
            # On garde cette configuration pour la suite ...
            params['website'] = webp

        return params

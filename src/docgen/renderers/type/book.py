
import logging
from dataclasses import dataclass
from docgen.renderers.renderer import Renderer
from docgen.renderers.type.base_pre_renderer2 import BasePreRenderer2
from docgen.utils.yml import read_yml, to_yml

logger = logging.getLogger(__name__)

@dataclass
class BookRenderer(BasePreRenderer2):
    project_type:str = "book"
    sub_output_dir:str = "_book"
    
    def prepare_quarto_yml_content(self)-> dict:
        params = super().prepare_quarto_yml_content()
        # Ajouter les paramètres spécifiques au livre

        exists = False
        chapters = []
        p_index = self.parent.build_dir / f"index.qmd"
        for suffix in (".md", ".qmd"):
            if p_index.with_suffix(suffix).exists():
                exists = True
                p_index = p_index.with_suffix(suffix)
                break
        if not exists:
            p_index.write_text("<!--Book Index Obligatoire.-->")

        if 'book' not in params:
            chapters = []
            for file in self.parent.parsed_items.not_included_files:
                chapters.append(str(file.relative_to(self.parent.build_dir)))
            if p_index.name not in chapters:
                chapters.insert(0, p_index.name)
            

            bookp = {
                'title': "Book Title",
                "chapters": chapters
            }
            
            # On garde cette configuration pour la suite ...
            params['book'] = bookp


        return params


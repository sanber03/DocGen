from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Iterator, List
from docgen.outputs.abstract import AbstractOutput
from docgen.outputs.descriptor import OutputPathDescriptor
from docgen.outputs.excel import ExcelImgOutput, ExcelOutput, ExcelMarkdownOutput
from docgen.outputs.img_copy import ImgCopy
from docgen.regular_expressions import DynotecRegularExpressions


@dataclass
class OutputsContainer:
    _instances:dict[Path, List[AbstractOutput]] = field(default_factory=dict)
    source_dir: Path = None
    build_dir: Path = None

    def add(self, output: AbstractOutput):
        output.container = self
        self._instances.setdefault(output.content_path, []).append(output)

    def feed_from_content(self,content:str,path:Path):
        for ocls,reg in [
            (ExcelImgOutput, DynotecRegularExpressions.excel_img_syntax),
            (ExcelMarkdownOutput, DynotecRegularExpressions.excel_table_syntax),
            (ImgCopy, DynotecRegularExpressions.path_in_img)
        ]:
            for match in reg.finditer(content):
                o = ocls(
                    rematch=match,
                    content_path=path,
                )
                self.add(o)

    @contextmanager
    def executor(self):
        with ImgCopy.executor(), ExcelOutput.executor():
            yield


    def outputs(self)->Iterator[AbstractOutput]:
        for outputs in self._instances.values():
            yield from outputs

    def run(self):
        """
        Process les outputs par content_path, match.position décroissant
        """
        
        with self.executor():
            for output in self.outputs():
                output.build()

        for content_path in self._instances.keys():
            # TODO : non robuste si des matches se chevauchent, tout casse
            self._instances[content_path].sort(key=lambda x: x.rematch.start(), reverse=True)  # Tri par position de match décroissante
        
        for content_path,outputs in self._instances.items():
            content = content_path.read_text(encoding="utf-8")
            for output in outputs:
                content = content[:output.rematch.start()] + output.sub_by + content[output.rematch.end():]
            content_path.write_text(content, encoding="utf-8")

from contextlib import contextmanager
from pathlib import Path
import shutil
from typing import ClassVar
from docgen.outputs.abstract import AbstractOutput
from docgen.outputs.descriptor import OutputPathDescriptor
from docgen.utils.path import has_been_modified


class ImgCopy(AbstractOutput):
    """
    Copie évenuellement un image hors de la source dans le build et modifie le passe de l'image
    dans la source.
    """
    _copy_cache:ClassVar[set] = set()

    @classmethod
    @contextmanager

    def executor(cls):
        """
        Context manager to handle the execution of image copying.
        This can be overridden in subclasses for specific behavior.
        """
        try:
            yield
        finally:
            cls._copy_cache.clear()

    def build(self):
        """
        Copie l'image à partir du chemin spécifié dans le shortcode.
        """
        # On récupère le chemin de l'image depuis le match : C'est 
        #   une position absolu depuis la source /xxx, 
        #   OU une position absolue
        #   OU relative depuis le file (# Le file vient potentiellent d'un sub folder)

        # On détermine sa position relative depuis le build_dir

        # On détermine alors si copie interne nécessaire
        # - OUI on garde le nouveau chemin relatif ET on procède à la copie
        # - NON on reprend le chemin original

        
        original_path = self.rematch.group(1).strip()


        if original_path.startswith('/'):
            img_path = self.container.build_dir / original_path[1:]
            mode = 0
        else:
            img_path = Path(original_path)
            if img_path.is_absolute():
                mode = 1
            else:
                img_path = self.content_path.parent / Path(img_path)
                mode = 2

        try:
            img_path = img_path.relative_to(self.container.build_dir)
        except ValueError:
            pass

        img_descr = OutputPathDescriptor.from_string(img_path,
                                                 source_dir=self.container.source_dir,
                                                 dest_dir=self.container.build_dir,)
        

        if img_descr.is_generated:
            # On garde référence à nom initial de l'image
            new_path = img_descr.relative_new_stem
            new_path = new_path\
                .with_stem(new_path.stem + f"{img_descr.absolute_path.stem}")\
                .with_suffix(img_descr.absolute_path.suffix)
        else:
            new_path = original_path


        if img_descr.is_generated and str(img_descr.absolute_path) not in self._copy_cache:
            # Copie lors de la première utilisation
            dest = img_descr.absolute_new_stem.with_name(new_path.name)
            if has_been_modified(img_descr.absolute_path, dest):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(img_descr.absolute_path, dest)
                self._copy_cache.add(str(img_descr.absolute_path))


        self.sub_by = self.rematch.group(0).replace(self.rematch.group(1), str(new_path))   

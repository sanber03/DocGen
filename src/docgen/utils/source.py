from pathlib import Path

def with_extension_file_iterator(path: Path, extensions: list[str]):
    """
    Iterate through files in the given path and its subdirectories,
    yielding only files with the specified extension.
    """
    if not isinstance(extensions, list):
        extensions = [extensions]
    for p in path.iterdir():
        if p.is_dir():
            yield from with_extension_file_iterator(p, extensions)
        elif p.suffix in extensions:
            yield p

def markdown_file_iterator(path:Path):
    yield from with_extension_file_iterator(path, [".md", ".qmd"])
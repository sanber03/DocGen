from docgen.renderers import Renderer
from pathlib import Path


p = Path(__file__).parent

renderer = Renderer(
    source=p,
    formats=["pdf","html"],
    output_dir=p
)
renderer.render(ma_variable="Hello World")


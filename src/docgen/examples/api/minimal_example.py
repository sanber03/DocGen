from docgen.renderers import Renderer
from pathlib import Path

from docgen.utils.table import to_quarto_markdown
import pandas as pd


p = Path(__file__).parent

chapter2_path = p / "Chapter2.qmd"
chapter2_content = '''

# Chapter 2

Ma variable vaut {{< var ma_variable>}} 

'''

chapter2_content+= to_quarto_markdown(pd.DataFrame({k:range(10) for k in "salut"}))


# Dans le style ci-dessous les couleurs ne fonctionnent que pour le html
cell_hover = {  # for row hover use <tr> instead of <td>
    'selector': 'td:hover',
    'props': [('background-color', '#ffffb3')]
}
index_names = {
    'selector': '.index_name',
    'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
}
headers = {
    'selector': 'th:not(.index_name)',
    'props': 'background-color: #000066; color: white;'
}

chapter2_content+= to_quarto_markdown(
    pd.DataFrame({k:range(1000,1010) for k in "salut"}).style\
        .format(precision=2, thousands="#", decimal=",") \
        .format_index(str.upper, axis=1)\
        .set_table_styles([cell_hover, index_names, headers]))

chapter2_path.write_text(chapter2_content)


renderer = Renderer(source=p,formats=["pdf","html"])
renderer.render(ma_variable="Hello World")


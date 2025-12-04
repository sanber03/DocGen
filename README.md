# docGen - Dynamic Document Generator

**docGen** is a tool that generates dynamic reports and websites in **PDF**, **DOCX**, or **HTML** from `.md` or `.qmd` files using Markdown syntax.

**docGen** is built on top of [Quarto](https://quarto.org/).

**docGen** is a command-line interface tool.

**docGen** provides a Python API to be used directly in Python scripts.

## Installation

### Requirements

- Python >= 3.11
- Poetry (recommended)

### Install from source

```bash
git clone https://github.com/sanber03/DocGen.git
cd docgen
poetry install
```

### Install with pip

```bash
pip install -e .
```

## How it works - Differences from Quarto

**docGen** extends Quarto with additional features:

- **Excel Integration**: Extract tables and charts from Excel files and embed them in documents
- **Jinja2 Templating**: Pre-process documents with Jinja2 before Quarto rendering
- **Variable Management**: Centralized variables in `_variables.yml`
- **Custom Extensions**: Additional shortcodes and filters for enhanced functionality

## Quick Start

1. Create a folder `my_note`
2. Save the following file as `my_document.md`:

```markdown
# Chapter 1

Getting started:

- Install docGen: ☑
- Create my first document: ☐
```

3. Open a command prompt in the folder
4. Run the command:

```bash
docgen render --to pdf --to html
```

5. View the results in `./docgen_output/_documents`

## Markdown Syntax in docGen

Quarto uses the Markdown syntax described at [this address](https://quarto.org/docs/authoring/markdown-basics.html).

We summarize here the key features used or implemented by docGen.

### Document Nesting

```markdown
{{< include ./my_sub_chapter.md >}}
```

### Including Tables/Images from Excel

The syntax is similar to creating Markdown links or images: `[label](url)` and `![label](path)`.

**Two syntaxes:**

- `excel[label](path?range_name)` - Rendered as image (Windows only)
  - If the range contains a chart, it will be visible
- `excel-table[label](path?range_name)` - Rendered as table

**Example:**

```markdown
excel[my_table_as_image](./example.xlsx?mychart)

excel-table[my_table](./example.xlsx?Sheet1!A1:D6)
```

## Variables and Dynamic Rendering

Two approaches are possible. The Jinja approach is more comprehensive and allows iterations.

Both approaches use variables contained in the `_variables.yml` file.

### The _variables.yml file

Variable values are read from the `_variables.yml` file at the project root:

```yaml
a: 1
my_list:
  - 1
  - 2
  - 3
```

### Jinja Dynamic Rendering

Files can use the [Jinja engine](https://jinja.palletsprojects.com/en/stable/templates/) before Quarto rendering:

```markdown
{% for value in my_list %}

# Sub-paragraph {{value}}

Created by iteration
{% endfor %}
```

Add the `--jinja` option to enable Jinja rendering:

```bash
docgen render ... --jinja
```

Or in Python API: `jinja=True`

### Quarto Dynamic Rendering

Quarto also offers dynamic rendering:

```markdown
The variable 'a' from _variables.yml is {{< var a >}}

The metadata 'mymetathing' is {{< meta mymetathing >}}
```

**Note:** In docGen, variables from `_variables.yml` are placed in the `vars` metadata. The following syntaxes are equivalent:

```markdown
{{< var a >}}
{{< meta vars.a >}}
```

## Conditional Rendering

### Jinja Conditional Rendering

See [Jinja documentation](https://jinja.palletsprojects.com/en/stable/templates/)

Variables are from the `_variables.yml` file:

```markdown
{% if my_variable %}

## My Paragraph

{% endif %}
```

Enable with `--jinja` option.

### Quarto Conditional Rendering

Quarto also offers conditional rendering. docGen automatically places `_variables.yml` content in metadata under the `vars` key:

```markdown
::: {.content-hidden when-meta="vars.hide_mysection"}

# Conditional section

:::

::: {.content-hidden unless-meta="vars.hide_mysection"}

# Conditional section if hide_mysection

:::
```

## Python API

```python
from docgen.renderers import Renderer
from pathlib import Path

renderer = Renderer(
    source=Path("my_note"),
    formats=["pdf", "html"],
    jinja=True
)

renderer.render(my_variable="Hello World")
```

## Command Line Usage

```bash
# Render to multiple formats
docgen render path/to/source --to html --to pdf --to docx

# With Jinja templating
docgen render path/to/source --jinja --to pdf

# Specify output directory
docgen render path/to/source --output-dir ./output --to html

# With project type
docgen render path/to/source --pt website --to html
```

### Available Project Types

- `default`: Standard document
- `website`: Multi-page website
- `book`: Book format with chapters

## Reporting Issues

When reporting an issue, please include:

1. Run the command with debug logging:
   ```bash
   docgen render .... --log-level debug --log .log
   ```

2. Collect:
   - Source folder
   - `.log` and `.log_quarto` files
   - Console output

3. Open an issue on GitHub with the information

## Author

Sanae Berri

## Built With

- [Quarto](https://quarto.org/) - Scientific and technical publishing
- [Jinja2](https://jinja.palletsprojects.com/) - Templating engine
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file handling
- [xlwings](https://www.xlwings.org/) - Excel integration (optional, Windows only)

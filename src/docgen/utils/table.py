import pandas as pd

def to_quarto_markdown(df_or_str:pd.DataFrame|str,label=None,header:bool=True,index:bool=True,**kwargs)->str:
    """Convert a DataFrame or HTML string to Quarto Markdown format."""
    if isinstance(df_or_str, str):
        result = df_or_str
    elif hasattr(df_or_str, 'to_html'):
        result = df_or_str.to_html(None,header=header,index=index,**kwargs)
    else:
        raise ValueError("Input must be a DataFrame or an HTML string.")
    labelr = f"\n<figcaption>{label}</figcaption>" if label else ""
    return f"""
```{{=html}}
{result}{labelr}
```
"""
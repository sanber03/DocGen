import re


class DynotecRegularExpressions:
    shortcode_start = re.compile(r"{{\s*<\s*")
    shortcode_end = re.compile(r"\s*>\s*}}")
    quarto_include = re.compile(shortcode_start.pattern+"include\s+(.*)"+shortcode_end.pattern)


    path_in_img = re.compile(r"\!\[.*\]\((.*)\)")
    excel_img_syntax = re.compile(r"excel(?:-img)?\[(.*)\]\((.*)\?(.*)\)")
    excel_table_syntax = re.compile(r"excel-table\[(.*)\]\((.*)\?(.*)\)")


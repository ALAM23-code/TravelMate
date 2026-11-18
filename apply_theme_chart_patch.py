"""Make Plotly charts and Streamlit dataframes respect TravelMate's theme.

Run this once from the TravelMate project root after copying app.py/ui.py.
This only updates presentation arguments; it does not touch the database.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DYNAMIC_FONT = 'font_color=("#E8EEF8" if st.session_state.get("theme_mode") == "Dark" else "#172B4D")'
DYNAMIC_TABLE_THEME = 'theme=("dark" if st.session_state.get("theme_mode") == "Dark" else "light"),\n'
SKIP_FILES = {
    "apply_theme_chart_patch.py",
    "app.py",
    "ui.py",
    "db.py",
}


def line_offsets(source):
    offsets = [0]
    for index, char in enumerate(source):
        if char == "\n":
            offsets.append(index + 1)
    return offsets


def absolute_offset(offsets, line_number, column):
    return offsets[line_number - 1] + column


def patch_dataframes(source, filename):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        print(f"Skipped dataframe patch in {filename}: syntax error ({exc}).")
        return source, 0

    offsets = line_offsets(source)
    insertions = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "dataframe"
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            continue
        if any(keyword.arg == "theme" for keyword in node.keywords):
            continue

        close_offset = absolute_offset(
            offsets,
            node.end_lineno,
            node.end_col_offset,
        ) - 1
        close_line_start = offsets[node.end_lineno - 1]
        prefix = source[close_line_start:close_offset]

        if prefix.strip() == "":
            # For the common multiline call layout, insert a new argument
            # immediately before the closing-parenthesis line.
            insertion = close_line_start
            argument_indent = prefix + "    "
            insertions.append(
                (insertion, argument_indent + DYNAMIC_TABLE_THEME)
            )
        else:
            # Inline call such as st.dataframe(df): add the argument before ')'.
            before_close = source[:close_offset].rstrip()
            separator = "" if before_close.endswith(",") else ", "
            insertions.append(
                (close_offset, separator + DYNAMIC_TABLE_THEME.strip().rstrip(","))
            )

    for insertion, text in sorted(insertions, reverse=True):
        source = source[:insertion] + text + source[insertion:]

    return source, len(insertions)


def patch_plotly_font(source):
    old_variants = (
        'font_color="#172B4D"',
        "font_color='#172B4D'",
    )
    updated = source
    for old in old_variants:
        updated = updated.replace(old, DYNAMIC_FONT)
    return updated


def main():
    candidates = [
        path for path in ROOT.glob("*.py")
        if path.name not in SKIP_FILES
    ]

    if not candidates:
        print("No manager modules found in this folder.")
        return

    for path in candidates:
        original = path.read_text(encoding="utf-8")
        updated, dataframe_count = patch_dataframes(original, path.name)
        updated = patch_plotly_font(updated)

        if updated != original:
            try:
                ast.parse(updated)
            except SyntaxError as exc:
                print(
                    f"Skipped changes to {path.name}: patched code did not "
                    f"pass syntax validation ({exc})."
                )
                continue

            path.write_text(updated, encoding="utf-8")
            print(
                f"Updated {path.name}: {dataframe_count} table theme(s) "
                "and any hard-coded Plotly font colors."
            )
        else:
            print(f"No theme changes needed in {path.name}.")

    print("Theme chart/table patch complete. No database files were changed.")


if __name__ == "__main__":
    main()

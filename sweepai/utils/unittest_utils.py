from dataclasses import dataclass

from black import FileMode, format_str
from loguru import logger


@dataclass
class DecomposedScript:
    imports: str
    definitions: str
    main: str


def split_script(script: str):
    import_section = []
    class_section = []
    main_section = []
    current_section = import_section

    for line in script.split("\n"):
        if line.startswith("import"):
            current_section = import_section
        elif line.startswith("class") or line.startswith("def"):
            current_section = class_section
        elif line.startswith("if __name__"):
            current_section = main_section
        current_section.append(line)

    return DecomposedScript(
        imports="\n".join(import_section).strip("\n"),
        definitions="\n".join(class_section).strip("\n"),
        main="\n".join(main_section).strip("\n"),
    )


def remove_constants_from_imports(imports: str) -> str:
    last_index = 0
    for index, line in enumerate(imports.splitlines()):
        if line.startswith("from") or line.startswith("import"):
            last_index = index
    return "\n".join(imports.splitlines()[: last_index + 1])


def remove_duplicates(seq: list) -> list:
    new_list = []
    compare_set = set()
    for item in seq:
        normalized_item = item.replace("'", '"')
        if normalized_item not in compare_set:
            compare_set.add(normalized_item)
            new_list.append(item)
    return new_list


def fuse_scripts(
    sections: list[str], do_remove_main: bool = True, do_format: bool = True
):
    decomposed_scripts = [split_script(section) for section in sections]
    imports = remove_duplicates([script.imports for script in decomposed_scripts])
    definitions = remove_duplicates(
        [script.definitions for script in decomposed_scripts]
    )
    main = remove_duplicates([script.main for script in decomposed_scripts])
    result = "\n\n".join(
        [
            "\n".join(imports),
            "\n".join(definitions),
            "\n".join(main) if not do_remove_main else "",
        ]
    )

    if do_format:
        try:
            result = format_str(result, mode=FileMode())
        except Exception as e:
            logger.exception(e)

    return result + "\n"


script_content_1 = """
import a
import b

class Foo:
    pass

if __name__ == '__main__':
    pass
"""

script_content_2 = """
import b
import d

def bar():
    pass

if __name__ == '__main__':
    pass
"""

if __name__ == "__main__":
    # Example usage:
    fused_script = fuse_scripts([script_content_2, script_content_2])
    print(fused_script)

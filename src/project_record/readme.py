"""Updates only an explicitly marked README region."""

from difflib import unified_diff
from pathlib import Path

from .core import RecordError


START, END = "<!-- project-record:start -->", "<!-- project-record:end -->"


def update_readme(path: Path, module: str, write: bool = False) -> dict:
    """Previews or applies one generated region without changing other prose.

    Args:
        path: The existing README with exactly one ordered marker pair.
        module: The generated module, with the same marker pair.
        write: True applies the change; false returns a reviewable diff only.

    Returns:
        The changed flag and unified diff, including when no write was requested.
    """
    original = path.read_bytes().decode("utf-8")
    for text in [original, module]:
        if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
            raise RecordError("README updates require exactly one ordered marker pair")
    replacement = module[module.index(START):module.index(END) + len(END)]
    result = original[:original.index(START)] + replacement + original[original.index(END) + len(END):]
    diff = "".join(unified_diff(original.splitlines(True), result.splitlines(True), fromfile=str(path), tofile=str(path)))
    if write and result != original:
        temporary = path.with_name(path.name + ".project-record.tmp")
        temporary.write_bytes(result.encode("utf-8"))
        temporary.replace(path)
    return {"changed": result != original, "written": write and result != original, "diff": diff}

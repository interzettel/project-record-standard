"""Checks that the committed README graphic matches the public ledger.

Run after the public pipeline with --records pointing to its output.
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Compares the generated graphic and marked text with committed output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, required=True)
    args = parser.parse_args()
    generated = args.records / 'standard'
    if (ROOT / 'assets/progress.svg').read_bytes() != (generated / 'progress.svg').read_bytes():
        raise SystemExit('Regenerate assets/progress.svg from the public pipeline')
    module = (generated / 'README-module.md').read_text().strip()
    if module not in (ROOT / 'README.md').read_text():
        raise SystemExit('Update the marked README module from the public pipeline')
    print('README text and graphic match the public source record')


if __name__ == '__main__':
    main()

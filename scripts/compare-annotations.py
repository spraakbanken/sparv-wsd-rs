#!/usr/bin/env python3
"""Script to validate 'sense' and 'sense_rs' attributes on tokens."""

import sys
from xml.etree import ElementTree as ET


def main() -> None:
    """Program to compare 'sense' and 'sense_rs' attributes."""
    example_file = sys.argv[1] if len(sys.argv) > 1 else "assets/small/bet-2018-2021-1-short_export.gold.xml"
    tree = ET.parse(example_file)
    root = tree.getroot()
    failures = _walk_and_validate_node(root)
    if failures:
        print("Validation failed", file=sys.stderr)  # noqa: T201
        for failure in failures:
            print(failure, file=sys.stderr)  # noqa: T201
        sys.exit(1)


def _walk_and_validate_node(node: ET.Element) -> list[str]:
    failures = []
    if node.tag == "token":
        sense_attr = node.attrib["sense"]
        sense_rs_attr = node.attrib["sense_rs"]
        if sense_attr != sense_rs_attr:
            failure = f"   fail: '{sense_attr}' != '{sense_rs_attr}' (sense != sense_rs) for {node.text=}"
            failures.append(failure)
            print(failure, file=sys.stderr)  # noqa: T201
        print(f"   ok: '{sense_attr}' == '{sense_rs_attr}' (sense == sense_rs) for {node.text=}", file=sys.stderr)  # noqa: T201

    for child in node:
        failures.extend(_walk_and_validate_node(child))
    return failures


if __name__ == "__main__":
    main()

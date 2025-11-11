#!/usr/bin/env python3
"""Script to validate 'sense' and 'sense_rs' attributes on tokens."""

import sys
from xml.etree import ElementTree as ET


def main() -> None:
    """Program to compare 'sense' and 'sense_rs' attributes."""
    example_file = sys.argv[1] if len(sys.argv) > 1 else "assets/small/bet-2018-2021-1-short_export.gold.xml"
    allowed_failures = int(sys.argv[2]) if len(sys.argv) > 2 else 30  # noqa: PLR2004
    tree = ET.parse(example_file)
    root = tree.getroot()
    failures, num_tokens = _walk_and_validate_node(root)
    if failures:
        print("=== Failures ===", file=sys.stderr)  # noqa: T201
        for failure in failures:
            print(failure, file=sys.stderr)  # noqa: T201
        print(  # noqa: T201
            f"Found {len(failures)} differences out of {num_tokens} ({len(failures) / num_tokens * 100:.2f} % failures)",  # noqa: E501
            file=sys.stderr,
        )
        if len(failures) > allowed_failures:
            print(f"Validation failed! Found {len(failures)} differences, when only {allowed_failures} where allowed.")  # noqa: T201
            sys.exit(1)


def _walk_and_validate_node(node: ET.Element) -> tuple[list[str], int]:
    failures = []
    num_tokens = 0
    if node.tag == "token":
        num_tokens += 1
        try:
            sense_attr = node.attrib["wsd.sense"]
        except KeyError:
            print(f"{node.attrib=}", file=sys.stderr)  # noqa: T201
            raise
        sense_rs_attr = node.attrib["sbx_wsd_rs.sense"]
        if sense_attr != sense_rs_attr:
            failure = f"   fail: '{sense_attr}' != '{sense_rs_attr}' (wsd.sense != sbx_wsd_rs.sense) for {node.text=}"
            failures.append(failure)
            # print(failure, file=sys.stderr)
        # else:
        # print(f"   ok: '{sense_attr}' == '{sense_rs_attr}' (sense == sense_rs) for {node.text=}", file=sys.stderr)

    for child in node:
        child_failures, child_num_tokens = _walk_and_validate_node(child)
        failures.extend(child_failures)
        num_tokens += child_num_tokens
    return failures, num_tokens


if __name__ == "__main__":
    main()

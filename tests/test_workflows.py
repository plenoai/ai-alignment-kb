"""Regression tests for GitHub Actions workflow runtime compatibility.

GitHub forced Node.js 20 actions onto Node.js 24 and reports a warning
annotation when an action still declares ``using: node20``. Warning annotations
are converted into issues by the repair controller, so every JavaScript action
used by this repository must resolve to a Node.js 24 runtime.

The minimum versions below are the first releases whose action metadata declares
Node.js 24. Composite actions are checked through the action they embed; for
example, ``upload-pages-artifact@v5`` uses ``upload-artifact@v7`` (Node.js 24),
while ``upload-pages-artifact@v4`` still embeds ``upload-artifact@v4``
(Node.js 20).

Actions must also be pinned to a full-length commit SHA. A mutable tag or branch
allows an upstream compromise to change the code that runs here, so each
``uses`` reference keeps the human-readable release in a trailing comment.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"

NODE24_MINIMUM = {
    "actions/checkout": 5,
    "actions/configure-pages": 6,
    "actions/deploy-pages": 5,
    "actions/github-script": 8,
    "actions/setup-node": 6,
    "actions/setup-python": 6,
    "actions/upload-artifact": 6,
    "actions/upload-pages-artifact": 5,
}

USES_RE = re.compile(
    r"^\s*-?\s*uses:\s*"
    r"(?P<action>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@"
    r"(?P<ref>[^\s#'\"]+)"
    r"(?:\s*#\s*(?P<tag>v?[0-9]+(?:\.[0-9]+)*))?",
    re.MULTILINE,
)

FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")


def action_major(match: re.Match[str]) -> int | None:
    """Return the major version for a tag or a SHA-pinned action, if known."""
    ref = match.group("ref")
    version = ref if re.fullmatch(r"v?[0-9]+(?:\.[0-9]+)*", ref) else match.group("tag")
    if not version:
        return None
    return int(re.match(r"v?([0-9]+)", version).group(1))


class WorkflowRuntimeTests(unittest.TestCase):
    def test_workflows_use_node24_action_runtimes(self) -> None:
        failures: list[str] = []
        for workflow in sorted(WORKFLOW_DIR.glob("*.yml")):
            text = workflow.read_text(encoding="utf-8")
            for match in USES_RE.finditer(text):
                action = match.group("action")
                minimum = NODE24_MINIMUM.get(action)
                if minimum is None:
                    continue
                major = action_major(match)
                if major is None:
                    failures.append(
                        f"{workflow.name}: {action} is pinned to a SHA without "
                        "a readable version comment"
                    )
                elif major < minimum:
                    failures.append(
                        f"{workflow.name}: {action}@{match.group('ref')} uses "
                        f"Node.js 20; use v{minimum} or newer"
                    )
        self.assertEqual([], failures, "\n".join(failures))

    def test_actions_are_pinned_to_full_length_commit_shas(self) -> None:
        failures: list[str] = []
        for workflow in sorted(WORKFLOW_DIR.glob("*.yml")):
            text = workflow.read_text(encoding="utf-8")
            for match in USES_RE.finditer(text):
                action = match.group("action")
                ref = match.group("ref")
                tag = match.group("tag")
                if not FULL_SHA_RE.fullmatch(ref):
                    failures.append(
                        f"{workflow.name}: {action}@{ref} is not pinned to a "
                        "full-length commit SHA"
                    )
                if tag is None:
                    failures.append(
                        f"{workflow.name}: {action}@{ref} is missing a release "
                        "version comment"
                    )
        self.assertEqual([], failures, "\n".join(failures))

    def test_pages_workflow_deploys_docs_with_node24_actions(self) -> None:
        workflow = WORKFLOW_DIR / "pages.yml"
        self.assertTrue(workflow.is_file(), "the Pages deployment workflow is missing")
        text = workflow.read_text(encoding="utf-8")

        self.assertRegex(text, r"(?m)^\s*workflow_dispatch:\s*$")
        self.assertRegex(text, r"(?m)^\s*branches:\s*\[\"main\"\]\s*$")
        self.assertRegex(text, r"(?m)^\s*pages:\s*write\s*$")
        self.assertRegex(text, r"(?m)^\s*id-token:\s*write\s*$")
        self.assertRegex(
            text, r"actions/upload-pages-artifact@[0-9a-f]{40}\s+# v5"
        )
        self.assertRegex(text, r"actions/deploy-pages@[0-9a-f]{40}\s+# v5")
        self.assertRegex(text, r"(?m)^\s*path:\s*docs\s*$")

    def test_pages_artifacts_exist(self) -> None:
        for name in ("index.html", "404.html"):
            self.assertTrue(
                (ROOT / "docs" / name).is_file(),
                f"docs/{name} is required by the Pages deployment",
            )


if __name__ == "__main__":
    unittest.main()

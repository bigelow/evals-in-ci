"""Schema check: every fixture must validate against its Kubernetes schema.

Runs kubeconform (pinned in mise.toml) in strict mode. Kubernetes 1.34.1
schemas cover the GA resource.k8s.io/v1 DRA types; the CRDs-catalog location
covers Gateway API, which is a CRD and absent from the core schemas.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURES = sorted((Path(__file__).resolve().parent.parent / "fixtures").glob("*.yaml"))

KUBECONFORM_ARGS = [
    "-strict",
    "-kubernetes-version", "1.34.1",
    "-schema-location", "default",
    "-schema-location",
    "https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json",
]


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_fixture_matches_schema(fixture: Path):
    kubeconform = shutil.which("kubeconform")
    assert kubeconform, (
        "kubeconform not on PATH — it is pinned in mise.toml; run `mise install`"
    )
    result = subprocess.run(
        [kubeconform, *KUBECONFORM_ARGS, str(fixture)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{fixture.name}: failed strict kubeconform schema validation:\n"
        f"{result.stdout}{result.stderr}"
    )

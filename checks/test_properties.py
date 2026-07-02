"""Property checks: claims kubeconform's schemas can't express.

A manifest can be schema-valid and still violate house rules — missing
resource bounds, floating image tags, or the pre-GA DRA request shape.
Each assertion names the fixture and the violated property.
"""

from pathlib import Path

import pytest
import yaml

FIXTURES = sorted((Path(__file__).resolve().parent.parent / "fixtures").glob("*.yaml"))


def containers(doc):
    """Yield (location, container) for every container in a workload doc."""
    if doc.get("kind") == "Pod":
        pod_spec = doc.get("spec", {})
    else:
        pod_spec = doc.get("spec", {}).get("template", {}).get("spec", {})
    for field in ("initContainers", "containers"):
        for c in pod_spec.get(field, []):
            yield f"{doc['kind']}/{doc['metadata']['name']} {field}[{c['name']}]", c


def docs(fixture):
    return [d for d in yaml.safe_load_all(fixture.read_text()) if d]


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_containers_set_requests_and_limits(fixture: Path):
    for doc in docs(fixture):
        for location, container in containers(doc):
            resources = container.get("resources", {})
            for bound in ("requests", "limits"):
                assert resources.get(bound), (
                    f"{fixture.name}: {location} does not set resources.{bound} — "
                    f"every container must declare resource requests and limits"
                )


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_no_image_uses_latest_tag(fixture: Path):
    for doc in docs(fixture):
        for location, container in containers(doc):
            image = container["image"]
            tag = image.rsplit("/", 1)[-1].partition(":")[2]
            assert tag and tag != "latest", (
                f"{fixture.name}: {location} uses image '{image}' — "
                f"images must pin an explicit tag, never :latest (or no tag, "
                f"which defaults to :latest)"
            )


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_resourceclaimtemplates_use_ga_request_shape(fixture: Path):
    for doc in docs(fixture):
        if doc.get("kind") != "ResourceClaimTemplate":
            continue
        name = doc["metadata"]["name"]
        assert doc.get("apiVersion") == "resource.k8s.io/v1", (
            f"{fixture.name}: ResourceClaimTemplate/{name} uses apiVersion "
            f"'{doc.get('apiVersion')}' — DRA claims must use the GA "
            f"resource.k8s.io/v1 API"
        )
        requests = doc["spec"]["spec"]["devices"]["requests"]
        assert requests, (
            f"{fixture.name}: ResourceClaimTemplate/{name} declares no device "
            f"requests — a claim template must request at least one device"
        )
        for request in requests:
            assert "exactly" in request or "firstAvailable" in request, (
                f"{fixture.name}: ResourceClaimTemplate/{name} device request "
                f"'{request.get('name')}' names its device class outside "
                f"'exactly'/'firstAvailable' — the GA resource.k8s.io/v1 shape "
                f"nests deviceClassName and count under one of those, not on "
                f"the request itself"
            )

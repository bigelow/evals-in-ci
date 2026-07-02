# Evals in CI: a minimal working example

[![ci](https://github.com/bigelow/evals-in-ci/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bigelow/evals-in-ci/actions/workflows/ci.yml)

This repo runs evals as ordinary CI checks: two verifiers over the same four
vendored Kubernetes manifests, on every push. There is no framework and no
harness — just pytest, a pinned validator, and a GitHub Actions job small
enough to read in one screen. The point is that an eval is only as good as
what its checks can actually verify, so I built the two tiers side by side.

## The two tiers

The schema tier is [checks/test_schema.py](checks/test_schema.py). It runs
kubeconform in strict mode against every fixture, using the Kubernetes 1.34.1
schemas (where the `resource.k8s.io/v1` DRA types are GA) plus a CRD catalog
for Gateway API. This catches everything a schema can express: unknown
fields, wrong types, retired API versions.

The property tier is [checks/test_properties.py](checks/test_properties.py).
It parses the same fixtures with PyYAML and asserts three things a schema
cannot: every container declares resource requests and limits, every image
pins a real tag rather than `:latest`, and every ResourceClaimTemplate uses
the GA `resource.k8s.io/v1` request shape. When one of these fails, the
message names the file and the violated property — a red check that doesn't
say why is off-thesis.

## Provenance

The fixtures are vendored from
[bigelow/kubernetes-2026](https://github.com/bigelow/kubernetes-2026) at a
pinned commit, recorded file by file in
[fixtures/PROVENANCE.md](fixtures/PROVENANCE.md). Pinning is the point: a
claim about these manifests is evidence tied to an inspectable state, not to
whatever the source repo happens to contain today.

## Run it

    mise install
    mise run test

## Evidence trail

Every commit in this repo has an [Entire.io](https://entire.io) session
checkpoint recorded alongside it, so the work that built the verifier is
itself inspectable — you can trace each check back to the session that wrote
it, the same way the checks trace each fixture back to its source.

## Companion essay

The essay this repo accompanies:
[Test the Agent Like You Test the Code](https://bigelow.github.io/posts/evals-as-ci/).

## License

Apache 2.0 — see [LICENSE](LICENSE).

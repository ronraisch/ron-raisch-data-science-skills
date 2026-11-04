---
name: gitlab-cicd
description: "Design or review GitLab CI/CD for a small multi-service monorepo: change-scoped jobs, OpenShift integration/production deployment, immutable container provenance, and automatic versioned Python package publication to Artifactory."
---

Credential prerequisite: **Before any local agent operation that accesses GitLab or OpenShift, load [agent-credentials](../agent-credentials/SKILL.md)**. Use only its personal GitLab login and approved NFS ServiceAccount kubeconfig; missing/invalid credentials require a stop and human provisioning instructions. For CI jobs, use explicitly authorized runner credentials; never borrow a researcher's login or silently discover alternatives.

Start with: repository tree, affected-service/shared dependency map, existing GitLab runner/executor capabilities, registry/Artifactory endpoints, OpenShift namespaces, deployment identities, and release policy. Do not assume any credential or environment exists.

## Do

1. Inspect existing pipelines, Dockerfiles, Python package metadata, dependency edges, runner capabilities and deployment resources before changing CI. Preserve working jobs and local conventions. Treat CI files as executable deployment code; request authorization before widening modification scope.
2. For roughly 5–10 services, use one root `.gitlab-ci.yml` with `include:local` and `include:rules:changes` for each component's local CI file. This yields **one combined pipeline**, not separate child pipelines. Include the component's CI file and its relevant shared dependencies in change paths. Handle merge requests, new branches, tags, manual and scheduled pipelines explicitly; do not assume `rules:changes` behaves like a normal push on all sources.
3. Give each service independently named test, build, integration-deploy and production-deploy jobs. Use `needs` for service-local DAG execution; use stage barriers or integration gates when services must ship together. On successful changes to the default branch, automatically deploy affected services to **integration**; offer **manual, protected production** promotion of the **same previously built image**. Do not automatically deploy to production.
4. Build/push container images with immutable commit-based tags (`CI_COMMIT_SHA`); embed `org.opencontainers.image.revision` and record pipeline/build identity. Resolve and retain the registry **digest** for exact binary provenance. Deploy by digest when practical; annotate the OpenShift Deployment with the source SHA, image digest and pipeline ID. No production rebuild.
5. For each Python package, test on relevant code changes but **do not build distributions for routine commits**. On an explicit, new, package-specific semantic-version Git tag pointing to a commit reachable from the protected default branch, validate the tag against package metadata, test, build wheel/sdist once, and **automatically publish** to a PyPI-format Artifactory repository. Keep older versions accessible. Do not overwrite an existing version; version fixes as new patch releases. Preserve the full commit SHA and distribution checksums as release provenance. Consumers should use exact package version pins when isolation is required.
6. Follow [agent-credentials](../agent-credentials/SKILL.md) for **local** agent authentication. For **CI jobs**, explicitly configure approved runner/job identity (protected/masked CI variables, trusted runners, or intentionally mounted NFS kubeconfig) and narrowly scoped OpenShift service accounts or GitLab Kubernetes Agent access. If a CI runner cannot read its configured credential source, stop rather than searching paths or taking credentials from the developer. Separate integration from production credentials, namespaces and protected environments. A runner's GitLab registration identity is **not** cluster deployment authorization. Configure image-pull credentials independently. Never put tokens in YAML/logs or disable TLS verification.
7. Share only common, stable CI patterns as templates/scripts; keep each service's logic local. Ensure publish jobs cannot run on normal pushes, cannot overwrite a package version, and build artifacts are passed to publishing rather than rebuilt. Check concurrency, failure propagation, stale pipeline deployment and emergency rollback paths.
8. Verify with GitLab CI Lint, dry-run/change-path cases, runner compatibility checks, and a nonproduction pipeline. Test: single-service edit, shared-library edit, CI-file edit, MR, main merge, unrelated tag, valid release tag, duplicate tag/version, failed test, integration success/failure, protected manual prod. Record what was actually executed; never claim a deployment was tested from YAML inspection alone.

See [implementation patterns](references/patterns.md) for concise sample YAML and safety caveats.

## Deliver

Root and service-local CI files; reusable build/deploy scripts where justified; dependency/change-trigger matrix; secret/RBAC/environment setup instructions; artifact-to-commit provenance contract; and observed validation results.

## Stop

No verified runner/registry/cluster access means deliver a reviewed configuration, **not** a claimed deployment. Block release on unmatched/non-main tag, test failure, existing Artifactory version, missing provenance, unavailable image/digest, unauthorized production identity, or unsafe secret exposure. Never silently broaden deployment permissions or skip release protection.

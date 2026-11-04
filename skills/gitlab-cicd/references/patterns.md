# GitLab CI/CD patterns for a small monorepo

Illustrative fragments, **not** a drop-in production pipeline. Adapt runner images, TLS trust, OpenShift RBAC, registry settings and repository paths. Validate against the GitLab version in use.

## 1. Layout and root includes

```text
.gitlab-ci.yml
ci/build-image.sh
ci/deploy-openshift.sh
services/sam2/.gitlab-ci.yml
apps/api/.gitlab-ci.yml
packages/my-utils/.gitlab-ci.yml
packages/my-utils/pyproject.toml
```

```yaml
stages: [test, build, deploy, publish]

include:
  - local: services/sam2/.gitlab-ci.yml
    rules:
      - if: '$CI_COMMIT_BRANCH || $CI_PIPELINE_SOURCE == "merge_request_event"'
        changes:
          - services/sam2/**/*
          - shared/python/**/*
          - ci/build-image.sh
          - ci/deploy-openshift.sh
  - local: packages/my-utils/.gitlab-ci.yml
    rules:
      - if: '$CI_COMMIT_TAG =~ /^my-utils-v[0-9]+\.[0-9]+\.[0-9]+$/'
      - if: '$CI_COMMIT_BRANCH || $CI_PIPELINE_SOURCE == "merge_request_event"'
        changes:
          - packages/my-utils/**/*
```

A changed `.gitlab-ci.yml` under the component's directory matches the corresponding glob. Extend the paths for transitive shared-library dependencies. For root CI changes and exceptional pipeline sources, decide explicitly whether to run all relevant jobs. `rules:changes` can evaluate true without a push comparison; use `compare_to` where applicable. Tag-rule ordering matters. Add `workflow:rules` to avoid duplicate branch/MR pipelines according to the team's workflow.

## 2. Per-service DAG and environment promotion

```yaml
sam2-test:
  stage: test
  image: python:3.12
  script:
    - python -m pip install -r services/sam2/requirements.txt
    - python -m pytest services/sam2/tests/

sam2-build:
  stage: build
  needs: [sam2-test]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  script:
    - ./ci/build-image.sh sam2 "$CI_REGISTRY_IMAGE/sam2:$CI_COMMIT_SHA"

sam2-integ:
  stage: deploy
  needs: [sam2-build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  environment:
    name: integration/sam2
    deployment_tier: staging
  resource_group: sam2-integ
  script:
    - ./ci/deploy-openshift.sh integration sam2 "$CI_REGISTRY_IMAGE/sam2:$CI_COMMIT_SHA"

sam2-prod:
  stage: deploy
  needs: [sam2-integ]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
  environment:
    name: production/sam2
    deployment_tier: production
  resource_group: sam2-prod
  script:
    - ./ci/deploy-openshift.sh production sam2 "$CI_REGISTRY_IMAGE/sam2:$CI_COMMIT_SHA"
```

Build requires a runner-supported image builder (Buildah in suitable OpenShift environments, otherwise supported Docker/BuildKit); the script must push an image and capture its digest in an artifact or registry query. Deploy should resolve the image **digest** and assert it matches the image built in that pipeline; use the same digest in integration and production. A commit SHA alone does not guarantee identical image bytes. Production deployment must use protected environments/approvals and disallow unauthorized CI modifications; `when: manual` alone is insufficient. Use GitLab deployment-order safety for delayed older pipelines. If using `needs`, do not rely on global stages for a cross-service release gate.

## 3. Versioned Python package, automatic publication

A tag such as `my-utils-v1.4.3` references a commit; it is not 'inside main'. Verify the commit is reachable from the protected default branch, and protect tag creation. CI must also check that the distribution's version matches the tag.

```yaml
my-utils-test:
  stage: test
  image: python:3.12
  script:
    - python -m pip install -e "packages/my-utils[test]"
    - python -m pytest packages/my-utils/tests/

my-utils-build:
  stage: build
  image: python:3.12
  needs: [my-utils-test]
  rules:
    - if: '$CI_COMMIT_TAG =~ /^my-utils-v[0-9]+\.[0-9]+\.[0-9]+$/'
  variables:
    GIT_DEPTH: "0"
  script:
    - git fetch origin "$CI_DEFAULT_BRANCH"
    - git merge-base --is-ancestor "$CI_COMMIT_SHA" "origin/$CI_DEFAULT_BRANCH"
    - python -m pip install build twine
    - python ci/check-package-version.py packages/my-utils "$CI_COMMIT_TAG"
    - cd packages/my-utils
    - python -m build
    - twine check dist/*
    - sha256sum dist/* > dist/SHA256SUMS
    - printf '%s\n' "$CI_COMMIT_SHA" > dist/SOURCE_COMMIT
  artifacts:
    paths: [packages/my-utils/dist/]

my-utils-publish:
  stage: publish
  image: python:3.12
  needs:
    - job: my-utils-build
      artifacts: true
  rules:
    - if: '$CI_COMMIT_TAG =~ /^my-utils-v[0-9]+\.[0-9]+\.[0-9]+$/'
  script:
    - python -m pip install twine
    - python -m twine upload --non-interactive --repository-url "$ARTIFACTORY_PYPI_URL" packages/my-utils/dist/*.whl packages/my-utils/dist/*.tar.gz
```

`ci/check-package-version.py` above is a **required project-specific implementation**, not supplied by this skill: read the static `project.version` (or the selected VCS-versioning backend's computed distribution version) and compare it with the tag; fail closed on mismatch. A `needs` dependency on a job excluded by rules can break pipeline creation: match release inclusion across dependent jobs (the test job above always exists when this file is included). Securely configure `TWINE_USERNAME` and `TWINE_PASSWORD` as protected variables. Artifactory must reject overwriting a published package (no redeploy/delete permission for CI). Publish checksum/provenance files separately into immutable Artifactory metadata storage if long-term retention is required, rather than assuming Twine uploads them. Optionally check package existence first to produce a clearer error; always let Artifactory enforce immutability.

Do not push modified tags, publish over an existing version, or make downstream consumers automatically accept a new version if exact pinning is intended. Version changes are intentional; ordinary commits test without building distributions.

## 4. Deployment traceability

```dockerfile
ARG GIT_COMMIT
LABEL org.opencontainers.image.revision=$GIT_COMMIT
```

```bash
# Inside supported image-build script
docker build --build-arg GIT_COMMIT="$CI_COMMIT_SHA" -t "$IMAGE" .
docker push "$IMAGE"

# Inside authenticated OpenShift deploy script, after pinning image digest
oc -n "$NAMESPACE" set image "deployment/$SERVICE" "$SERVICE=$IMAGE_BY_DIGEST"
oc -n "$NAMESPACE" annotate "deployment/$SERVICE" \
  "ci.git.commit=$CI_COMMIT_SHA" \
  "ci.git.pipeline=$CI_PIPELINE_ID" \
  "ci.image.digest=$IMAGE_DIGEST" --overwrite
oc -n "$NAMESPACE" rollout status "deployment/$SERVICE" --timeout=180s
```

`IMAGE_BY_DIGEST`, `IMAGE_DIGEST`, `NAMESPACE`, and the authenticated session must come from verified build output/CI environment, **not guessed values**. A GitLab Runner registration token is not an OpenShift API credential. Prefer Kubernetes Agent or separate least-privilege Service Accounts for integration/production. Use CA trust, never insecure TLS flags.

## 5. Validation checklist

- One combined pipeline has jobs only for affected components; shared changes trigger all relevant consumers.
- Tests fail before build/deploy; `needs` does not accidentally bypass required cross-service gates.
- No service builds from a package-version tag alone; no package distribution builds for ordinary commits.
- New protected package tag on main: test → build → publish automatically; existing versions remain available and immutable.
- Image labels/tags, stored digest, deployed digest, and OpenShift annotations all identify the same commit and artifact.
- Integration auto-deploys only after allowed successful default-branch builds; production requires authorized human approval and promotes the same digest.
- A failed/stale pipeline cannot silently deploy an old image over a newer deployment.
- Check the real GitLab CI Lint output and run representative cases on a nonproduction runner before enabling production.

# Optional research-record browser

```bash
python -m dashboard.build PROJECT_A PROJECT_B --output /tmp/research.html
```

Open the HTML file directly. It is a static snapshot, with no server, database, JavaScript, API keys or internet access. Rebuild after records change. It revalidates available run evidence before showing best results. Invalid projects are shown as errors rather than silently omitted.


Record text is escaped, external URLs are not followed, and a restrictive content security policy blocks scripts. Optional tracker links can remain in manifests for human reference; the dashboard makes no tracker API calls. Only build trusted local records: a static output can contain private research text. This tool does not publish or upload it.

## Quick local hosting

From the repository root, with Python 3.11+ (no pip installs):

```bash
python -m dashboard --demo
```

Open **http://127.0.0.1:8080**. Stop with Ctrl+C. Use your own project or an existing snapshot:

```bash
python -m dashboard /path/to/my-study /path/to/another-study
python -m dashboard --html /path/to/research.html
```

With uv, prefix the same command with `uv run --no-project`, e.g. `uv run --no-project python -m dashboard --demo`. Nothing contacts an external service. If the port is busy, add `--port 8081`. For deliberate LAN access, add `--host 0.0.0.0`; the default binds only to your computer. There is no application login, so share only a snapshot appropriate for the network you expose it to.

Only `/`, `/index.html`, and `/healthz` are served. Project folders, datasets, checkpoints, source files and directory listings are never served. Project mode renders once on startup: restart after changing records. HTML mode reopens the file for each request, so replacing the snapshot takes effect on refresh. Invalid individual records remain visible in the rendered report. The standalone exported HTML still works with no host at all.

## Quick OpenShift installation

Requires Python 3.11+, the `oc` CLI, an existing login, and a selected project where you can create builds, workloads and routes:

```bash
oc login YOUR_CLUSTER
oc project YOUR_PROJECT
python -m dashboard.openshift.install /path/to/my-study
```

The installer renders locally, uploads only the HTML as a ConfigMap, builds the small hosting image in OpenShift, creates a Deployment/Service/TLS Route, waits for rollout and prints the HTTPS URL. No local Docker installation or cluster-admin/SCC grant is required. Your cluster must support Docker-strategy binary builds and have its internal image registry enabled for the default build path. Re-run the same command to publish updated records; resource names are stable (`research-records`). It targets the **currently selected namespace** and prints it before applying resources.

Already exported the page? Use:

```bash
python -m dashboard.openshift.install --html /path/to/research.html
```

The HTML contains research notes and is uploaded to the selected cluster. The generated Route uses edge TLS and redirects HTTP; it does not add login or identity management. Use your organization's existing ingress/access controls if the snapshot is private. The workload runs with an arbitrary non-root UID, dropped capabilities, no service-account token, a read-only root filesystem and a read-only ConfigMap mount. No PVC, database, dependency installation or tracker access is needed.

### Disconnected clusters and prebuilt images

Mirror an approved Python 3.11+ image into your internal registry, preferably by digest, then:

```bash
python -m dashboard.openshift.install /path/to/my-study \
  --base-image registry.internal/python:3.12-slim
```

The binary build sends only `serve.py` and `Containerfile`; it does not fetch Git, pip packages or research files. The unpinned default base is convenient for first use; pin your approved image digest for repeatable production builds.

If in-cluster builds or the internal registry are disabled, build/push once using your normal image tooling:

```bash
podman build -f dashboard/Containerfile -t registry.internal/research-records:v1 .
podman push registry.internal/research-records:v1
python -m dashboard.openshift.install /path/to/my-study \
  --image registry.internal/research-records:v1
```

`--image` skips building; the cluster must be able to pull that image (configure namespace pull secrets if required). To run that image locally:

```bash
python -m dashboard.build /path/to/my-study --output /tmp/research-snapshot/index.html
podman run --rm --read-only --user 12345:0 -p 127.0.0.1:8080:8080 \
  -v /tmp/research-snapshot:/snapshot:ro,Z registry.internal/research-records:v1
```

The ConfigMap path intentionally supports snapshots up to 900 KiB; larger snapshots fail before cluster changes. Select fewer projects or shorten notes. No silent truncation is performed.

### Operations and troubleshooting

```bash
oc get pods -l app=research-records
oc logs deployment/research-records
oc logs -f bc/research-records
oc rollout status deployment/research-records
oc get route research-records
```

ConfigMap refresh is eventually consistent; reload the browser after the update propagates. The installer also restarts the Deployment. A failure stops installation with the oc error; fix it and rerun. Use a new namespace if another application already uses these resource names. Uninstall this dashboard only with:

```bash
oc delete route,service,deployment,buildconfig,imagestream research-records
oc delete configmap research-records-html
```

The manifests are in [openshift/template.yaml](openshift/template.yaml); inspect them before installation. Binary-build and arbitrary-UID behavior follow [Red Hat's build-input documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.13/html/builds/creating-build-inputs) and [image guidance](https://docs.redhat.com/en/documentation/openshift_container_platform/4.6/html/images/creating-images).

Validation: local HTTP serving, fixed routes, traversal rejection, snapshot updates, size limits and installer command/staging behavior are tested. No Docker/Podman runtime, `oc` CLI or live OpenShift cluster is available in the development environment; container image builds and actual cluster rollout have not been executed here.

Component projects add a hierarchy/version table, approved run scopes, scope/runtime/contract failures, external artifact references, optional ZenML/tracker links and dated research events. The existing findings, comparable verified results and pause/resume notes remain. Rebuild the snapshot after record changes. NFS/file/HF references are links/metadata only: the host still serves HTML, never the artifacts. Opening an NFS reference requires a mounted share and browser/OS support.

# Optional self-hosted ClearML

The skills and records work without this integration. Local evidence stays authoritative; ClearML is a mirror and optional execution backend. No server is started or configured by the core workflow.

## License and capability review (2026-10-30)

| Component / capability | Reviewed primary source | Use here |
| --- | --- | --- |
| Python SDK | [repository/license](https://github.com/clearml/clearml), Apache-2.0 | Explicit opt-in logging and offline SDK mode |
| Agent | [license](https://github.com/clearml/clearml-agent/blob/master/LICENSE), Apache-2.0; [workers/queues](https://clear.ml/docs/latest/docs/fundamentals/agents_and_queues/) | Optional CPU worker/queue execution |
| Server and Web-App | [Server README](https://github.com/clearml/clearml-server), [SSPL-1.0 license](https://github.com/clearml/clearml-server/blob/master/LICENSE) | Self-hosted task/metric/artifact/dataset records |
| Experiment comparison | [Web-App comparison](https://clear.ml/docs/latest/docs/webapp/webapp_exp_comparing/) | Reuse existing parameter/scalar/plot/artifact comparison; do not rebuild it |
| Dataset versions | [Dataset SDK](https://clear.ml/docs/latest/docs/references/sdk/dataset/) | Immutable finalized dataset ID plus local digests |
| Task SDK/offline | [Task API](https://clear.ml/docs/latest/docs/references/sdk/task/) | connect, report_scalar, upload_artifact, set_offline, execute_remotely |

SDK and Agent are open-source Apache-2.0. Server is source-available under SSPL, which is [not OSI-approved open source](https://opensource.org/blog/the-sspl-is-not-an-open-source-license). Read the actual license, including section 13 obligations if offering its functionality as a service. It does not become MIT through this repository. We do not redistribute the server or its compose stack.

The documented self-hosted stack includes experiment history, scalar/parameter comparison, artifact browsing, versioned datasets and worker queues. Enterprise marketing/UI pages can describe additional paid features; SSO/RBAC, commercial orchestration/control-plane dashboards, Hyper-Datasets and proprietary enterprise applications are not dependencies or promises of this integration. Exact entitlements can change: confirm against the selected server version, not a generic marketing page. The local dashboard assembles our own continuity records; it is not a replacement for paid ClearML applications.

## Server setup

Use the [official Linux/macOS deployment procedure](https://clear.ml/docs/latest/docs/deploying_clearml/clearml_server_linux_mac/) including Docker prerequisites, persistent directories, permissions, host settings and backup procedure. It requires at least 8 GB RAM (16 GB recommended). Web/API/file services use 8080/8008/8081. The default deployment has unrestricted access; apply the official security configuration before exposing it beyond a trusted local host.

The upstream HEAD examined during this implementation was `2ebdc43951b9432cc7fa528bbb3a7100fc6fe805`. For a reproducible deployment choose a reviewed server release/commit, fetch its official compose file, and pin all referenced images/digests. Example fetch after reviewing that revision:

```bash
curl -fsSL https://raw.githubusercontent.com/clearml/clearml-server/2ebdc43951b9432cc7fa528bbb3a7100fc6fe805/docker/docker-compose.yml -o /opt/clearml/docker-compose.yml
# After completing the official directory/permission/security setup:
docker compose -f /opt/clearml/docker-compose.yml config
docker compose -f /opt/clearml/docker-compose.yml pull
docker compose -f /opt/clearml/docker-compose.yml up -d
```

A pinned compose Git revision alone does not pin mutable container tags. Record resolved image digests and deployment environment. This stack was not deployed in this session. For air-gapped use pre-transfer images, wheels, Git sources and datasets; see offline.md.

## SDK configuration and logging

```bash
uv sync --extra clearml
uv run clearml-init
```

Point initialization at **your self-hosted server**, or copy tools/clearml/clearml.conf.example to ~/clearml.conf and insert locally generated credentials. Do not commit credentials. Run the core example first, then mirror one run:

```bash
python -m examples.demo --output /tmp/clearml-local-study
uv run python -m tools.clearml.log_run /tmp/clearml-local-study \
  /tmp/clearml-local-study/specs/logistic.json \
  /tmp/clearml-local-study/runs/logistic/runtime.json
```

For a network-free SDK session, add `--offline`. ClearML's SDK stores an offline session for later explicit import; this does not replace the local file records. See Task.set_offline/import_offline_session documentation. Core users need not install the SDK at all.

The adapter records spec ID, dataset/split digests, evaluation protocol, actual observed runtime objects, scalar result, spec/runtime JSON, verification and checkpoint/history/source artifacts. Parameter mirroring sets `ignore_remote_overrides=True`: a tracker mirror must not change the evidence it is uploading. Upload failure propagates but cannot delete the local run. Process/verification failures remain explicit in the uploaded JSON.

In the Web-App, select compatible tasks and click COMPARE; compare parameters, last scalar values, plots and artifacts using the existing interface. Review local verification status first. SDK auto-capture is convenient but does not prove that intended weights, preprocessing or evaluation executed.

## Dataset-version references

Basic integration already records local dataset and split SHA-256. To additionally use ClearML Data:

```python
from clearml import Dataset
from tools.experiment_verification import digest

version = Dataset.create(dataset_project="sensor-study", dataset_name="readings", dataset_version="1.0.0")
version.add_files(path="/tmp/clearml-local-study/data.csv")
version.add_files(path="/tmp/clearml-local-study/splits.json")
version.upload()
version.finalize()
print(version.id)  # Save the immutable ID and local digests in your experiment record.

# Later: materialize that exact finalized ID, then re-hash actual local files.
local = Dataset.get(dataset_id=version.id, only_completed=True).get_local_copy()
```

A version label/ID is a reference, not proof of which bytes the trainer read. Do not silently resolve “latest” for a reproducible run. Upload only data you intend to place on that backend. No dataset is uploaded by the default demo.

## Optional remote registration and execution

Commit and push this repository to a worker-accessible Git remote first. Install clearml-agent on the CPU worker, configure it for the same backend, and create/select a queue named `cpu`:

```bash
uv tool install clearml-agent
clearml-agent init
clearml-agent daemon --queue cpu --foreground
```

On the submitting host, register and enqueue the example:

```bash
uv run python -m tools.clearml.remote_example --queue cpu
```

Without `--queue`, it registers and executes locally. With a queue, `Task.execute_remotely` submits and exits on the host, and the agent runs the recorded code. The SDK's task parameter connection supports output-path overrides; experiment settings are still observed and verified by the local demo. Ensure the agent has compatible Python, packages, dataset access and the exact code revision. Use CPU queues; no NVIDIA runtime is required. The worker creates local records and uploads project/summary artifacts; individual completed runs can then be mirrored with log_run.

Validation boundary: adapter behavior is tested with a fake Task object; SDK calls were checked against official API docs. A live server, actual SDK offline serialization, dataset upload and remote worker were not exercised here. Test those in your selected self-hosted deployment before relying on them.

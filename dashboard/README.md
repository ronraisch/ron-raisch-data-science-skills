# Optional research-record browser

```bash
python -m dashboard.build PROJECT_A PROJECT_B --output /tmp/research.html
```

Open the HTML file directly. It is a static snapshot, with no server, database, JavaScript, API keys or internet access. Rebuild after records change. It revalidates available run evidence before showing best results. Invalid projects are shown as errors rather than silently omitted.

This view assembles the continuity information that lives in these local records: original question, hypothesis status, findings/negative results, pause reason, next experiments and expandable notes. It is a record reader, not an assertion that ClearML lacks project notes or reports. Experiment comparison, charts, resource monitoring, task queues and artifact management already have ClearML interfaces and are not reimplemented here. See docs/clearml.md for the capability review.

Record text is escaped, external URLs are not followed, and a restrictive content security policy blocks scripts. Optional ClearML URLs can remain in manifests for human reference; the dashboard deliberately makes no live ClearML API calls. Only build trusted local records: a static output can contain private research text. This tool does not publish or upload it.

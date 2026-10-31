"""Mirror completed local evidence to an explicitly selected ClearML backend."""
import argparse
from pathlib import Path
from tools.experiment_verification import load_json
from tools.experiment_verification.core import resolve


def log_run(root, spec_path, runtime_path, task_class=None, offline=False):
    if task_class is None:
        from clearml import Task
        task_class=Task
    spec=load_json(spec_path);run=load_json(runtime_path)
    if offline:
        task_class.set_offline(offline_mode=True)
    task=task_class.init(project_name="Ron's Data Science Skills / examples", task_name=run["run_id"],
                         reuse_last_task_id=False, auto_connect_frameworks=False,
                         auto_connect_arg_parser=False)
    try:
        # Disable parameter override: this mirrors completed runs, never mutates intent.
        task.connect({"spec_id":spec["id"],"dataset_sha256":spec["dataset"]["sha256"],
                      "split_sha256":spec["splits"]["sha256"],"evaluation_protocol":spec["evaluation_protocol"]},
                     name="ResearchRecord", ignore_remote_overrides=True)
        task.connect(run["observations"], name="ObservedRuntime", ignore_remote_overrides=True)
        task.get_logger().report_scalar(title=spec["expected"]["metric"]["name"], series=spec["expected"]["metric"]["split"],
                                       value=run["result"], iteration=0)
        for name,path in (("spec",spec_path),("runtime",runtime_path)):
            task.upload_artifact(name=name,artifact_object=str(path),wait_on_upload=True)
        external=[a for a in run['artifacts'] if a.get('uri')]
        if external:
            task.connect({'references':external},name='ExternalArtifacts',ignore_remote_overrides=True)
        if spec.get('components'):
            task.connect(spec['components'],name='ComponentScope',ignore_remote_overrides=True)
        for artifact in run["artifacts"]:
            if artifact.get('uri'):continue # Preserve references; never upload NFS checkpoints implicitly.
            task.upload_artifact(name=Path(artifact["path"]).name,artifact_object=str(resolve(root,artifact["path"])),wait_on_upload=True)
        folder=Path(runtime_path).parent
        task.upload_artifact(name="verification",artifact_object=str(folder/"verification.json"),wait_on_upload=True)
        return task.id
    finally:
        task.close()


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("root",type=Path);p.add_argument("spec",type=Path);p.add_argument("runtime",type=Path);p.add_argument("--offline",action="store_true")
    a=p.parse_args();print(log_run(a.root,a.spec,a.runtime,offline=a.offline))

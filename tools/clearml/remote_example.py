"""Opt-in ClearML task registration and remote CPU execution.
Run only after publishing this repository at a worker-accessible revision.
"""
import argparse
from clearml import Task


def main(queue=None):
    task=Task.init(project_name="Ron's Data Science Skills / examples",task_name="CPU research demonstration",
                   reuse_last_task_id=False,auto_connect_frameworks=False,auto_connect_arg_parser=False)
    params={"output":"/tmp/clearml-study-"+task.id}
    task.connect(params,name="Demo")
    # On the worker, returns and executes the code below; on the submitting host
    # enqueues this task and exits. No GPU required. Commit/push before submission.
    if queue:
        task.execute_remotely(queue_name=queue,exit_process=True)
    from examples.demo import build
    root=build(params["output"])
    task.upload_artifact(name="project",artifact_object=str(root/"project.json"),wait_on_upload=True)
    task.upload_artifact(name="summary",artifact_object=str(root/"summary.md"),wait_on_upload=True)
    task.close()


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--queue",default=None);a=p.parse_args();main(a.queue)

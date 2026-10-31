"""Optional OSS local pipeline; standalone experiment code remains authoritative."""
from pathlib import Path
from zenml import step, pipeline
from zenml.client import Client
from tools.experiment_verification.core import load_json, save_json, verify, digest
from tools.experiment_verification.records import validate_project


@step(enable_cache=False)
def execute_component_study(output: str) -> dict:
    from examples.component_study.demo import build
    root=build(output)
    spec=load_json(root/'specs/decoder.json')
    return {'project':str(root),'spec':str(root/'specs/decoder.json'),'spec_sha256':digest(root/'specs/decoder.json'),
            'components':spec['components'],'artifacts':load_json(root/'project.json')['external_artifacts']}


@step(enable_cache=False)
def verify_component_study(record: dict) -> dict:
    root=Path(record['project']);spec_path=Path(record['spec'])
    _,errors=validate_project(root)
    if errors:raise ValueError('; '.join(errors))
    report=verify(load_json(spec_path),load_json(root/'runs/decoder/runtime.json'),root,spec_path)
    if report['status']!='verified':raise AssertionError(report)
    return {'project':str(root),'verification':report['status'],'components':report['components'],
            'spec_sha256':digest(spec_path),'artifacts':record['artifacts']}


@pipeline(enable_cache=False)
def component_research(output: str):
    verify_component_study(execute_component_study(output))


def run(output):
    result=component_research(output=str(Path(output).resolve()))
    # SDK pipeline invocation returns a PipelineRunResponse on the supported release.
    run_id=str(result.id)
    metadata={'zenml_run_id':run_id,'status':str(result.status),'stack_id':str(Client().active_stack.id),
              'steps':{name:str(value.id) for name,value in result.steps.items()},
              'scope_note':'Research components need not be ZenML steps; this pipeline groups execution and verification.'}
    save_json(Path(output)/'records/zenml.json',metadata)
    return metadata


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();print(run(a.output))

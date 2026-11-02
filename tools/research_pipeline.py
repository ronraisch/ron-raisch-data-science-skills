"""Author pipeline topology in trusted Python; JSON exports are run evidence only."""
from dataclasses import dataclass, field
from pathlib import Path
from .experiment_verification.core import save_json
from .experiment_verification.components import validate_manifest


@dataclass(frozen=True)
class Component:
    id: str
    path: str
    purpose: str
    sources: tuple = ()
    dependencies: tuple = ()
    version: str = '1.0.0'
    inputs: dict = field(default_factory=lambda: {'type':'object'})
    outputs: dict = field(default_factory=lambda: {'type':'object'})
    config: dict = field(default_factory=dict)
    config_schema: dict = field(default_factory=lambda: {'type':'object'})
    invariants: tuple = ('Execute declared contract tests',)
    contract_tests: tuple = ('contract',)

    def record(self):
        from dataclasses import asdict
        result=asdict(self)
        for key in ('sources','dependencies','invariants','contract_tests'):result[key]=list(result[key])
        return result


@dataclass(frozen=True)
class Pipeline:
    components: tuple
    watch: tuple = ('**/*.py','**/*.lock','**/*.toml')
    record_roots: tuple = ('runs','records','artifacts','.git','.venv','__pycache__')

    def manifest(self):
        return validate_manifest({'schema_version':1,'components':[c.record() for c in self.components],
                                  'watch':list(self.watch),'record_roots':list(self.record_roots)})

    def export(self,path):
        save_json(Path(path),self.manifest())
        return Path(path)

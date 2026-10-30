#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'skills');
const exists = p => {try {fs.lstatSync(p); return true;} catch (e) {if (e.code === 'ENOENT') return false; throw e;}};
const available = () => fs.readdirSync(source).filter(n => exists(path.join(source,n,'SKILL.md'))).sort();
const help = `Ron's Data Science Skills

  list
  install <skill...|all> [--agent codex|claude] [--destination PATH]
  serve <project...|--demo|--html FILE> [--port 8080]
  deploy <project...|--html FILE> [--image IMAGE]

Install defaults to .agents/skills in the current directory.
Linked skills are included; existing directories are never overwritten.
Skill installation needs Node only. serve/deploy need Python 3.11+;
deploy also needs an oc login. Set PYTHON to select an interpreter.
`;

function install(args) {
  let destination, agent;
  const names = [];
  for (let i=0; i<args.length; i++) {
    const arg=args[i];
    if (arg==='--destination' || arg==='--agent') {
      const value=args[++i];
      if (!value || value.startsWith('--')) throw new Error(`Missing value for ${arg}`);
      if (arg==='--destination') destination=value; else agent=value;
    } else if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    else names.push(arg);
  }
  if (agent && !['codex','claude'].includes(agent)) throw new Error('Agent must be codex or claude');
  if (destination && agent) throw new Error('Choose --destination or --agent');
  if (!names.length || new Set(names).size!==names.length || (names.includes('all') && names.length!==1)) throw new Error('Choose unique skill names or all');
  const known=new Set(available());
  const queue=names[0]==='all' ? [...known] : [...names];
  const closure=new Set();
  while (queue.length) {
    const name=queue.pop();
    if (!known.has(name)) throw new Error(`Unknown skill: ${name}`);
    if (closure.has(name)) continue;
    closure.add(name);
    const text=fs.readFileSync(path.join(source,name,'SKILL.md'),'utf8');
    for (const m of text.matchAll(/\]\(\.\.\/([a-z0-9-]+)\/SKILL\.md\)/g)) queue.push(m[1]);
  }
  const target=path.resolve(destination ?? (agent==='claude' ? '.claude/skills' : '.agents/skills'));
  const selected=[...closure].sort();
  for (const name of selected) if (exists(path.join(target,name))) throw new Error(`Already exists: ${path.join(target,name)}. Nothing installed.`);
  fs.mkdirSync(target,{recursive:true});
  const created=[];
  try {
    for (const name of selected) {
      const dest=path.join(target,name);
      fs.mkdirSync(dest); created.push(dest);
      for (const entry of fs.readdirSync(path.join(source,name))) {
        fs.cpSync(path.join(source,name,entry),path.join(dest,entry),{recursive:true,force:false,errorOnExist:true});
      }
    }
  } catch (e) {
    for (const dest of created.reverse()) fs.rmSync(dest,{recursive:true,force:true});
    throw e;
  }
  console.log(`Installed ${selected.length} skills into ${target}:\n${selected.join('\n')}`);
}

const [command,...args]=process.argv.slice(2);
try {
  if (!command || ['help','--help','-h'].includes(command)) console.log(help);
  else if (command==='list') console.log(available().join('\n'));
  else if (command==='install') install(args);
  else if (command==='serve' || command==='deploy') {
    const module=command==='serve' ? 'dashboard.serve' : 'dashboard.openshift.install';
    const python=process.env.PYTHON || (process.platform==='win32' ? 'python' : 'python3');
    // Preserve the caller's working directory, so project paths stay relative to the user.
    const code="import sys,runpy;sys.path.insert(0,sys.argv.pop(1));runpy.run_module(sys.argv.pop(1),run_name='__main__')";
    const result=spawnSync(python,['-c',code,root,module,...args],{stdio:'inherit'});
    if (result.error) throw new Error(`Cannot run ${python}. Install Python 3.11+ or set PYTHON. ${result.error.message}`);
    process.exitCode=result.status ?? 1;
  } else throw new Error(`Unknown command: ${command}. Run with --help.`);
} catch (e) {console.error(e.message); process.exitCode=1;}

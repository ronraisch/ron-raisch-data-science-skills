#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {requestAgentsConsent,inspectAgentsFile,appendAgentsParagraph} from './research-onboarding.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'skills');
const exists = p => {try {fs.lstatSync(p); return true;} catch (e) {if (e.code === 'ENOENT') return false; throw e;}};
const available = () => fs.readdirSync(source).filter(n => exists(path.join(source,n,'SKILL.md'))).sort();
const help = `Ron's Data Science Skills

  list
  install <skill...|all> [--agent codex|claude] [--destination PATH]
          [--with-agents|--no-agents] [--agents-md PATH]
  serve <project...|--demo|--html FILE> [--port 8080]
  deploy <project...|--html FILE> [--image IMAGE]

Install defaults to .agents/skills in the current directory.
Linked skills are included; existing directories are never overwritten.
Interactive installation offers an optional research-triggering AGENTS.md paragraph.
Noninteractive installs leave it unchanged unless --with-agents is supplied.
Skill installation needs Node only. serve/deploy need Python 3.11+;
deploy also needs an oc login. Set PYTHON to select an interpreter.
`;

async function install(args) {
  let destination, agent, agentsFile='AGENTS.md', mode;
  const names = [];
  for (let i=0; i<args.length; i++) {
    const arg=args[i];
    if (arg==='--with-agents' || arg==='--no-agents') {
      if (mode) throw new Error('Choose only one of --with-agents or --no-agents');
      mode=arg==='--with-agents' ? 'yes' : 'no';
    } else if (arg==='--destination' || arg==='--agent' || arg==='--agents-md') {
      const value=args[++i];
      if (!value || value.startsWith('--')) throw new Error(`Missing value for ${arg}`);
      if (arg==='--destination') destination=value; else if (arg==='--agent') agent=value; else agentsFile=value;
    } else if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    else names.push(arg);
  }
  if (agent && !['codex','claude'].includes(agent)) throw new Error('Agent must be codex or claude');
  if (destination && agent) throw new Error('Choose --destination or --agent');
  if (!names.length || new Set(names).size!==names.length || (names.includes('all') && names.length!==1)) throw new Error('Choose unique skill names or all');
  const known=new Set(available());
  if (names.some(n=>n!=='all' && !known.has(n))) throw new Error('Unknown skill: '+names.find(n=>n!=='all' && !known.has(n)));
  const filename=path.resolve(agentsFile);
  const paragraph=fs.readFileSync(path.join(root,'templates/agents-research.md'),'utf8');
  const consent=await requestAgentsConsent({mode,filename,paragraph});
  if (consent) inspectAgentsFile(filename,paragraph);
  const queue=names[0]==='all' ? [...known] : [...names];
  if (consent && !queue.includes('research-start')) queue.push('research-start');
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
        fs.cpSync(path.join(source,name,entry),path.join(dest,entry),{recursive:true,force:false,errorOnExist:true,filter:src=>path.basename(src)!=='__pycache__' && !src.endsWith('.pyc')});
      }
    }
  } catch (e) {
    for (const dest of created.reverse()) fs.rmSync(dest,{recursive:true,force:true});
    throw e;
  }
  console.log(`Installed ${selected.length} skills into ${target}:\n${selected.join('\n')}`);
  if (consent) console.log(appendAgentsParagraph(filename,paragraph) ? `Added research triggering paragraph to ${filename}` : `Research paragraph already present in ${filename}; preserved it.`);
  else console.log('AGENTS.md unchanged. Opt in with --with-agents; it also installs research-start.');
  if (selected.includes('research-start')) console.log('To begin: ask your agent “Use research-start to begin this research project.”');
}

const [command,...args]=process.argv.slice(2);
try {
  if (!command || ['help','--help','-h'].includes(command)) console.log(help);
  else if (command==='list') console.log(available().join('\n'));
  else if (command==='install') await install(args);
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

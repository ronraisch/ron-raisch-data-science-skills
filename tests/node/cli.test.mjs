import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const cli=path.join(root,'bin/cli.mjs');
const call=(args,cwd=root)=>spawnSync(process.execPath,[cli,...args],{cwd,encoding:'utf8'});
const temp=fn=>{const d=fs.mkdtempSync(path.join(os.tmpdir(),'ron-skills-'));try{fn(d);}finally{fs.rmSync(d,{recursive:true,force:true});}};

test('lists all 20 skills',()=>{const r=call(['list']);assert.equal(r.status,0);assert.equal(r.stdout.trim().split('\n').length,20);});
test('install includes transitive siblings and assets',()=>temp(d=>{const r=call(['install','research-resume','--destination',d]);assert.equal(r.status,0,r.stderr);for(const name of ['research-resume','research-handoff','research-summary','experiment-verify'])assert.ok(fs.existsSync(path.join(d,name,'SKILL.md')));assert.ok(fs.existsSync(path.join(d,'research-summary/references/record-contract.md')));}));
test('rejects unknown skill before writing',()=>temp(d=>{assert.equal(call(['install','research-resume','bad','--destination',d]).status,1);assert.deepEqual(fs.readdirSync(d),[]);}));
test('refuses overwrite before copying any skill',()=>temp(d=>{fs.mkdirSync(path.join(d,'research-summary'));const r=call(['install','all','--destination',d]);assert.equal(r.status,1);assert.deepEqual(fs.readdirSync(d),['research-summary']);}));
test('claude destination is relative to caller',()=>temp(d=>{const r=call(['install','research-grill','--agent','claude'],d);assert.equal(r.status,0,r.stderr);assert.ok(fs.existsSync(path.join(d,'.claude/skills/research-grill/SKILL.md')));}));
test('rejects conflicting or malformed options',()=>{for(const args of [['install'],['install','all','research-grill'],['install','all','--agent','bad'],['install','all','--destination'],['install','all','--agent','codex','--destination','x']])assert.equal(call(args).status,1);});
test('Python launcher returns usage from outside checkout',()=>temp(d=>{const r=call(['serve','--help'],d);assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/read-only research dashboard/);}));

test('offline install bundles upstream methods and supporting scripts',()=>temp(d=>{const r=call(['install','eda','--destination',d]);assert.equal(r.status,0,r.stderr);for(const f of ['METHOD.md','scripts/eda_analyzer.py','assets/report_template.md'])assert.ok(fs.existsSync(path.join(d,'eda/references/upstream',f)));}));

test('new skills install with their portable contracts and dependencies',()=>temp(d=>{const r=call(['install','production-validator','--destination',d]);assert.equal(r.status,0,r.stderr);for(const name of ['production-validator','production-handoff','component-design','experiment-verify'])assert.ok(fs.existsSync(path.join(d,name,'SKILL.md')));assert.ok(fs.existsSync(path.join(d,'component-design/references/component-contract.md')));}));

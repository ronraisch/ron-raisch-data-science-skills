import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {requestAgentsConsent,appendAgentsParagraph} from '../../bin/research-onboarding.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const paragraph=fs.readFileSync(path.join(root,'templates/agents-research.md'),'utf8');
const temp=fn=>{const d=fs.mkdtempSync(path.join(os.tmpdir(),'research-onboarding-'));try{fn(d);}finally{fs.rmSync(d,{recursive:true,force:true});}};
const cli=(args,cwd)=>spawnSync(process.execPath,[path.join(root,'bin/cli.mjs'),...args],{cwd,encoding:'utf8'});

test('interactive consent previews exact paragraph, filename, scope expansion and defaults no',async()=>{
  for(const [answer,expected] of [['',false],['n',false],['yes',true],['Y',true]]) {
    let preview='';let question='';
    const result=await requestAgentsConsent({filename:'/project/AGENTS.md',paragraph,input:{isTTY:true},output:{isTTY:true,write:s=>preview+=s},ask:async q=>{question=q;return answer;}});
    assert.equal(result,expected);assert.ok(preview.includes(paragraph.trim()));assert.ok(preview.includes('/project/AGENTS.md'));assert.ok(preview.includes('linked skills'));assert.ok(question.includes('[y/N]'));
  }
});
test('noninteractive and explicit opt out never ask',async()=>{
 for(const options of [{input:{isTTY:false},output:{isTTY:true}},{input:{isTTY:true},output:{isTTY:false}},{mode:'no',input:{isTTY:true},output:{isTTY:true}}])assert.equal(await requestAgentsConsent({...options,ask:()=>assert.fail('Must not prompt')}),false);
 assert.equal(await requestAgentsConsent({mode:'yes'}),true);
});
test('append preserves original prose and edited block; repeat is idempotent',()=>temp(d=>{
 const filename=path.join(d,'AGENTS.md');fs.writeFileSync(filename,'Existing instructions without newline');
 assert.equal(appendAgentsParagraph(filename,paragraph),true);const content=fs.readFileSync(filename,'utf8');assert.ok(content.startsWith('Existing instructions without newline\n\n'));
 fs.writeFileSync(filename,content.replace('Load one phase at a time.','My custom phase rule.'));
 assert.equal(appendAgentsParagraph(filename,paragraph),false);assert.ok(fs.readFileSync(filename,'utf8').includes('My custom phase rule.'));
}));
test('symlink and malformed managed blocks are refused',()=>temp(d=>{
 const file=path.join(d,'AGENTS.md'),original=path.join(d,'source.md');fs.writeFileSync(original,'Keep me');fs.symlinkSync(original,file);
 assert.throws(()=>appendAgentsParagraph(file,paragraph),/symlink/);assert.equal(fs.readFileSync(original,'utf8'),'Keep me');fs.unlinkSync(file);
 fs.writeFileSync(file,'<!-- ron-data-science-skills:research-start -->');assert.throws(()=>appendAgentsParagraph(file,paragraph),/Incomplete/);
}));
test('CLI does not write AGENTS.md without affirmative consent',()=>temp(d=>{
 const r=cli(['install','research-start'],d);assert.equal(r.status,0,r.stderr);assert.ok(!fs.existsSync(path.join(d,'AGENTS.md')));assert.ok(fs.existsSync(path.join(d,'.agents/skills/research-start/SKILL.md')));
}));
test('CLI explicit consent adds paragraph and startup dependencies to partial selection',()=>temp(d=>{
 fs.writeFileSync(path.join(d,'AGENTS.md'),'Keep project instructions\n');const r=cli(['install','eda','--with-agents'],d);assert.equal(r.status,0,r.stderr);
 const text=fs.readFileSync(path.join(d,'AGENTS.md'),'utf8');assert.ok(text.startsWith('Keep project instructions\n'));assert.ok(text.includes(paragraph.trim()));
 for(const skill of ['eda','research-start','research-grill','component-design','research-wayfinder','research-resume'])assert.ok(fs.existsSync(path.join(d,'.agents/skills',skill,'SKILL.md')));
}));
test('custom agents file is explicit; conflicting flags fail before modifications',()=>temp(d=>{
 let r=cli(['install','research-start','--with-agents','--no-agents'],d);assert.equal(r.status,1);assert.deepEqual(fs.readdirSync(d),[]);
 r=cli(['install','research-start','--with-agents','--agents-md','instructions/AGENTS.md'],d);assert.equal(r.status,0,r.stderr);assert.ok(fs.existsSync(path.join(d,'instructions/AGENTS.md')));assert.ok(!fs.existsSync(path.join(d,'AGENTS.md')));
}));

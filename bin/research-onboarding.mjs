import fs from 'node:fs';
import path from 'node:path';
import {createInterface} from 'node:readline/promises';

const begin='<!-- ron-data-science-skills:research-start -->';
const end='<!-- /ron-data-science-skills:research-start -->';

export function inspectAgentsFile(filename, paragraph) {
  if (!fs.existsSync(filename)) {
    try {fs.lstatSync(filename); throw new Error('Refusing AGENTS.md symlink');}
    catch (e) {if (e.code!=='ENOENT') throw e;}
    return {content:'',present:false};
  }
  const stat=fs.lstatSync(filename);
  if (stat.isSymbolicLink() || !stat.isFile()) throw new Error('AGENTS.md must be a regular file; symlinks are not modified');
  const content=fs.readFileSync(filename,'utf8');
  const hasBegin=content.includes(begin), hasEnd=content.includes(end);
  if (hasBegin!==hasEnd || hasBegin && content.indexOf(begin)>content.indexOf(end)) throw new Error('Incomplete research skills block in AGENTS.md; inspect it before retrying');
  return {content,present:hasBegin || content.includes(paragraph.trim())};
}

export function appendAgentsParagraph(filename,paragraph) {
  const {content,present}=inspectAgentsFile(filename,paragraph);
  if (present) return false; // Preserve existing and user-edited blocks.
  fs.mkdirSync(path.dirname(filename),{recursive:true});
  const gap=content ? (content.endsWith('\n') ? '\n' : '\n\n') : '';
  fs.appendFileSync(filename,gap+begin+'\n'+paragraph.trim()+'\n'+end+'\n');
  return true;
}

export async function requestAgentsConsent({mode,filename,paragraph,input=process.stdin,output=process.stdout,ask}) {
  if (mode==='yes') return true;
  if (mode==='no') return false;
  if (!input.isTTY || !output.isTTY) return false;
  output.write(`\nOptional research triggering paragraph for ${filename}:\n\n${paragraph.trim()}\n\nThis also includes research-start and its linked skills in this installation.\n`);
  if (ask) return /^(y|yes)$/i.test((await ask('Append this paragraph? [y/N] ')).trim());
  const reader=createInterface({input,output});
  try {return /^(y|yes)$/i.test((await reader.question('Append this paragraph? [y/N] ')).trim());}
  finally {reader.close();}
}

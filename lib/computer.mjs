import {plainRequirements} from './workflow.mjs';

// Read the chapter and every number from the actual requirements, never title.
export function parseComputerReferences(html) {
  const text=plainRequirements(html);
  const match=/^第\s*(十|[一二三四五六七八九]|10|[1-9])\s*章\s*课后习题\s*[:：]\s*(\d+(?:\s*[、，,]\s*\d+)*)\s*[。.]?\s*$/.exec(text);
  if(!match)return {refs:[],supported:false,text};
  const cn='一二三四五六七八九十';
  const chapter=/^\d+$/.test(match[1])?Number(match[1]):cn.indexOf(match[1])+1;
  const numbers=match[2].split(/[、，,]/).map(s=>Number(s.trim()));
  if(numbers.some(n=>n<1) || new Set(numbers).size!==numbers.length)return {refs:[],supported:false,text};
  return {refs:numbers.map(n=>`${chapter}/${n}`),supported:true,text};
}

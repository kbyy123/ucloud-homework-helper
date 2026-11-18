import {plainRequirements} from './workflow.mjs';

// Printed exercise-page ranges verified against the 2021 BUPT textbook TOC.
const groups=[[1,33,37],[2,65,68],[3,105,108],[4,143,146],[5,157,158],[6,173,174],[7,190,191],[8,206,207],[9,225,228],[10,257,260],[11,271,271]];

export function parseProbabilityReferences(html) {
  const text=plainRequirements(html),lines=text.split('\n').map(s=>s.trim()).filter(Boolean),refs=[];
  let section=null,supplement=false;
  const fail=()=>({refs:[],supported:false,text});
  for(const line of lines) {
    if(/^补充作业\s*[:：]$/.test(line)){supplement=true;section=null;continue;}
    const page=/^p\s*(\d+)(?:\s*[-–—－~～]\s*(\d+))?$/i.exec(line);
    if(page) {
      const lo=Number(page[1]),hi=Number(page[2]||page[1]);
      const group=groups.find(([,start,end])=>lo>=start && hi<=end && hi>=lo);
      if(!group)return fail();section=group[0];continue;
    }
    if(supplement) {
      if(/^1\s*[（(]仅[）)]利用概率公理化定义证明不可能事件的概率是零。[（(]要求[，,]证明不同于p18\s*性质4[）)]\s*[；;]?$/i.test(line)) {
        refs.push('supplement/empty-axioms-v1');continue;
      }
      const extra=/^2\s+p35\s+26\s*[；;]?$/i.exec(line);
      if(extra){refs.push('1/26');continue;}
      return fail();
    }
    if(!section)return fail();
    const clause=line.replace(/[；;。.]\s*$/,'');
    if(!/^\d+(?:\s*[（(]\s*\d+\s*[）)])?(?:(?:\s*[,，、]\s*|\s+)\d+(?:\s*[（(]\s*\d+\s*[）)])?)*$/.test(clause))return fail();
    for(const match of clause.matchAll(/(\d+)(?:\s*[（(]\s*(\d+)\s*[）)])?/g)) {
      const n=Number(match[1]),part=match[2]&&Number(match[2]);
      if(n<1 || (match[2] && part<1))return fail();
      refs.push(`${section}/${n}${part?'('+part+')':''}`);
    }
  }
  return {refs:[...new Set(refs)],supported:refs.length>0,text};
}

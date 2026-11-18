import {plainRequirements} from './workflow.mjs';

export const FOURTH_REFS=['4/9','4/14','4/19','4/22(2)','4/26','4/27','4/28','4/34',
  'supplement/bivariate-normal-correlation-v1'];

export function parseProbabilityFourthReferences(html) {
  const text=plainRequirements(html);
  const lines=text.split('\n').map(s=>s.trim()).filter(Boolean);
  const patterns=[
    /^p\s*144\s*[-–—－]\s*146$/i,
    /^9\s+14\s+19\s+22\s*[（(]\s*2\s*[）)]\s+26\s+27\s+28\s+34$/,
    /^证明二维正态分布的两个随机分量[得的]相关系数是第五个参数(?:\\rho|ρ)$/,
  ];
  const supported=lines.length===patterns.length&&lines.every((line,i)=>patterns[i].test(line));
  return {text,supported,refs:supported?[...FOURTH_REFS]:[]};
}

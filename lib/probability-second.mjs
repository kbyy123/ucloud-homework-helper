import {plainRequirements} from './workflow.mjs';

// A source-specific extension, kept separate so earlier bank fingerprints stay
// stable. Unknown wording or added conditions must be reviewed in full.
export function parseProbabilitySecondReferences(html) {
 const text=plainRequirements(html),lines=text.split('\n').map(s=>s.trim()).filter(Boolean);
 const patterns=[/^p35\s+21$/i,
  /^用数学归纳法证明p18\s*一般加法公式，并应用一般加法公式求解p35\s+23$/i,
  /^p35\s+26$/i,
  /^p105\s*[-–—－]\s*108\s+10\s+11\s+15\s+16\s+20\s+26$/i];
 if(lines.length!==patterns.length || lines.some((s,i)=>!patterns[i].test(s)))return {refs:[],supported:false,text};
 return {refs:['1/21','supplement/inclusion-exclusion-induction-v1','1/23','1/26','3/10','3/11','3/15','3/16','3/20','3/26'],supported:true,text};
}

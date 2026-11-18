import {plainRequirements} from './workflow.mjs';
import {inlineImageHashes,canonical} from './group-theory.mjs';

export const SEMIGROUP_REFS=['9.2/16','9.2/20','9.2/30'];
export const SEMIGROUP_REQUIREMENTS='9.2 Exercises：(Sixth Edition) 16（给出具体判断依据）, 20, 30\n（Fourth Edition）18,26 and below:\nDetermine whether the set together with the binary operation is a semigroup, a monoid, or neither. If it is a monoid, specify the identity. If it is a semigroup or a monoid, determine if it is commutative. Give your reason.16. The set of integers of the form , where * is ordinary multiplication.';
export const SEMIGROUP_IMAGE_HASH='d3919d3744f2ec3c1c3cfa6fcb03580fb89b5c8dcc99d43df48a1fba1c798917';
export function parseSemigroupReferences(html,chapter) {
 const text=plainRequirements(html),images=inlineImageHashes(html);
 const supported=chapter==='Group Theory'&&canonical(text)===canonical(SEMIGROUP_REQUIREMENTS)&&
   images?.length===1&&images[0]===SEMIGROUP_IMAGE_HASH;
 return {text,supported,refs:supported?[...SEMIGROUP_REFS]:[]};
}

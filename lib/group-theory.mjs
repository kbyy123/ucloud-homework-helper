import {createHash} from 'node:crypto';
import {plainRequirements} from './workflow.mjs';

// Match the verified Sixth Edition branch; preserve the Fourth Edition branch
// and inline formula images in the source, never merge its question numbers.
export const GROUP_REFS=['9.1/16','9.1/32','9.1/34'];
export const GROUP_REQUIREMENTS='(Sixth Edition) 9.1 Exercises: 16, 32, 34\n(Fourth Edition）9.1 Exercises: 16, 28 and below:\n34. Define a binary operation on a set by . Is associative? commutative? idempotent?';
export const canonical=s=>String(s).replace(/\s+/g,'');
export function bindGroupTextbook(course,detail) {
 if(course.key!=='离散数学' || detail.chapterName!=='Group Theory')return course;
 const binding=course.chapterBindings?.find(b=>b.chapter==='Group Theory');
 if(!binding)return course;
 if(binding.bookId!=='kolman-6')throw Error('群论教材绑定尚未核验');
 return {...course,...binding};
}
export function inlineImageHashes(html) {
 const images=[...String(html).matchAll(/<img\b[^>]*src="data:image\/png;base64,([A-Za-z0-9+/=]+)"[^>]*>/g)];
 if(images.length!==(String(html).match(/<img\b/gi)||[]).length)return null;
 return images.map(m=>createHash('sha256').update(Buffer.from(m[1],'base64')).digest('hex'));
}
export function parseGroupReferences(html,chapter,expectedImages) {
 const text=plainRequirements(html),images=inlineImageHashes(html);
 const fail=()=>({refs:[],supported:false,text});
 if(chapter!=='Group Theory'||canonical(text)!==canonical(GROUP_REQUIREMENTS)||!images||!expectedImages||
  images.length!==expectedImages.length||images.some((s,i)=>s!==expectedImages[i]))return fail();
 return {refs:[...GROUP_REFS],supported:true,text};
}

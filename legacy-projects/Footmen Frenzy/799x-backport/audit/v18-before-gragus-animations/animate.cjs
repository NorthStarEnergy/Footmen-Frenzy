const fs=require('fs'),path=require('path'),w=require('C:/Users/User/Documents/ChatGPT/Footmen Frenzy/799x-backport/tools/model-tools/node_modules/war3-model');
const src=process.argv[2]||'C:/Users/User/Documents/ChatGPT/Footmen Frenzy/mini-foots/base/files/InfernalGragas.mdx';const dest=process.argv[3]||path.join(__dirname,'InfernalGragas.mdx');
const buf=fs.readFileSync(src),m=w.parseMDX(buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength));
const mul=(a,b)=>{const[x,y,z,w]=a,[X,Y,Z,W]=b;return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]};
const axis=(i,d)=>{let q=[0,0,0,Math.cos(d*Math.PI/360)];q[i]=Math.sin(d*Math.PI/360);return q};
const times=[0,200,450,650,850,1050,1300,1600],weights=[0,.25,1,1,1,1,.55,0];
const seen=new WeakSet();
function visit(o){if(!o||typeof o!=='object'||ArrayBuffer.isView(o)||seen.has(o))return;seen.add(o);
 if(o.Keys&&o.LineType!==undefined&&(o.GlobalSeqId===null||o.GlobalSeqId===undefined)){
 const base=o.Keys.find(k=>k.Frame===1833)||o.Keys.filter(k=>k.Frame<=1833).at(-1)||o.Keys[0];
 if(base){for(let k=0;k<times.length;k++){let v=Array.from(base.Vector);const n=m.Nodes.find(n=>n?.Rotation===o);
 if(n?.ObjectId===35)v=mul(axis(2,20*weights[k]),mul(axis(0,-100*weights[k]),v));
 if(n?.ObjectId===40)v=mul(axis(1,(-15+(k===3?2:k===4?-2:0))*weights[k]),v);
 let key={Frame:44000+times[k],Vector:new Float32Array(v)};if(base.InTan)key.InTan=new Float32Array(v);if(base.OutTan)key.OutTan=new Float32Array(v);o.Keys.push(key);}
 o.Keys.sort((a,b)=>a.Frame-b.Frame);}return;}
 for(const v of Object.values(o))visit(v);
}
visit(m);
if(m.Sequences[9].Name!=='Spell Slam'||m.Sequences[9].Interval[0]!==36167)throw Error('Unexpected model');
m.Sequences[9].Interval[1]=36667;
const seq={...m.Sequences[1],Name:'Spell Drink',Interval:new Uint32Array([44000,45600]),NonLooping:true,Rarity:0,MinimumExtent:new Float32Array([-180,-180,-80]),MaximumExtent:new Float32Array([210,210,370]),BoundsRadius:450};m.Sequences.push(seq);
m.Info.MinimumExtent=new Float32Array([-180,-180,-80]);m.Info.MaximumExtent=new Float32Array([330,250,760]);m.Info.BoundsRadius=850;
for(const g of m.Geosets){if(g.Anims?.length===12)g.Anims.push({MinimumExtent:new Float32Array(seq.MinimumExtent),MaximumExtent:new Float32Array(seq.MaximumExtent),BoundsRadius:seq.BoundsRadius});}
const out=Buffer.from(w.generateMDX(m));fs.writeFileSync(dest,out);const check=w.parseMDX(out.buffer.slice(out.byteOffset,out.byteOffset+out.byteLength));
if(check.Sequences.length!==13||check.Sequences[12].Interval[1]-check.Sequences[12].Interval[0]!==1600)throw Error('Sequence check');
fs.writeFileSync(path.join(__dirname,'animated-model.json'),JSON.stringify(check,(k,v)=>ArrayBuffer.isView(v)?Array.from(v):v));console.log(check.Sequences.map((s,i)=>[i,s.Name,Array.from(s.Interval)]));

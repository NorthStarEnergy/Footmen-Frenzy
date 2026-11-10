const fs=require('fs'),path=require('path');
const w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const root=__dirname;
function files(p){return fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(p,e.name)):[path.join(p,e.name)]);}
const input=files(path.join(root,'assets/original')).find(p=>/\.mdx$/i.test(p));
const b=fs.readFileSync(input),m=w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));
fs.writeFileSync(path.join(root,'assets/Stalker-original.mdl'),w.generateMDL(m));
const report={input,version:m.Version,info:m.Info,sequences:m.Sequences,textures:m.Textures,attachments:m.Attachments,bones:m.Bones.map(n=>({name:n.Name,id:n.ObjectId,parent:n.Parent,pivot:n.PivotPoint,translation:n.Translation})),helpers:m.Helpers,particles:m.ParticleEmitters2,geosets:m.Geosets.map(g=>({vertices:g.Vertices.length/3,faces:g.Faces.length/3,min:g.MinimumExtent,max:g.MaximumExtent})),cameras:m.Cameras};
fs.writeFileSync(path.join(root,'model-inspection.json'),JSON.stringify(report,(k,v)=>ArrayBuffer.isView(v)?Array.from(v):v,2));
console.log(JSON.stringify({version:m.Version,info:m.Info,sequences:m.Sequences.map(s=>({name:s.Name,interval:Array.from(s.Interval)})),textures:m.Textures,bones:report.bones,attachments:m.Attachments},(k,v)=>ArrayBuffer.isView(v)?Array.from(v):v,2));

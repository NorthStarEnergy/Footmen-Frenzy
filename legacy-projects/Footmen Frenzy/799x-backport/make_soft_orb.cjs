// Small matte sphere: standard alpha blending, no additive layers or emitters.
const fs = require('fs'), path = require('path');
const w = require('./tools/model-tools/node_modules/war3-model');
const root = __dirname;
const parse = p => { const b=fs.readFileSync(p); return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)); };
const m = parse(path.join(root,'assets/Spells/Orianna/Feedback/AttackRing.mdx'));
const radius=28, latitude=12, longitude=24, vertices=[], normals=[], uv=[], faces=[];
for(let j=0;j<=latitude;j++) for(let i=0;i<=longitude;i++) {
  const a=Math.PI*j/latitude, b=2*Math.PI*i/longitude;
  const n=[Math.sin(a)*Math.cos(b),Math.sin(a)*Math.sin(b),Math.cos(a)];
  vertices.push(...n.map(v=>v*radius)); normals.push(...n); uv.push(i/longitude,j/latitude);
}
for(let j=0;j<latitude;j++) for(let i=0;i<longitude;i++) {
  const a=j*(longitude+1)+i, b=a+longitude+1;
  if(j>0) faces.push(a,b,a+1);
  if(j<latitude-1) faces.push(a+1,b,b+1);
}
const bounds={BoundsRadius:radius,MinimumExtent:new Float32Array([-radius,-radius,-radius]),MaximumExtent:new Float32Array([radius,radius,radius])};
Object.assign(m.Info,bounds,{Name:'Orianna Soft Orb'});
Object.assign(m.Sequences[0],bounds,{Interval:new Uint32Array([0,1000]),NonLooping:false});
Object.assign(m.Geosets[0],bounds,{Vertices:new Float32Array(vertices),Normals:new Float32Array(normals),Faces:new Uint16Array(faces),VertexGroup:new Uint8Array(vertices.length/3),TVertices:[new Float32Array(uv)]});
m.GeosetAnims[0].Alpha=1;
m.Materials[0].Layers[0].FilterMode=2; // ordinary alpha blend, not additive glow
m.Materials[0].Layers[0].Shading=0;
m.Textures[0].Image='Spells\\Orianna\\Feedback\\SoftOrb.blp';
// A tiny neutral texture with full alpha and mipmaps, using the BLP1 format.
const palette=Buffer.alloc(1024); palette.set([215,210,205,255],0);
const header=Buffer.alloc(156);header.write('BLP1');
[1,8,4,4,5,0].forEach((v,i)=>header.writeUInt32LE(v,4+4*i));
let offset=1180;const levels=[];
for(const [i,size] of [4,2,1].entries()) {
  const count=size*size, data=Buffer.concat([Buffer.alloc(count),Buffer.alloc(count,255)]);
  header.writeUInt32LE(offset,28+i*4);header.writeUInt32LE(data.length,92+i*4);
  levels.push(data);offset+=data.length;
}
const out=path.join(root,'src/Spells/Orianna/Feedback');fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'SoftOrb.blp'),Buffer.concat([header,palette,...levels]));
fs.writeFileSync(path.join(out,'SoftOrb.mdx'),Buffer.from(w.generateMDX(m)));
const checked=parse(path.join(out,'SoftOrb.mdx'));
if(checked.ParticleEmitters2.length || checked.Lights.length || checked.Sequences[0].NonLooping || checked.GeosetAnims[0].Alpha!==1 || checked.Materials[0].Layers[0].FilterMode!==2) throw Error('Invalid soft orb presentation');
// All faces must point outwards, so the sphere remains visible from every angle.
for(let i=0;i<faces.length;i+=3) {
  const p=faces.slice(i,i+3).map(k=>vertices.slice(k*3,k*3+3));
  const a=p[1].map((v,k)=>v-p[0][k]), b=p[2].map((v,k)=>v-p[0][k]);
  const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  if(n.reduce((s,v,k)=>s+v*p[0][k],0)<=0) throw Error('Inward sphere face');
}
fs.writeFileSync(path.join(root,'audit/soft-orb.json'),JSON.stringify({radius,vertices:vertices.length/3,triangles:faces.length/3,loopingStand:true,additiveLayers:0,particles:0,lights:0,texture:m.Textures[0].Image},null,2));
console.log('Matte orb generated and round-trip validated.');

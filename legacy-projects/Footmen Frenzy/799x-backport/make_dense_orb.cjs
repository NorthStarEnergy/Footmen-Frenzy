const fs=require('fs'),path=require('path'),w=require('./tools/model-tools/node_modules/war3-model');
const out=path.join(__dirname,'src/Spells/Orianna/Feedback');
const raw=fs.readFileSync(path.join(out,'SoftOrb.mdx'));
const m=w.parseMDX(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength));
m.Info.Name='Steady Jade Orb';m.Textures[0].Image='Spells\\Orianna\\Feedback\\DenseOrb.blp';
Object.assign(m.Materials[0].Layers[0],{FilterMode:0,Shading:1});
const palette=Buffer.alloc(1024);
for(let i=0;i<256;i++){const light=.3+.7*i/255;palette.set([Math.round(205*light),Math.round(225*light),Math.round(100*light),255],i*4);}
const header=Buffer.alloc(156);header.write('BLP1');[1,8,64,64,5,0].forEach((v,i)=>header.writeUInt32LE(v,4+i*4));
let offset=1180;const levels=[];
for(let size=64,level=0;size>=1;size>>=1,level++){
  const pixels=Buffer.alloc(size*size);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const a=(y+.5)/size*Math.PI,b=(x+.5)/size*2*Math.PI;
    const dot=Math.sin(a)*Math.cos(b)*.4+Math.sin(a)*Math.sin(b)*.2+Math.cos(a)*.89;
    pixels[y*size+x]=Math.round(255*Math.max(0,Math.min(1,.25+.75*Math.max(0,dot))));
  }
  const data=Buffer.concat([pixels,Buffer.alloc(size*size,255)]);header.writeUInt32LE(offset,28+4*level);header.writeUInt32LE(data.length,92+4*level);offset+=data.length;levels.push(data);
}
fs.writeFileSync(path.join(out,'DenseOrb.blp'),Buffer.concat([header,palette,...levels]));
const data=Buffer.from(w.generateMDX(m));fs.writeFileSync(path.join(out,'DenseOrb.mdx'),data);
const checked=w.parseMDX(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength));
if(checked.ParticleEmitters2.length||checked.Lights.length||checked.Materials[0].Layers[0].FilterMode!==0||checked.GeosetAnims[0].Alpha!==1)throw Error('Orb must stay opaque without flashing components');
console.log('Opaque static jade orb validated.');

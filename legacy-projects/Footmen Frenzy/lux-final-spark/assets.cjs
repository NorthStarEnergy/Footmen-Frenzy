// Procedural classic-format Warcraft beam meshes; no external artwork.
const fs=require('fs'), path=require('path');
const w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const root=__dirname,out=path.join(root,'src/Spells/Lux');fs.mkdirSync(out,{recursive:true});
const vec=(...v)=>new Float32Array(v);
const source=fs.readFileSync(path.join(root,'../799x-backport/assets/Spells/Orianna/Feedback/AttackRing.mdx'));
function base(){return w.parseMDX(source.buffer.slice(source.byteOffset,source.byteOffset+source.byteLength));}
function texture(name,flare){
 const n=64,header=Buffer.alloc(156),palette=Buffer.alloc(1024),levels=[];
 header.write('BLP1');[1,8,n,n,5,0].forEach((v,i)=>header.writeUInt32LE(v,4+i*4));
 for(let i=0;i<256;i++)palette.set([i,i,i,255],i*4);
 let offset=1180,level=0;
 for(let size=n;size>=1;size>>=1){
  const pixels=Buffer.alloc(size*size),alpha=Buffer.alloc(size*size,255);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
   const u=(x+.5)/size*2-1,v=(y+.5)/size*2-1;
   const d=flare?Math.hypot(u,v):Math.abs(v);
   const intensity=flare?Math.exp(-d*d*7)*Math.max(0,1-d):Math.pow(Math.max(0,1-d*d),1.7);
   pixels[y*size+x]=Math.round(intensity*255);
  }
  const data=Buffer.concat([pixels,alpha]);header.writeUInt32LE(offset,28+level*4);header.writeUInt32LE(data.length,92+level*4);
  levels.push(data);offset+=data.length;level++;
 }
 fs.writeFileSync(path.join(out,name+'.blp'),Buffer.concat([header,palette,...levels]));
}
const reports=[];
for(const flare of [false,true]){
 const name=flare?'FinalSparkFlare':'FinalSparkBeam',m=base();
 const vertices=[],normals=[],uv=[],faces=[];
 function quad(points,normal){const k=vertices.length/3;for(let i=0;i<4;i++){vertices.push(...points[i]);normals.push(...normal);uv.push(...[[0,0],[1,0],[1,1],[0,1]][i]);}faces.push(k,k+1,k+2,k,k+2,k+3);}
 quad([[-.5,-.5,0],[.5,-.5,0],[.5,.5,0],[-.5,.5,0]],[0,0,1]);
 // The shallow upright plane keeps a luminous volume at low camera angles.
 quad([[-.5,0,-.19],[.5,0,-.19],[.5,0,.19],[-.5,0,.19]],[0,-1,0]);
 if(flare)quad([[0,-.5,-.5],[0,.5,-.5],[0,.5,.5],[0,-.5,.5]],[1,0,0]);
 const bounds={BoundsRadius:4096,MinimumExtent:vec(-4096,-4096,-512),MaximumExtent:vec(4096,4096,512)};
 m.Version=800;Object.assign(m.Info,bounds,{Name:'Final Spark '+(flare?'source flare':'beam segment')});
 // Empty death sequence prevents a residual mesh after DestroyEffect.
 m.Sequences=[{...m.Sequences[0],...bounds,Name:'Stand',Interval:new Uint32Array([0,1000]),NonLooping:false},{...m.Sequences[0],...bounds,Name:'Death',Interval:new Uint32Array([1100,1200]),NonLooping:true}];
 m.Geosets=[{...m.Geosets[0],...bounds,Vertices:vec(...vertices),Normals:vec(...normals),Faces:new Uint16Array(faces),VertexGroup:new Uint8Array(vertices.length/3),TVertices:[vec(...uv)],Anims:[bounds,bounds]}];
 m.GeosetAnims[0].Alpha={LineType:0,GlobalSeqId:null,Keys:[{Frame:0,Vector:vec(1)},{Frame:1000,Vector:vec(1)},{Frame:1100,Vector:vec(0)},{Frame:1200,Vector:vec(0)}]};
 m.GeosetAnims[0].Color=vec(1,1,1);
 m.Materials[0].Layers=[{...m.Materials[0].Layers[0],FilterMode:3,Shading:17,Alpha:1,TextureID:0}];
 m.Textures=[{Image:'Spells\\Lux\\'+name+'.blp',ReplaceableId:0,Flags:0}];
 texture(name,flare);
 const encoded=Buffer.from(w.generateMDX(m));fs.writeFileSync(path.join(out,name+'.mdx'),encoded);
 fs.writeFileSync(path.join(root,name+'.mdl'),w.generateMDL(m));
 const checked=w.parseMDX(encoded.buffer.slice(encoded.byteOffset,encoded.byteOffset+encoded.byteLength));
 if(checked.Version!==800||checked.Geosets[0].Vertices.length!==vertices.length||checked.Textures.length!==1)throw Error('Invalid model '+name);
 if(checked.Materials[0].Layers[0].FilterMode!==3)throw Error('Beam must be additive');
 const b=fs.readFileSync(path.join(out,name+'.blp')),blp=w.decodeBLP(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
 if(w.getBLPImageData(blp,0).width!==64)throw Error('Texture decode failed');
 reports.push({name,bytes:encoded.length,vertices:vertices.length/3,textureDecoded:true,format:800});
}
fs.writeFileSync(path.join(root,'asset-checks.json'),JSON.stringify({models:reports,engine_tested:false},null,2));
console.log('Beam/flare MDX and all BLP mipmaps encoded and decoded.');

const fs=require('fs'),path=require('path'),w=require('./tools/model-tools/node_modules/war3-model');
const root=__dirname,out=path.join(root,'src/Spells/Orianna/Feedback');
const parse=p=>{const b=fs.readFileSync(p);return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
for(const kind of ['MoveGround','AttackGround','ProtectGround','ShockGround','ShockImpact']){
  const m=parse(path.join(root,'assets/Spells/Orianna/Feedback/AttackRing.mdx'));
  const bounds={BoundsRadius:1.5,MinimumExtent:new Float32Array([-1,-1,-.01]),MaximumExtent:new Float32Array([1,1,.01])};
  Object.assign(m.Info,bounds,{Name:'Orianna Soft '+kind});
  Object.assign(m.Sequences[0],bounds,{Interval:new Uint32Array([0,1000]),NonLooping:false});
  Object.assign(m.Geosets[0],bounds,{Vertices:new Float32Array([-1,-1,0,1,-1,0,1,1,0,-1,1,0]),Normals:new Float32Array([0,0,1,0,0,1,0,0,1,0,0,1]),Faces:new Uint16Array([0,1,2,0,2,3]),VertexGroup:new Uint8Array(4),TVertices:[new Float32Array([0,0,1,0,1,1,0,1])]});
  m.GeosetAnims[0].Alpha=1;Object.assign(m.Materials[0].Layers[0],{FilterMode:2,Shading:17});
  m.Textures[0].Image='Spells\\Orianna\\Feedback\\'+kind+'.blp';
  fs.writeFileSync(path.join(out,kind+'.mdx'),Buffer.from(w.generateMDX(m)));
  const checked=parse(path.join(out,kind+'.mdx'));
  if(checked.Geosets[0].Vertices.length!==12||checked.Sequences[0].NonLooping||checked.Materials[0].Layers[0].FilterMode!==2||!fs.existsSync(path.join(out,kind+'.blp')))throw Error('Invalid energy plane '+kind);
}
console.log('Five soft command models generated and round-trip validated.');

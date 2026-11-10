const fs=require('fs'),path=require('path'),w=require('./tools/model-tools/node_modules/war3-model');
const root=__dirname;
const parse=p=>{const b=fs.readFileSync(p);return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
const source=path.join(root,'assets/Models/OriannaEnchantress/BlackLegionEnchantressMissileV2.mdx');
const out=path.join(root,'src/Spells/Orianna/Feedback');
fs.mkdirSync(out,{recursive:true});
const report=[];
for(const kind of ['EnchantressOrb','EnchantressOrbBlue','EnchantressTrail']) {
  const m=parse(source);
  // Keep the author's orb mesh and motion, but avoid repeated missile launch/death
  // sounds and explosive death particles as the persistent effect attaches/detaches.
  m.EventObjects=[];
  m.ParticleEmitters2=m.ParticleEmitters2.slice(0,2);
  for(const p of m.ParticleEmitters2) {
    p.EmissionRate*=0.35;
    p.Alpha=new Uint8Array([120,75,0]);
    p.Visibility={LineType:0,GlobalSeqId:null,Keys:[333,367,667,833,1000,1833].map(Frame=>({Frame,Vector:new Float32Array([Frame<1000?1:0])}))};
    if(kind==='EnchantressOrbBlue')p.SegmentColor=[new Float32Array([.25,.55,1]),new Float32Array([.1,.3,.65]),new Float32Array([.1,.2,.4])];
  }
  if(kind==='EnchantressTrail')m.ParticleEmitters2=[];
  if(kind==='EnchantressOrbBlue') {
    for(const t of m.Textures)if(/Green_/.test(t.Image))t.Image='Textures\\GenericGlowFaded.blp';
    for(const a of m.GeosetAnims)a.Color=new Float32Array([1,1,1]);
  }
  if(kind!=='EnchantressTrail') {
    // A shaded opaque sphere gives the original translucent Enchantress glow
    // a readable solid center, without increasing particle brightness.
    const core=parse(path.join(out,'SoftOrb.mdx'));
    const id=Math.max(...m.Nodes.map(n=>n.ObjectId))+1;
    const bone={...core.Bones[0],Name:'Solid Core',ObjectId:id,GeosetId:m.Geosets.length,GeosetAnimId:m.GeosetAnims.length};
    m.Bones.push(bone);m.Nodes[id]=bone;m.PivotPoints[id]=new Float32Array([0,0,0]);
    const geo=core.Geosets[0];geo.Vertices=new Float32Array(Array.from(geo.Vertices,v=>v*.65));
    geo.Groups=[[id]];geo.MaterialID=m.Materials.length;
    Object.assign(geo,{BoundsRadius:18.2,MinimumExtent:new Float32Array([-18.2,-18.2,-18.2]),MaximumExtent:new Float32Array([18.2,18.2,18.2])});
    const textureName=kind==='EnchantressOrbBlue'?'OrbCoreBlue.blp':'OrbCore.blp';
    const texture=fs.readFileSync(path.join(out,'SoftOrb.blp'));
    texture.set(kind==='EnchantressOrbBlue'?[255,220,185,255]:[185,220,100,255],156);
    fs.writeFileSync(path.join(out,textureName),texture);
    core.Materials[0].Layers[0].TextureID=m.Textures.length;
    core.Materials[0].Layers[0].FilterMode=0;
    m.Textures.push({ReplaceableId:0,Image:'Spells\\Orianna\\Feedback\\'+textureName,Flags:0});
    m.Materials.push(core.Materials[0]);
    m.GeosetAnims.push({...core.GeosetAnims[0],GeosetId:m.Geosets.length});m.Geosets.push(geo);
    const bounds={BoundsRadius:52,MinimumExtent:new Float32Array([-52,-52,-52]),MaximumExtent:new Float32Array([52,52,52])};
    Object.assign(m.Info,bounds);for(const s of m.Sequences)Object.assign(s,bounds);
  }
  fs.writeFileSync(path.join(out,kind+'.mdx'),Buffer.from(w.generateMDX(m)));
  const checked=parse(path.join(out,kind+'.mdx'));
  if(checked.EventObjects.length || checked.ParticleEmitters2.length>2 || !checked.Sequences.some(s=>s.Name==='Stand'&&!s.NonLooping))throw Error('Invalid persistent orb');
  if(kind!=='EnchantressTrail' && (checked.Geosets.length!==2 || checked.Materials.at(-1).Layers[0].FilterMode!==0))throw Error('Missing solid core');
  report.push({kind,particles:checked.ParticleEmitters2.length,textures:checked.Textures.map(t=>t.Image)});
}
fs.writeFileSync(path.join(root,'audit/enchantress/runtime-models.json'),JSON.stringify(report,null,2));
console.log('Enchantress orb variants generated and validated.');

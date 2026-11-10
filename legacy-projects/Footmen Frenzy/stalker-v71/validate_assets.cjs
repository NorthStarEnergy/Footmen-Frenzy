const fs=require('fs'),path=require('path'),w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const R=__dirname,dir=path.join(R,'src/Units/Stalker'),report={};
for(const name of ['Stalker','Disruptor']){
 const b=fs.readFileSync(path.join(dir,name+'.mdx')),m=w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));
 const r=new w.ModelRenderer(m);let samples=0;
 for(const s of m.Sequences)for(let i=0;i<=8;i++){
  r.setFrame(s.Interval[0]+(s.Interval[1]-s.Interval[0])*i/8);r.update(0);samples++;
  for(const n of r.rendererData.nodes)if(n&&Array.from(n.matrix).some(v=>!Number.isFinite(v)))throw Error(name+' nonfinite animation');
 }
 for(const g of m.Geosets){if(Array.from(g.Faces).some(i=>i>=g.Vertices.length/3))throw Error('Bad vertex index');if(g.Anims.length!==m.Sequences.length)throw Error('Sequence extent mismatch');for(const a of g.Anims)if(Array.from(a.MinimumExtent).some((v,i)=>v>a.MaximumExtent[i]))throw Error('Inverted extent');}
 report[name]={format:m.Version,sequences:m.Sequences.length,samples,attachment_count:m.Attachments.length,collision_shapes:m.CollisionShapes.length};
}
for(const p of ['Units/Stalker/Stalker.blp','Units/Stalker/Plasma.blp','Units/Stalker/BTNStalker.blp','ReplaceableTextures/CommandButtonsDisabled/DISBTNStalker.blp']){
 const b=fs.readFileSync(path.join(R,'src',p)),blp=w.decodeBLP(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));let mipmaps=0;
 for(let i=0;i<16&&(blp.width>>i)>0;i++){try{const im=w.getBLPImageData(blp,i);if(!im.width||!im.height)break;mipmaps++;}catch(e){if(i===0)throw e;break;}}
 report[p]={width:blp.width,height:blp.height,mipmaps};
}
fs.writeFileSync(path.join(R,'asset-validation.json'),JSON.stringify(report,null,2));console.log('All generated model frames, face indices, extents, and imported textures validated.');

const fs=require('fs'),path=require('path'),w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const R=__dirname,b=fs.readFileSync(path.join(R,'src/Units/Stalker/Stalker.mdx')),m=w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));
const r=new w.ModelRenderer(m);r.setFrame(6400);r.update(0);
const transform=(v,mat)=>[mat[0]*v[0]+mat[4]*v[1]+mat[8]*v[2]+mat[12],mat[1]*v[0]+mat[5]*v[1]+mat[9]*v[2]+mat[13],mat[2]*v[0]+mat[6]*v[1]+mat[10]*v[2]+mat[14]];
const meshes=m.Geosets.map((g,i)=>{
 const positions=[];
 for(let j=0;j<g.Vertices.length;j+=3){const ids=g.Groups[g.VertexGroup[j/3]],p=[0,0,0];for(const id of ids){const t=transform(g.Vertices.slice(j,j+3),r.rendererData.nodes[id].matrix);for(let k=0;k<3;k++)p[k]+=t[k]/ids.length;}positions.push(...p);}
 return {positions,faces:Array.from(g.Faces),uv:Array.from(g.TVertices[0]),alpha:r.rendererData.geosetAlpha[i],layers:m.Materials[g.MaterialID].Layers.map(l=>({texture:l.TextureID,alpha:typeof l.Alpha==='number'?l.Alpha:1,filter:l.FilterMode}))};
});
const texture=fs.readFileSync(path.join(R,'src/Units/Stalker/Stalker.blp'));const im=w.getBLPImageData(w.decodeBLP(texture.buffer.slice(texture.byteOffset,texture.byteOffset+texture.length)),0);fs.writeFileSync(path.join(R,'assets/texture.rgba'),Buffer.from(im.data));
fs.writeFileSync(path.join(R,'assets/preview-mesh.json'),JSON.stringify({meshes,width:im.width,height:im.height,muzzle:transform([12,0,69],r.rendererData.nodes[39].matrix),camera:m.Cameras[0]}));
console.log('Exported animated model frame and decoded texture for offline inspection.');

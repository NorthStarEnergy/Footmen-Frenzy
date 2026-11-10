const fs=require('fs'),path=require('path');
const {parseMDX,generateMDX}=require('../mundo-polish-v45/tools/war3-model/package/dist/war3-model.cjs');
const b=fs.readFileSync(path.join(__dirname,'../mundo-polish-v45/src/war3mapImported/TFCard.mdx'));
const m=parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
m.Info.Name='TF small glowing orb with short wake';m.Geosets=[];m.GeosetAnims=[];
m.Materials[0].Layers[0].FilterMode=3;
let v=[],n=[],uv=[],f=[];
for(let j=0;j<=8;j++)for(let i=0;i<=16;i++){
 const a=i*Math.PI/8,t=j*Math.PI/8,x=Math.sin(t)*Math.cos(a),y=Math.sin(t)*Math.sin(a),z=Math.cos(t);
 v.push(x*12,y*12,z*12);n.push(x,y,z);uv.push(.5,.5);
 if(j<8&&i<16){let k=j*17+i;f.push(k,k+17,k+1,k+1,k+17,k+18);}
}
const ext={MinimumExtent:new Float32Array([-32,-32,-32]),MaximumExtent:new Float32Array([32,32,32]),BoundsRadius:56};
m.Geosets.push({Vertices:new Float32Array(v),Normals:new Float32Array(n),TVertices:[new Float32Array(uv)],VertexGroup:new Uint8Array(v.length/3),Faces:new Uint16Array(f),Groups:[[0]],TotalGroupsCount:1,...ext,Anims:[ext],MaterialID:0,SelectionGroup:0,Unselectable:true});
m.GeosetAnims.push({GeosetId:0,Alpha:1,Color:new Float32Array([1,1,1]),Flags:2});
// Soft billboard halo uses Warcraft's radial glow; unit tint colors the mesh.
m.Textures.push({Image:'Textures\\GenericGlowX.blp',ReplaceableId:0,Flags:0});
m.Materials.push({PriorityPlane:0,RenderMode:0,Layers:[{FilterMode:3,Shading:17,TextureID:1,TVertexAnimId:null,CoordId:0,Alpha:.7}]});
const halo={Name:'Halo',ObjectId:1,Parent:0,PivotPoint:new Float32Array([0,0,0]),Flags:264,GeosetId:1,GeosetAnimId:1};
m.Bones.push(halo);m.Nodes.push(halo);m.PivotPoints.push(halo.PivotPoint);
m.Geosets.push({Vertices:new Float32Array([0,-28,-28,0,28,-28,0,28,28,0,-28,28]),Normals:new Float32Array([1,0,0,1,0,0,1,0,0,1,0,0]),TVertices:[new Float32Array([0,0,1,0,1,1,0,1])],VertexGroup:new Uint8Array(4),Faces:new Uint16Array([0,1,2,0,2,3]),Groups:[[1]],TotalGroupsCount:1,...ext,Anims:[ext],MaterialID:1,SelectionGroup:0,Unselectable:true});
m.GeosetAnims.push({GeosetId:1,Alpha:1,Color:new Float32Array([1,1,1]),Flags:2});
const trail={Name:'Short wake',ObjectId:2,Parent:0,PivotPoint:new Float32Array([0,0,0]),Flags:16384,HeightAbove:3,HeightBelow:3,Alpha:.25,Color:new Float32Array([1,1,1]),LifeSpan:.09,TextureSlot:0,EmissionRate:40,Rows:1,Columns:1,MaterialID:1,Gravity:0};
m.RibbonEmitters=[trail];m.Nodes.push(trail);m.PivotPoints.push(trail.PivotPoint);
const out=generateMDX(m),r=parseMDX(out);
if(r.Geosets.length!==2||r.RibbonEmitters.length!==1||Math.abs(r.RibbonEmitters[0].LifeSpan-.09)>.001)throw Error('Orb validation failed');
fs.writeFileSync(path.join(__dirname,'src/war3mapImported/TFOrb.mdx'),Buffer.from(out));
console.log('Small orb + halo + 0.09s trail: MDX roundtrip passed.');

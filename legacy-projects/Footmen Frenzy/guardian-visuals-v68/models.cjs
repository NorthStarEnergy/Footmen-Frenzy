const fs=require('fs'),path=require('path');
const {generateMDX,parseMDX,generateMDL}=require('../mundo-polish-v45/tools/war3-model/package/dist/war3-model.cjs');
const F=x=>new Float32Array(x),U=x=>new Uint32Array(x),R=__dirname;
const read=p=>{const b=fs.readFileSync(p);return parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
function mesh(m,v,f,color,mat=0,alpha=1){
 const id=m.Geosets.length,n=v.length/3;
 m.Geosets.push({Vertices:F(v),Normals:F(Array.from({length:n},()=>[0,0,1]).flat()),TVertices:[F(Array(n*2).fill(.5))],VertexGroup:new Uint8Array(n),Faces:new Uint16Array(f),Groups:[[0]],TotalGroupsCount:1,MinimumExtent:m.Info.MinimumExtent,MaximumExtent:m.Info.MaximumExtent,BoundsRadius:m.Info.BoundsRadius,Anims:m.Sequences.map(()=>({MinimumExtent:m.Info.MinimumExtent,MaximumExtent:m.Info.MaximumExtent,BoundsRadius:m.Info.BoundsRadius})),MaterialID:mat,SelectionGroup:0,Unselectable:true});
 m.GeosetAnims.push({GeosetId:id,Alpha:alpha,Color:F(color),Flags:2});
}
let dome=read(path.join(R,'base/war3mapImported/HiveForceShield.mdx'));
dome.Info.Name='Guardian faint pentagonal shield';
for(const mat of dome.Materials)for(const l of mat.Layers)if(typeof l.Alpha==='number')l.Alpha*=.5;
const tid=dome.Textures.length;dome.Textures.push({Image:'war3mapImported\\TFWhite.blp',Flags:0,ReplaceableId:0});
const mid=dome.Materials.length;dome.Materials.push({PriorityPlane:0,RenderMode:0,Layers:[{FilterMode:2,Shading:145,TextureID:tid,TVertexAnimId:null,CoordId:0,Alpha:.18}]});
// Sparse five-sided outlines projected onto the existing spherical dome.
let v=[],f=[],pentagons=[];
const norm=a=>{const n=Math.hypot(...a);return a.map(x=>x/n);};
for(const [theta,count,rad] of [[0,1,.19],[.48,6,.18],[.94,10,.19],[1.35,13,.16]]){
 for(let k=0;k<count;k++){
  const phi=2*Math.PI*k/count+(theta>.9?.16:0),n=[Math.sin(theta)*Math.cos(phi),Math.sin(theta)*Math.sin(phi),Math.cos(theta)],u=[Math.cos(theta)*Math.cos(phi),Math.cos(theta)*Math.sin(phi),-Math.sin(theta)],w=[-Math.sin(phi),Math.cos(phi),0],pts=[];
  for(let j=0;j<5;j++){const a=2*Math.PI*j/5+Math.PI/2;pts.push(norm(n.map((x,i)=>x+rad*(Math.cos(a)*u[i]+Math.sin(a)*w[i]))));}
  pentagons.push(pts.map(p=>p.map((x,i)=>x*473+(i===2?-39:0))));
  for(let j=0;j<5;j++){
   const a=pts[j],b=pts[(j+1)%5];
   for(let s=0;s<5;s++){
    const p=norm(a.map((x,i)=>x+(b[i]-x)*s/5)),q=norm(a.map((x,i)=>x+(b[i]-x)*(s+1)/5)),d=q.map((x,i)=>x-p[i]);
    const side=norm([p[1]*d[2]-p[2]*d[1],p[2]*d[0]-p[0]*d[2],p[0]*d[1]-p[1]*d[0]]);const at=v.length/3;
    for(const [pt,sgn] of [[p,-1],[p,1],[q,1],[q,-1]])v.push(...pt.map((x,i)=>473*x+side[i]*sgn*1.15+(i===2?-39:0)));
    f.push(at,at+1,at+2,at,at+2,at+3);
   }
  }
 }
}
mesh(dome,v,f,[.45,.8,1],mid);
const ext={MinimumExtent:F([-70,-70,0]),MaximumExtent:F([70,70,190]),BoundsRadius:210};
const bone={Name:'Root',ObjectId:0,Parent:null,PivotPoint:F([0,0,0]),Flags:256,GeosetId:null,GeosetAnimId:null};
let pylon={Version:800,Info:{Name:'Guardian Psionic Pylon',...ext,BlendTime:150},Sequences:[{Name:'Stand',Interval:U([0,1000]),NonLooping:false,...ext,MoveSpeed:0,Rarity:0}],Textures:[{Image:'war3mapImported\\TFWhite.blp',Flags:0,ReplaceableId:0}],Materials:[{PriorityPlane:0,RenderMode:0,Layers:[{FilterMode:0,Shading:17,TextureID:0,TVertexAnimId:null,CoordId:0,Alpha:1}]}],Geosets:[],GeosetAnims:[],Bones:[bone],Nodes:[bone],PivotPoints:[F([0,0,0])],Helpers:[],Attachments:[],EventObjects:[],CollisionShapes:[],GlobalSequences:[],ParticleEmitters:[],ParticleEmitters2:[],Cameras:[],Lights:[],RibbonEmitters:[],TextureAnims:[]};
// Elongated faceted crystal: blue planes with pale cyan highlights.
for(let j=0;j<6;j++){let a=j*Math.PI/3,b=(j+1)*Math.PI/3,p=[Math.cos(a)*27,Math.sin(a)*27,105],q=[Math.cos(b)*27,Math.sin(b)*27,105];mesh(pylon,[0,0,184,...p,...q,0,0,48],[0,1,2,1,3,2],j%3===0?[.5,.93,1]:j%3===1?[.12,.55,.95]:[.06,.28,.65]);}
function prism(points,width,color){for(let j=0;j<points.length-1;j++){const a=points[j],b=points[j+1];const vs=[];for(const p of [a,b])for(const [x,y] of [[-1,-1],[1,-1],[1,1],[-1,1]])vs.push(p[0]+x*width,p[1]+y*width,p[2]);mesh(pylon,vs,[0,1,5,0,5,4,1,2,6,1,6,5,2,3,7,2,7,6,3,0,4,3,4,7,4,5,6,4,6,7],color);}}
for(let k=0;k<3;k++){let a=k*2*Math.PI/3;const point=(r,z)=>[r*Math.cos(a),r*Math.sin(a),z];prism([point(32,5),point(53,23),point(48,65),point(34,110)],6,[.75,.52,.19]);prism([point(48,29),point(43,63)],2,[.3,.8,1]);}
for(const [name,m] of [['GuardianPentagonDome',dome],['GuardianPylon',pylon]]){
 const bytes=generateMDX(m),parsed=parseMDX(bytes);if(parsed.Geosets.length!==m.Geosets.length)throw Error('Roundtrip failed');
 for(const g of parsed.Geosets){if([...g.Faces].some(i=>i>=g.Vertices.length/3))throw Error('Invalid face');}
 fs.writeFileSync(path.join(R,'src',name+'.mdx'),Buffer.from(bytes));fs.writeFileSync(path.join(R,name+'.mdl'),generateMDL(parsed));
 console.log(name,bytes.byteLength,'bytes; geosets',m.Geosets.length);
}
fs.writeFileSync(path.join(R,'geometry-preview.json'),JSON.stringify({pentagons,pylon:pylon.Geosets.map((g,i)=>({v:Array.from(g.Vertices),f:Array.from(g.Faces),color:Array.from(pylon.GeosetAnims[i].Color)}))}));

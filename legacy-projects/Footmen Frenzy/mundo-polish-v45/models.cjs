const fs=require('fs'),path=require('path');
const {generateMDX,parseMDX,generateMDL}=require('./tools/war3-model/package/dist/war3-model.cjs');
const F=x=>new Float32Array(x), U=x=>new Uint32Array(x);
function model(name,r){
 const ext={MinimumExtent:F([-r,-r,-r]),MaximumExtent:F([r,r,r]),BoundsRadius:r*1.733};
 const bone={Name:'Root',ObjectId:0,Parent:null,PivotPoint:F([0,0,0]),Flags:256,GeosetId:null,GeosetAnimId:null};
 return {Version:800,Info:{Name:name,...ext,BlendTime:150},Sequences:[{Name:'Stand',Interval:U([0,1000]),NonLooping:false,...ext,MoveSpeed:0,Rarity:0}],Textures:[{Image:'war3mapImported\\TFWhite.blp',Flags:0,ReplaceableId:0}],Materials:[{PriorityPlane:0,RenderMode:0,Layers:[{FilterMode:0,Shading:17,TextureID:0,TVertexAnimId:null,CoordId:0,Alpha:1}]}],Geosets:[],GeosetAnims:[],Bones:[bone],Nodes:[bone],PivotPoints:[F([0,0,0])],Helpers:[],Attachments:[],EventObjects:[],CollisionShapes:[],GlobalSequences:[],ParticleEmitters:[],ParticleEmitters2:[],Cameras:[],Lights:[],RibbonEmitters:[],TextureAnims:[]};
}
function mesh(m,verts,faces,color){
 const id=m.Geosets.length, n=verts.length/3;
 m.Geosets.push({Vertices:F(verts),Normals:F(Array.from({length:n},()=>[0,0,1]).flat()),TVertices:[F(Array(n*2).fill(.5))],VertexGroup:new Uint8Array(n),Faces:new Uint16Array(faces),Groups:[[0]],TotalGroupsCount:1,MinimumExtent:m.Info.MinimumExtent,MaximumExtent:m.Info.MaximumExtent,BoundsRadius:m.Info.BoundsRadius,Anims:[{MinimumExtent:m.Info.MinimumExtent,MaximumExtent:m.Info.MaximumExtent,BoundsRadius:m.Info.BoundsRadius}],MaterialID:0,SelectionGroup:0,Unselectable:true});
 m.GeosetAnims.push({GeosetId:id,Alpha:1,Color:F(color),Flags:2});
}
function quad(m,x,y,w,h,z,c){mesh(m,[x-w,y-h,z,x+w,y-h,z,x+w,y+h,z,x-w,y+h,z],[0,1,2,0,2,3],c);}
let card=model('Twisted Fate - small playing card',40);
quad(card,0,0,28,18,0,[.95,.95,.95]);quad(card,0,0,24,14,.3,[.12,.12,.16]);quad(card,0,0,22,12,.6,[.95,.95,.95]);
mesh(card,[-13,0,1,0,-9,1,13,0,1,0,9,1],[0,1,2,0,2,3],[.1,.1,.14]);
quad(card,-19,8,2,2,1,[.1,.1,.14]);quad(card,19,-8,2,2,1,[.1,.1,.14]);
let gate=model('Twisted Fate - swirling card gateway',140);
gate.Materials[0].Layers[0].FilterMode=3;
function arc(r,w,start,end,c){let v=[],f=[];for(let i=0;i<=48;i++){let a=start+(end-start)*i/48;v.push(Math.cos(a)*(r-w),Math.sin(a)*(r-w),3,Math.cos(a)*(r+w),Math.sin(a)*(r+w),3);if(i<48){let j=i*2;f.push(j,j+1,j+3,j,j+3,j+2);}}mesh(gate,v,f,c);}
arc(110,2,0,Math.PI*2,[1,.7,.18]);arc(93,1.5,0,Math.PI*2,[.65,.3,1]);
for(let k=0;k<3;k++){let a=k*Math.PI*2/3;arc(75,3,a,a+1.5,[1,.8,.3]);arc(52,2,-a,-a+1.5,[.6,.25,1]);}
for(let k=0;k<12;k++){let a=k*Math.PI/6;quad(gate,Math.cos(a)*125,Math.sin(a)*125,4,7,3,[1,.8,.4]);}
for(let [name,m] of [['TFCard',card],['TFGateway',gate]]){
 const bytes=generateMDX(m),parsed=parseMDX(bytes);
 if(parsed.Version!==800||parsed.Geosets.length!==m.Geosets.length)throw Error('Model roundtrip failed');
 fs.writeFileSync(path.join(__dirname,'src/war3mapImported',name+'.mdx'),Buffer.from(bytes));
 fs.writeFileSync(path.join(__dirname,'assets',name+'.mdl'),generateMDL(parsed));
 console.log(name,bytes.byteLength,'bytes',parsed.Geosets.length,'geosets, MDX roundtrip passed');
}


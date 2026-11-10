// Flat, self-contained command glyphs. Runtime controls their motion and fading.
const fs=require('fs'),path=require('path'),w=require('./tools/model-tools/node_modules/war3-model');
const root=__dirname,out=path.join(root,'src/Spells/Orianna/Feedback');
const parse=p=>{const b=fs.readFileSync(p);return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
const specs=[['MoveGround',[85,210,155]],['AttackGround',[255,125,65]],['ProtectGround',[70,200,235]],['ShockGround',[185,110,240]]];
const previews=[];
for(const [kind,color] of specs){
  const vertices=[],faces=[],normals=[],uv=[];
  function line(points,width){for(let i=1;i<points.length;i++){
    const a=points[i-1],b=points[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]);if(!d)continue;
    const nx=-(b[1]-a[1])/d*width/2,ny=(b[0]-a[0])/d*width/2,k=vertices.length/3;
    for(const p of [[a[0]+nx,a[1]+ny],[a[0]-nx,a[1]-ny],[b[0]-nx,b[1]-ny],[b[0]+nx,b[1]+ny]]){vertices.push(...p,0);normals.push(0,0,1);uv.push(.5,.5);}
    faces.push(k,k+1,k+2,k,k+2,k+3);
  }}
  const polar=(r,a)=>[r*Math.cos(a),r*Math.sin(a)];
  if(kind==='MoveGround'){
    for(const x of [-.15,.45])line([[x-.3,-.32],[x,0],[x-.3,.32]],.07);
    line([[-.9,-.13],[-.45,-.13]],.035);line([[-.9,.13],[-.45,.13]],.035);
  }else if(kind==='AttackGround'){
    for(let j=0;j<12;j++){const a=j*Math.PI/6;
      line([polar(.18,a),polar(.38,a+.11),polar(.55,a-.07),polar(.88,a)],.025);
      line([polar(.73,a-.09),polar(.88,a),polar(.73,a+.09)],.035);
    }
  }else if(kind==='ProtectGround'){
    line([[0,-.32],[.27,0],[0,.32],[-.27,0],[0,-.32]],.045);
    line([[-.13,0],[.13,0]],.05);line([[0,-.13],[0,.13]],.05);
    for(let j=0;j<4;j++){
      const a=j*Math.PI/2;
      line([polar(.4,a-.25),polar(.67,a-.31),polar(.86,a),polar(.67,a+.31),polar(.4,a+.25)],.045);
      line([polar(.48,a-.6),polar(.61,a-.6)],.06);
    }
  }else{
    for(let j=0;j<3;j++){
      const p=[];for(let k=0;k<=36;k++){const t=k/36;p.push(polar(.91-.79*t,j*2*Math.PI/3+3.8*t));}line(p,.035);
      const p0=p.at(-2),end=p.at(-1),a=Math.atan2(end[1]-p0[1],end[0]-p0[0]);
      line([[end[0]-.12*Math.cos(a-.6),end[1]-.12*Math.sin(a-.6)],end,[end[0]-.12*Math.cos(a+.6),end[1]-.12*Math.sin(a+.6)]],.04);
    }
  }
  const m=parse(path.join(root,'assets/Spells/Orianna/Feedback/AttackRing.mdx'));
  const bounds={BoundsRadius:1.5,MinimumExtent:new Float32Array([-1,-1,-.01]),MaximumExtent:new Float32Array([1,1,.01])};
  Object.assign(m.Info,bounds,{Name:'Orianna '+kind});
  Object.assign(m.Sequences[0],bounds,{Interval:new Uint32Array([0,1000]),NonLooping:false});
  Object.assign(m.Geosets[0],bounds,{Vertices:new Float32Array(vertices),Normals:new Float32Array(normals),Faces:new Uint16Array(faces),VertexGroup:new Uint8Array(vertices.length/3),TVertices:[new Float32Array(uv)]});
  m.GeosetAnims[0].Alpha=1;
  Object.assign(m.Materials[0].Layers[0],{FilterMode:2,Shading:17});
  m.Textures[0].Image='Spells\\Orianna\\Feedback\\'+kind+'.blp';
  const palette=Buffer.alloc(1024);palette.set([color[2],color[1],color[0],255]);
  const header=Buffer.alloc(156);header.write('BLP1');[1,8,4,4,5,0].forEach((v,i)=>header.writeUInt32LE(v,4+4*i));
  let offset=1180;const levels=[];
  for(const [i,size] of [4,2,1].entries()){const data=Buffer.concat([Buffer.alloc(size*size),Buffer.alloc(size*size,255)]);header.writeUInt32LE(offset,28+i*4);header.writeUInt32LE(data.length,92+i*4);levels.push(data);offset+=data.length;}
  fs.writeFileSync(path.join(out,kind+'.blp'),Buffer.concat([header,palette,...levels]));
  fs.writeFileSync(path.join(out,kind+'.mdx'),Buffer.from(w.generateMDX(m)));
  const checked=parse(path.join(out,kind+'.mdx'));
  if(checked.Geosets[0].Vertices.length!==vertices.length||checked.Sequences[0].NonLooping||checked.ParticleEmitters2.length)throw Error('Invalid ground glyph '+kind);
  if(vertices.some((v,i)=>i%3!==2&&Math.abs(v)>1))throw Error('Glyph exceeds radius');
  previews.push({kind,color,vertices,faces});
}
fs.writeFileSync(path.join(root,'audit/command-ground.json'),JSON.stringify(previews));
console.log('Four command ground models generated and round-trip validated.');

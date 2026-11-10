const fs=require('fs'),path=require('path');
const w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const R=__dirname,O=path.join(R,'src/Spells/Mundo');fs.mkdirSync(O,{recursive:true});
const original=fs.readFileSync(path.join(R,'assets/PlagueCloudCaster.mdx'));
const parse=b=>w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));
const F=x=>new Float32Array(x);
// RGB stops: light green, darker green, purple/dark-green mixture, near-black.
const stops=[
 {t:0,c:[[145,235,105],[85,195,65],[45,140,40]]},
 {t:.33,c:[[80,165,65],[48,123,46],[30,88,32]]},
 {t:.67,c:[[100,45,115],[35,87,42],[53,27,63]]},
 {t:1,c:[[19,15,23],[12,24,15],[8,10,9]]}
];
const report=[];
for(let i=0;i<=20;i++){
 const t=i/20,m=parse(original);let n=0;while(n<stops.length-2&&t>stops[n+1].t)n++;
 const a=stops[n],b=stops[n+1],p=(t-a.t)/(b.t-a.t);
 const rgb=a.c.map((c,j)=>c.map((v,k)=>v+(b.c[j][k]-v)*p));
 // Author emitter colors, not just instance tint: particles carry their own colors.
 const emitter=m.ParticleEmitters2[0];
 emitter.SegmentColor=rgb.map(c=>F([c[2]/255,c[1]/255,c[0]/255]));
 emitter.FilterMode=0; // alpha blended; additive black would disappear.
 emitter.Alpha=new Uint8Array([Math.round(123+40*t),Math.round(60+30*t),0]);
 m.Version=800;m.Info.Name='Mundo cloud heat '+i;
 const bounds={MinimumExtent:F([-250,-250,-30]),MaximumExtent:F([250,250,300]),BoundsRadius:420};
 Object.assign(m.Info,bounds);for(const s of m.Sequences)Object.assign(s,bounds);
 const data=Buffer.from(w.generateMDX(m)),check=parse(data);
 if(check.ParticleEmitters2[0].FilterMode!==0||check.ParticleEmitters2[0].Alpha[2]!==0)throw Error('Particle blend/cleanup mismatch');
 for(let j=0;j<3;j++)for(let k=0;k<3;k++)if(Math.abs(check.ParticleEmitters2[0].SegmentColor[j][2-k]*255-rgb[j][k])>.001)throw Error('Color roundtrip mismatch');
 fs.writeFileSync(path.join(O,'Cloud'+i+'.mdx'),data);
 report.push({heat:t,damage_multiplier:1+t,rgb:rgb.map(c=>c.map(Math.round)),bytes:data.length});
}
fs.writeFileSync(path.join(R,'asset-checks.json'),JSON.stringify({models:report,roundtrip_passed:true,blend:'alpha',native_texture:parse(original).Textures[0].Image,in_game_visual_check:false},null,2));
console.log('21 cloud models generated and roundtrip checked.');

const fs=require('fs');const {parseMDX,generateMDX}=require('../mundo-polish-v45/tools/war3-model/package/dist/war3-model.cjs');
const b=fs.readFileSync('../tf-orbs-v45c/src/war3mapImported/TFOrb.mdx');const m=parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
m.Info.Name='Twisted Fate radiant orb';let r=m.RibbonEmitters[0];r.LifeSpan=.34;r.HeightAbove=7;r.HeightBelow=7;r.Alpha=.58;r.EmissionRate=50;
const out=generateMDX(m);const check=parseMDX(out);if(Math.abs(check.RibbonEmitters[0].LifeSpan-.34)>.001)throw Error('trail invalid');fs.writeFileSync('src/TFOrb.mdx',Buffer.from(out));console.log('Orb model verified');

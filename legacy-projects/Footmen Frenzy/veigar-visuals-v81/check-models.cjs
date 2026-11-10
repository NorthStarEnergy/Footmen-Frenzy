const fs=require('fs'),path=require('path'),assert=require('assert');
const w=require('../mundo-polish-v45/tools/war3-model/package/dist/war3-model.cjs');
const root=path.join(__dirname,'../Transfer/veigar-refine-v69-work/edited/Spells/Veigar69');
const reports=[];
for(const name of ['BalefulOrb','PrimordialOrb','Meteor','MeteorImpact']) {
 const bytes=fs.readFileSync(path.join(root,name+'.mdx'));
 const model=w.parseMDX(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));
 assert.equal(model.Version,800);
 assert(model.Sequences.some(s=>s.Name===(name==='MeteorImpact'?'Birth':'Stand')));
 assert(model.ParticleEmitters2.length>0);
 for(const e of model.ParticleEmitters2) assert(e.TextureID>=0&&e.TextureID<model.Textures.length);
 for(const t of model.Textures) assert(/^(Textures\\|Abilities\\)/.test(t.Image),'Unexpected custom texture '+t.Image);
 const round=Buffer.from(w.generateMDX(model));
 const parsed=w.parseMDX(round.buffer.slice(round.byteOffset,round.byteOffset+round.byteLength));
 assert.equal(parsed.ParticleEmitters2.length,model.ParticleEmitters2.length);
 reports.push({name,bytes:bytes.length,emitters:model.ParticleEmitters2.length,sequences:model.Sequences.map(s=>s.Name),textures:model.Textures.map(t=>t.Image)});
}
fs.writeFileSync(path.join(__dirname,'model-checks.json'),JSON.stringify({passed:true,models:reports,engine_tested:false},null,2));
console.log('Four models parsed and round-tripped; animation and texture indices valid.');

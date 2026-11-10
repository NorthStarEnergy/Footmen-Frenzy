const fs = require('fs'), path = require('path');
const w = require('./tools/model-tools/node_modules/war3-model');
const root = __dirname;
const textures = JSON.parse(fs.readFileSync(path.join(root, 'assets/orb-textures.json')));
const parse = p => {const b=fs.readFileSync(p);return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));};
const report = [];
for (const name of ['OrbLightningX.mdx', 'OrbLightX.mdx']) {
  const model = parse(path.join(root, '../mini-foots/base/files/war3mapImported', name));
  const intervals = model.Sequences.filter(s => /Stand|Portrait/.test(s.Name)).map(s => Array.from(s.Interval));
  const fill = (track, dimensions) => {
    if (!track || typeof track === 'number' || track.GlobalSeqId != null) return;
    for (const interval of intervals) for (const frame of interval) {
      if (track.Keys.some(k => k.Frame === frame)) throw Error('Unexpected existing idle key');
      const key = {Frame:frame, Vector:new Float32Array(dimensions).fill(1)};
      if (track.LineType >= 2) {
        key.InTan = new Float32Array(dimensions).fill(track.LineType === 2 ? 0 : 1);
        key.OutTan = new Float32Array(dimensions).fill(track.LineType === 2 ? 0 : 1);
      }
      track.Keys.push(key);
    }
    track.Keys.sort((a,b)=>a.Frame-b.Frame);
  };
  for (const geoset of model.GeosetAnims) fill(geoset.Alpha, 1);
  for (const particle of model.ParticleEmitters2) fill(particle.Visibility, 1);
  for (const node of [...model.Bones,...model.Helpers]) fill(node.Scaling, 3);
  for (const texture of model.Textures) texture.Image = textures[texture.Image];
  // The old model-wide bounding radius was zero despite a roughly 180-unit mesh.
  model.Info.BoundsRadius = 200;
  const destination = path.join(root, 'src/war3mapImported', name);
  fs.mkdirSync(path.dirname(destination), {recursive:true});
  fs.writeFileSync(destination, Buffer.from(w.generateMDX(model)));
  const checked = parse(destination);
  for (const geoset of checked.GeosetAnims) for (const interval of intervals) for (const frame of interval) {
    if (geoset.Alpha.Keys.find(k=>k.Frame===frame)?.Vector[0] !== 1) throw Error('Invisible idle geoset');
  }
  report.push({name, idleIntervals:intervals, textures:checked.Textures.map(t=>t.Image), boundsRadius:checked.Info.BoundsRadius});
}
const ring = parse(path.join(root, 'assets/Spells/Orianna/Feedback/AttackRing.mdx'));
ring.Textures[0].Image = 'Spells\\Orianna\\Feedback\\ProtectRingColor.blp';
fs.writeFileSync(path.join(root, 'src/Spells/Orianna/Feedback/ProtectRing.mdx'), Buffer.from(w.generateMDX(ring)));
fs.writeFileSync(path.join(root,'audit/orb-models.json'), JSON.stringify(report,null,2));
console.log('Both orb models repaired and round-trip parsed; Protect ring generated.');

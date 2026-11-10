const fs = require('fs'), path = require('path');
const w = require('../799x-backport/tools/model-tools/node_modules/war3-model');
const root = __dirname;
const expected = JSON.parse(fs.readFileSync(path.join(root, 'asset-checks.json')));
let maxStep = 0;
const models = [];
for (let i = 0; i <= 20; i++) {
  const bytes = fs.readFileSync(path.join(root, 'models', `Cloud${i}.mdx`));
  const m = w.parseMDX(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.length));
  if (m.Version !== 800 || m.ParticleEmitters2.length !== 1) throw Error(`Invalid emitter in ${i}`);
  const e = m.ParticleEmitters2[0];
  if (e.FilterMode !== 0 || e.Alpha[2] !== 0) throw Error(`Bad blend or fade in ${i}`);
  const colors = e.SegmentColor.map(c => Array.from(c).reverse().map(v => Math.round(v * 255)));
  if (JSON.stringify(colors) !== JSON.stringify(expected.models[i].rgb)) throw Error(`Incorrect RGB in ${i}`);
  if (i) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++)
    maxStep = Math.max(maxStep, Math.abs(colors[j][k] - models[i-1].colors[j][k]));
  models.push({ colors, alpha: Array.from(e.Alpha), texture: m.Textures[0].Image });
}
if (maxStep > 35) throw Error(`Abrupt adjacent color step ${maxStep}`);
if (!models.every(m => m.texture === expected.native_texture)) throw Error('Texture reference differs');
fs.writeFileSync(path.join(root, 'model-checks.json'), JSON.stringify({ models: models.length, max_rgb_step: maxStep, texture: models[0].texture, imported_from_actual_base: true, in_game_visual_check: false }, null, 2));
console.log(`21 imported particle models parsed; maximum adjacent RGB channel change ${maxStep}; alpha blend and fade verified.`);

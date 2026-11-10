const fs=require('fs'),path=require('path');
const w=require('../799x-backport/tools/model-tools/node_modules/war3-model');
const R=__dirname,O=path.join(R,'src/Units/Stalker');fs.mkdirSync(O,{recursive:true});
const F=x=>new Float32Array(x),U=x=>new Uint32Array(x);
function load(p){const b=fs.readFileSync(p);return w.parseMDX(b.buffer.slice(b.byteOffset,b.byteOffset+b.length));}
let m=load(path.join(R,'assets/original/Stalker/Stalker_Test.mdx'));
const oldSequences=m.Sequences,keep=oldSequences.map((s,i)=>i).filter(i=>oldSequences[i].Name!=='Spell');
const bounds=death=>({MinimumExtent:F(death?[-350,-350,-120]:[-110,-110,-10]),MaximumExtent:F(death?[350,350,600]:[110,110,130]),BoundsRadius:death?800:210});
let invalidBounds=0;
for(const g of m.Geosets)for(const a of g.Anims)if([...a.MinimumExtent,...a.MaximumExtent].some(n=>Math.abs(n)>1e20))invalidBounds++;
m.Sequences=keep.map(i=>({...oldSequences[i],...bounds(oldSequences[i].Name.startsWith('Death'))}));
Object.assign(m.Info,bounds(true));
for(const g of m.Geosets){g.Anims=keep.map(i=>bounds(oldSequences[i].Name.startsWith('Death')));}
m.Textures[0].Image='Units\\Stalker\\Stalker.blp';
// This 2010 path is absent from the installed game; use its smoke atlas.
m.Textures.find(t=>t.Image==='Textures\\Clouds8x8.blp').Image='Textures\\Clouds8x8Grey.blp';
const attachments=[['origin',[0,0,0],null],['chest',[0,0,48],39],['weapon',[12,0,69],39],['overhead',[0,0,112],39]];
for(let i=0;i<attachments.length;i++){
 const [Name,p,Parent]=attachments[i],ObjectId=m.PivotPoints.length;
 const a={Name, ObjectId,Parent,Flags:0,PivotPoint:F(p),Path:'',AttachmentID:i};
 m.Attachments.push(a);m.Nodes[ObjectId]=a;m.PivotPoints.push(F(p));
}
// Keep mouse picking close to the body rather than the broad death bounds.
const pick={Name:'Body Selection',ObjectId:m.PivotPoints.length,Parent:39,Flags:8192,PivotPoint:F([0,0,0]),Shape:2,Vertices:F([0,0,48]),BoundsRadius:48};
m.CollisionShapes.push(pick);m.Nodes[pick.ObjectId]=pick;m.PivotPoints.push(F([0,0,0]));
function save(name,model){const b=Buffer.from(w.generateMDX(model));fs.writeFileSync(path.join(O,name+'.mdx'),b);const check=load(path.join(O,name+'.mdx'));fs.writeFileSync(path.join(R,'assets',name+'.mdl'),w.generateMDL(check));return check;}
let fixed=save('Stalker',m);
if(fixed.Attachments.length!==4||fixed.Sequences.some(s=>s.Name==='Spell')||fixed.Textures[0].Image!=='Units\\Stalker\\Stalker.blp')throw Error('Stalker patch roundtrip failed');
fs.copyFileSync(path.join(R,'assets/original/Stalker/Stalker.blp'),path.join(O,'Stalker.blp'));
// Reuse the project's authored additive flare topology for a blue plasma bolt.
let bolt=load(path.join(R,'../lux-final-spark/src/Spells/Lux/FinalSparkFlare.mdx'));
bolt.Info.Name='Stalker particle disruptor';
Object.assign(bolt.Info,{MinimumExtent:F([-45,-14,-14]),MaximumExtent:F([25,14,14]),BoundsRadius:60});
for(const g of bolt.Geosets){for(let i=0;i<g.Vertices.length;i+=3){g.Vertices[i]*=64;g.Vertices[i+1]*=22;g.Vertices[i+2]*=22;}Object.assign(g,{MinimumExtent:F([-45,-14,-14]),MaximumExtent:F([25,14,14]),BoundsRadius:60});g.Anims=bolt.Sequences.map(()=>({MinimumExtent:F([-45,-14,-14]),MaximumExtent:F([25,14,14]),BoundsRadius:60}));}
bolt.Textures[0].Image='Units\\Stalker\\Plasma.blp';
for(const s of bolt.Sequences)Object.assign(s,{MinimumExtent:F([-45,-14,-14]),MaximumExtent:F([25,14,14]),BoundsRadius:60});
bolt.GeosetAnims[0].Color=F([1.0,0.42,0.25]); // MDX stores BGR.
save('Disruptor',bolt);
fs.copyFileSync(path.join(R,'../lux-final-spark/src/Spells/Lux/FinalSparkFlare.blp'),path.join(O,'Plasma.blp'));
const blp=fs.readFileSync(path.join(O,'Stalker.blp')),decoded=w.decodeBLP(blp.buffer.slice(blp.byteOffset,blp.byteOffset+blp.length));
const image=w.getBLPImageData(decoded,0);
const report={format:fixed.Version,invalid_animation_bounds_repaired:invalidBounds,removed_sequence:'Spell',sequences:fixed.Sequences.map(s=>s.Name),attachments:fixed.Attachments.map(a=>({name:a.Name,parent:a.Parent,pivot:Array.from(a.PivotPoint)})),muzzle_model_coordinates:[12,0,69],model_scale:1,missile_launch_fields:{ulpx:0,ulpy:12,ulpz:69},portrait:fixed.Cameras[0].Name,texture_dimensions:[image.width,image.height],custom_texture:'Units\\Stalker\\Stalker.blp',native_texture_dependencies:fixed.Textures.slice(1).filter(t=>t.Image).map(t=>t.Image),team_color:fixed.Textures.some(t=>t.ReplaceableId===1),roundtrip_passed:true};
fs.writeFileSync(path.join(R,'asset-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));

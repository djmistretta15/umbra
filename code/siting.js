// Umbra siting: where would a city go on the Moon and Mars? Coarse 1 degree grids.
// Node, no deps. node siting.js <dataDir> <outJson>
const fs=require('fs'),path=require('path');
const D=process.argv[2],OUT=process.argv[3];
const rd=f=>fs.readFileSync(path.join(D,f));
const R2D=180/Math.PI,D2R=Math.PI/180;

// ---------- MOON ----------
// LOLA LDEM_16: 16 px/deg, int16 LE, height = DN*0.5 m, row 0 = 90N, col 0 = 0E (lon 0..360)
function moon(){
  const b=rd('moon/ldem_16.img'),W=5760,H=2880,P=16;
  const z=new Float32Array(W*H);for(let i=0;i<W*H;i++)z[i]=b.readInt16LE(i*2)*0.5;
  const dy=2*Math.PI*1737400/360/P;
  const slope=new Float32Array(W*H);
  for(let r=1;r<H-1;r++){const lat=90-(r+.5)/P,dx=dy*Math.max(Math.cos(lat*D2R),.02);
    for(let c=0;c<W;c++){const cl=(c+W-1)%W,cr=(c+1)%W;
      const gx=(z[r*W+cr]-z[r*W+cl])/(2*dx),gy=(z[(r+1)*W+c]-z[(r-1)*W+c])/(2*dy);
      slope[r*W+c]=Math.atan(Math.hypot(gx,gy))*R2D}}
  // Lunar Prospector GRS 2 degree equal-area pixels
  const grs=[];for(const l of rd('moon/lpgrs_high1_elem_abundance_2deg.tab').toString().split('\n')){const t=l.trim().split(/\s+/).map(Number);if(t.length<16)continue;
    grs.push({la0:t[1],la1:t[2],lo0:t[3],lo1:t[4],TiO2:t[11]*100,FeO:t[12]*100,Th:t[14]})}
  const grsAt=(la,lo)=>{lo=lo>180?lo-360:lo;for(const g of grs)if(la>=g.la0&&la<g.la1&&lo>=g.lo0&&lo<g.lo1)return g;return null};
  // LROC skylights (pits into lava tubes or voids), approx centres
  const pits=[["Marius Hills pit",14.1,-56.8],["Mare Tranquillitatis pit",8.3,33.2],["Mare Ingenii pit",-35.9,166.1]];
  const cells=[];
  for(let la=-89.5;la<90;la++)for(let lo=0.5;lo<360;lo++){
    const r0=Math.round((90-la-.5)*P),c0=Math.round((lo-.5)*P);
    let flat=0,n=0,smean=0,run=0,best=0;
    for(let r=r0;r<r0+P;r++){run=0;for(let c=c0;c<c0+P*6;c++){ // look 6 deg east so long tracks are not cut at cell edges
        const s=slope[r*W+(c%W)];if(c<c0+P){n++;smean+=s;if(s<3)flat++}
        if(s<1)run++;else{best=Math.max(best,run);run=0}}best=Math.max(best,run)}
    const kmpx=dy*Math.cos(la*D2R)/1000,track=best*kmpx;
    const g=grsAt(la,lo),L=lo>180?lo-360:lo;
    const nearSide=Math.abs(L)<=82; // Earth always above the horizon (libration margin)
    const pit=pits.find(p=>Math.hypot(p[1]-la,(p[2]-L)*Math.cos(la*D2R))<3);
    cells.push({lat:la,lon:+L.toFixed(1),flat:flat/n,slope:smean/n,track_km:+track.toFixed(0),TiO2:g?+g.TiO2.toFixed(2):null,FeO:g?+g.FeO.toFixed(1):null,Th:g?+g.Th.toFixed(1):null,near:nearSide,pit:pit?pit[0]:null})}
  // function scores 0..1
  const q=(arr,p)=>{const a=arr.filter(x=>x!=null).sort((x,y)=>x-y);return a[Math.floor(p*(a.length-1))]};
  const ti90=q(cells.map(c=>c.TiO2),.9),fe90=q(cells.map(c=>c.FeO),.9),th90=q(cells.map(c=>c.Th),.9);
  for(const c of cells){
    const f={};
    f.landing=c.flat>=.8; // harbor: most of the cell is gentle enough to land and build pads
    f.massdriver=c.track_km>=50&&Math.abs(c.lat)<=25; // a straight east-running flat strip, low latitude so launches reach low-inclination orbit
    f.ilmenite=c.TiO2!=null&&c.TiO2>=ti90; // oxygen and metal from ilmenite
    f.iron=c.FeO!=null&&c.FeO>=fe90;
    f.kreep=c.Th!=null&&c.Th>=th90; // thorium, rare-earth rich KREEP
    f.comms=c.near;
    f.shelter=!!c.pit;
    c.f=Object.keys(f).filter(k=>f[k])}
  // hub = functions available within ~150 km (neighbouring 1 deg cells at low latitude)
  const idx=(la,lo)=>{const r=Math.floor(89.5-la),cc=((Math.floor(lo+.5-.5)+360)%360);return r*360+cc};
  const get=(la,lo)=>{if(la<-89.5||la>89.5)return null;let L=lo;if(L<0)L+=360;return cells[(Math.round(la+89.5))*360+Math.floor(L)]};
  for(const c of cells){const s=new Set();for(let a=-2;a<=2;a++)for(let b=-2;b<=2;b++){const o=get(c.lat+a,c.lon+b/Math.max(Math.cos(c.lat*D2R),.2));if(o)o.f.forEach(x=>s.add(x))}
    c.hub=[...s];c.hubN=s.size}
  return {cells,thresholds:{TiO2_p90:ti90,FeO_p90:fe90,Th_p90:th90}}
}

// ---------- MOON SOUTH POLE (LOLA 60 m sunlight and shadow, if downloaded) ----------
function pole(){
  const fA=path.join(D,'moon/AVGVISIB_85S_060M_201608.IMG'),fP=path.join(D,'moon/LPSR_85S_060M_201608.IMG');
  if(!fs.existsSync(fA)||!fs.existsSync(fP))return null;
  const lbl=fs.readFileSync(fA.replace(/IMG$/,'LBL'),'utf8');
  const g=k=>{const m=lbl.match(new RegExp(k+'\\s*=\\s*"?([-\\d.E+]+)'));return m?+m[1]:null};
  return {lines:g('LINES'),samples:g('LINE_SAMPLES'),bits:g('SAMPLE_BITS'),scale:g('MAP_SCALE'),note:'parsed later'}
}

// ---------- MARS ----------
function mars(){
  // MOLA MEGDR 16 px/deg, int16 BE, metres, row 0 = 90N, col 0 = 0E
  const b=rd('mars/megt90n000eb.img'),W=5760,H=2880,P=16;
  const z=new Float32Array(W*H);for(let i=0;i<W*H;i++)z[i]=b.readInt16BE(i*2);
  const dy=2*Math.PI*3396190/360/P;
  // TES night thermal inertia 20 px/deg int16 BE
  const t=rd('mars/global_ti_night_2007.img'),TW=7200;
  // Odyssey GRS water-equivalent hydrogen, 5 deg
  const wat={};for(const l of rd('mars/h2o_sr_5x5.tab').toString().split('\n')){const a=l.trim().split(/\s+/).map(Number);if(a.length<3||a[2]>9000)continue;wat[a[0]+','+a[1]]=a[2]}
  const watAt=(la,lo)=>{const L=((lo%360)+360)%360;return wat[(Math.floor(la/5)*5+2.5)+','+(Math.floor(L/5)*5+2.5)]??null};
  const cells=[];
  for(let la=-89.5;la<90;la++)for(let lo=0.5;lo<360;lo++){
    const r0=Math.round((90-la-.5)*P),c0=Math.round((lo-.5)*P),dx=dy*Math.max(Math.cos(la*D2R),.02);
    let n=0,el=0,flat=0,tis=[];
    for(let r=r0;r<r0+P;r++)for(let c=c0;c<c0+P;c++){const i=r*W+c;el+=z[i];n++;
      if(r>0&&r<H-1){const gx=(z[r*W+(c+1)%W]-z[r*W+(c+W-1)%W])/(2*dx),gy=(z[i+W]-z[i-W])/(2*dy);if(Math.atan(Math.hypot(gx,gy))*R2D<2)flat++}}
    for(let r=Math.round((90-la-.5)*20);r<Math.round((90-la+.5)*20);r++)for(let c=Math.round((lo-.5)*20);c<Math.round((lo+.5)*20);c++){const v=t.readInt16BE((r*TW+c)*2);if(v>0&&v<3000)tis.push(v)}
    tis.sort((a,b)=>a-b);const ti=tis.length?tis[tis.length>>1]:null;
    const L=lo>180?lo-360:lo;
    cells.push({lat:la,lon:L,elev_km:+(el/n/1000).toFixed(2),flat:+(flat/n).toFixed(2),TI:ti,water:watAt(la,lo)})}
  const w=cells.map(c=>c.water).filter(x=>x!=null).sort((a,b)=>a-b),w80=w[Math.floor(.8*(w.length-1))];
  for(const c of cells){const f={};
    f.landing=c.elev_km<=-1&&c.flat>=.7; // harbor: low ground gives a parachute more air; flat for touchdown
    f.firm=c.TI!=null&&c.TI>=150; // not deep dust
    f.water=c.water!=null&&c.water>=w80; // Odyssey GRS top 20% of hydrogen (ice and hydrated minerals)
    f.sun=Math.abs(c.lat)<=30; // year-round solar power
    f.launch=c.flat>=.7; // flat apron for pads a few km from the habitat
    c.f=Object.keys(f).filter(k=>f[k])}
  const get=(la,lo)=>{if(la<-89.5||la>89.5)return null;let L=lo;if(L<0)L+=360;L=((L%360)+360)%360;return cells[(Math.round(la+89.5))*360+Math.floor(L)]};
  for(const c of cells){const s=new Set();for(let a=-2;a<=2;a++)for(let b=-2;b<=2;b++){const o=get(c.lat+a,c.lon+b/Math.max(Math.cos(c.lat*D2R),.2));if(o)o.f.forEach(x=>s.add(x))}
    c.hub=[...s];c.hubN=s.size}
  return {cells,thresholds:{water_p80:w80}}
}

const M=moon(),Ma=mars(),Po=pole();
// cluster the best cells into named hubs (greedy, 8 deg apart)
function top(cells,need,k,sep,rank){const out=[];const cand=cells.filter(need).sort(rank);
  for(const c of cand){if(out.every(o=>Math.hypot(o.lat-c.lat,(o.lon-c.lon)*Math.cos(c.lat*D2R))>sep))out.push(c);if(out.length>=k)break}return out}
const moonHubs=top(M.cells,c=>c.f.includes('landing'),12,8,(a,b)=>b.hubN-a.hubN||b.track_km-a.track_km||(b.TiO2||0)-(a.TiO2||0));
const moonDrivers=top(M.cells,c=>c.f.includes('massdriver'),10,8,(a,b)=>b.track_km-a.track_km);
const marsHubs=top(Ma.cells,c=>c.f.includes('landing'),12,8,(a,b)=>b.hubN-a.hubN||(b.water||0)-(a.water||0));
// validation: places NASA has studied
const moonStudied=[["Apollo 11",0.67,23.47],["Apollo 12",-3.01,-23.42],["Apollo 14",-3.65,-17.47],["Apollo 15",26.13,3.63],["Apollo 16",-8.97,15.5],["Apollo 17",20.19,30.77],["Marius Hills",14.1,-56.8]];
const marsStudied=[["Jezero (Perseverance)",18.4,77.5],["Gale (Curiosity)",-5.4,137.8],["Meridiani (Opportunity)",-1.9,-5.5],["Arcadia Planitia ice",40,-160],["Deuteronilus Mensae",44,22],["Protonilus Mensae",44,47],["Mawrth Vallis",24,-19]];
const nearestHub=(hubs,la,lo)=>Math.min(...hubs.map(h=>Math.hypot(h.lat-la,(h.lon-lo)*Math.cos(la*D2R))));
const cellAt=(cells,la,lo)=>cells.find(c=>Math.abs(c.lat-la)<=.5&&Math.abs(c.lon-lo)<=.5)||{};
const pct=(cells,v)=>+(100*cells.filter(c=>c.hubN<v).length/cells.length).toFixed(0);
const val=(cells,list)=>list.map(([n,la,lo])=>{const c=cellAt(cells,la,lo);return {name:n,lat:la,lon:lo,hubN:c.hubN,hub:c.hub,beats_pct:pct(cells,c.hubN)}});
const pick=c=>({lat:c.lat,lon:c.lon,hubN:c.hubN,hub:c.hub,here:c.f,...Object.fromEntries(Object.entries(c).filter(([k])=>!['f','hub','hubN','lat','lon'].includes(k)))});
const res={note:'Coarse 1 degree siting. Moon: LRO LOLA LDEM_16 slopes and tracks, Lunar Prospector GRS TiO2/FeO/Th, LROC pits. Mars: MGS MOLA MEGDR, MGS TES night thermal inertia, Mars Odyssey GRS water.',
 moon:{thresholds:M.thresholds,studied:val(M.cells,moonStudied),hubs:moonHubs.map(pick),massDrivers:moonDrivers.map(pick),counts:Object.fromEntries(['landing','massdriver','ilmenite','iron','kreep','comms','shelter'].map(k=>[k,M.cells.filter(c=>c.f.includes(k)).length]))},
 pole:Po,
 mars:{thresholds:Ma.thresholds,hubs:marsHubs.map(pick),studied2:val(Ma.cells,marsStudied),studied:marsStudied.map(([n,la,lo])=>({name:n,lat:la,lon:lo,deg_to_hub:+nearestHub(marsHubs,la,lo).toFixed(1),hubN_here:(Ma.cells.find(c=>Math.abs(c.lat-la)<=.5&&Math.abs(c.lon-lo)<=.5)||{}).hubN})),
   counts:Object.fromEntries(['landing','firm','water','sun','launch'].map(k=>[k,Ma.cells.filter(c=>c.f.includes(k)).length]))}};
fs.writeFileSync(OUT,JSON.stringify(res,null,1));
console.log(JSON.stringify(res.moon.counts),JSON.stringify(res.mars.counts));
for(const h of res.moon.hubs)console.log('MOON',h.lat,h.lon,h.hubN,h.hub.join('+'),'track',h.track_km,'Ti',h.TiO2);
for(const h of res.moon.massDrivers)console.log('DRIVER',h.lat,h.lon,h.track_km,'km','Ti',h.TiO2,h.hub.join('+'));
for(const h of res.mars.hubs)console.log('MARS',h.lat,h.lon,h.hubN,h.hub.join('+'),'el',h.elev_km,'w',h.water,'TI',h.TI);
console.log(JSON.stringify(res.moon.studied));console.log(JSON.stringify(res.mars.studied2));console.log(JSON.stringify(Po));

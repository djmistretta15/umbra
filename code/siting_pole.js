// South pole detail: 1 km blocks from LOLA 60 m sunlight/shadow and 40 m slope
const fs=require('fs'),path=require('path');const D=process.argv[2];
const A=fs.readFileSync(path.join(D,'moon/AVGVISIB_85S_060M_201608.IMG')),S=fs.readFileSync(path.join(D,'moon/LPSR_85S_060M_201608.IMG')),Sl=fs.readFileSync(path.join(D,'moon/ldsm_85s_40m.img'));
const N6=5058,N4=7584,R=1737400,B=1000,half=N6*60/2,NB=Math.floor(2*half/B);
const sun=new Float32Array(NB*NB),psr=new Float32Array(NB*NB),cnt=new Float32Array(NB*NB),flat=new Float32Array(NB*NB),fc=new Float32Array(NB*NB);
const bi=(x,y)=>{const i=Math.floor((x+half)/B),j=Math.floor((half-y)/B);return i>=0&&j>=0&&i<NB&&j<NB?j*NB+i:-1};
for(let l=0;l<N6;l++)for(let s=0;s<N6;s++){const k=l*N6+s,x=(s-2528.5)*60,y=(2528.5-l)*60,b=bi(x,y);if(b<0)continue;
  const v=A.readUInt16LE(k*2)*0.00004,p=A.readInt16LE(k*2)<0?0:S.readInt16LE(k*2)*0.000025+0.5;
  if(v>sun[b])sun[b]=v;psr[b]+=(p>0.5?1:0);cnt[b]++}
for(let l=0;l<N4;l++)for(let s=0;s<N4;s++){const k=l*N4+s,dn=Sl.readInt16LE(k*2);if(dn===0)continue;const sl=dn*0.0015+45,x=(s-3791.5)*40,y=(3791.5-l)*40,b=bi(x,y);if(b<0)continue;fc[b]++;if(sl<10)flat[b]++}
const ll=(x,y)=>{const r=Math.hypot(x,y);return {lat:+(-90+2*Math.atan(r/(2*R))*180/Math.PI).toFixed(3),lon:+((Math.atan2(x,y)*180/Math.PI+360)%360).toFixed(2)}};
const blocks=[];
for(let j=0;j<NB;j++)for(let i=0;i<NB;i++){const b=j*NB+i;if(!cnt[b]||!fc[b])continue;
  const fl=flat[b]/fc[b],x=-half+(i+.5)*B,y=half-(j+.5)*B;
  let ice=99,pad=false;
  for(let dj=-5;dj<=5;dj++)for(let di=-5;di<=5;di++){const jj=j+dj,ii=i+di;if(jj<0||ii<0||jj>=NB||ii>=NB)continue;const o=jj*NB+ii,d=Math.hypot(di,dj);
    if(cnt[o]&&psr[o]/cnt[o]>0.05&&d<ice)ice=d;if(d>=2&&d<=5&&fc[o]&&flat[o]/fc[o]>0.8)pad=true}
  const f=[];if(sun[b]>=0.6)f.push('power');if(ice<=2)f.push('ice');if(fl>=0.6)f.push('landing');if(pad)f.push('pad');
  blocks.push({...ll(x,y),x,y,sun:+sun[b].toFixed(2),ice_km:ice,flat:+fl.toFixed(2),f,n:f.length})}
blocks.sort((a,b)=>b.n-a.n||b.sun-a.sun||b.flat-a.flat);
const hubs=[];for(const b of blocks){if(hubs.every(h=>Math.hypot(h.x-b.x,h.y-b.y)>8000))hubs.push(b);if(hubs.length>=12)break}
const LF=JSON.parse(fs.readFileSync(process.argv[3],'utf8')).hubs;
const toXY=(lat,lon)=>{const r=2*R*Math.tan((90+lat)*Math.PI/360);return [r*Math.sin(lon*Math.PI/180),r*Math.cos(lon*Math.PI/180)]};
for(const h of hubs){let best=1e9,nm='';for(const L of LF){const [x,y]=toXY(L.lat,L.lon),d=Math.hypot(x-h.x,y-h.y)/1000;if(d<best){best=d;nm=L.near}}h.lightflow_km=+best.toFixed(1);h.lightflow_near=nm;delete h.x;delete h.y}
const full=blocks.filter(b=>b.n===4).length;
fs.writeFileSync(process.argv[4],JSON.stringify({blocks_km2:blocks.length,all_four:full,hubs},null,1));
console.log('blocks',blocks.length,'all4',full);hubs.forEach(h=>console.log(JSON.stringify(h)));
LF.forEach(L=>console.log('LF',L.lat,L.lon,L.near,L.sun,L.km_to_shadow_ice));

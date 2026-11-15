// Umbra: science layers for the Moon and Mars globes (globe.html).
// Reads raw NASA PDS files and writes tex/globe_tex.js (data URIs + value grids, loads from disk or web).
// Usage: node code/build_globe_tex.mjs <Umbra-data dir>
// Rules mirror code/mars_ref.py and code/moon_ref.py so the globes agree with results/*.json.
import fs from 'fs'; import zlib from 'zlib'; import { spawn } from 'child_process'; import readline from 'readline';

const D = (process.argv[2] || 'C:/Users/Iconix/Desktop/Umbra-data').replace(/\\/g, '/');
const OUT = new URL('../tex/', import.meta.url);
fs.mkdirSync(OUT, { recursive: true });

// ---------- PNG writer (RGBA or gray) ----------
const CRC = new Int32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c; });
const crc = b => { let c = -1; for (const x of b) c = CRC[(c ^ x) & 255] ^ (c >>> 8); return (c ^ -1) >>> 0; };
function chunk(t, d) { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); }
function png(w, h, px, ch) { // px: Uint8Array w*h*ch, ch 1 (gray) or 4 (rgba)
  const raw = Buffer.alloc((w * ch + 1) * h);
  for (let y = 0; y < h; y++) { raw[y * (w * ch + 1)] = 0; Buffer.from(px.buffer, px.byteOffset + y * w * ch, w * ch).copy(raw, y * (w * ch + 1) + 1); }
  const ih = Buffer.alloc(13); ih.writeUInt32BE(w, 0); ih.writeUInt32BE(h, 4); ih[8] = 8; ih[9] = ch === 4 ? 6 : 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}
const uri = b => 'data:image/png;base64,' + b.toString('base64');

// ---------- colour ramps ----------
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const RAMP = {
  magma: ['#000004', '#2c115f', '#721f81', '#b73779', '#f1605d', '#feb078', '#fcfdbf'],
  viridis: ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
  cividis: ['#00204d', '#31446b', '#666970', '#958f78', '#cbba69', '#ffea46'],
  blues: ['#081d58', '#225ea8', '#41b6c4', '#c7e9b4', '#ffffd9'],
  ice: ['#e0f3ff', '#7cc4f2', '#2b7bd6', '#1a3d8f', '#0b1a47'],
  inferno: ['#000004', '#320a5e', '#781c6d', '#bc3754', '#ed6925', '#fbb61a', '#fcffa4'],
  sun: ['#140b34', '#4b1d6b', '#a33b5c', '#e46e2f', '#fdbd3a', '#fff9c4'],
};
function ramp(name, t) { const s = RAMP[name].map(hex); t = Math.max(0, Math.min(1, t)) * (s.length - 1); const i = Math.min(s.length - 2, Math.floor(t)), f = t - i; return s[i].map((v, k) => Math.round(v + (s[i + 1][k] - v) * f)); }

// ---------- helpers ----------
const rd = f => fs.readFileSync(`${D}/${f}`);
const i16 = (b, be) => { const n = b.length / 2, a = new Int16Array(n); for (let i = 0; i < n; i++) a[i] = be ? b.readInt16BE(i * 2) : b.readInt16LE(i * 2); return a; };
// sample an equirect grid (lat 90..-90 rows, lon lon0..lon0+360 cols) at lat/lon, nearest or bilinear
function sampler(a, W, H, lon0, bilinear) {
  return (lat, lon) => {
    let x = ((lon - lon0) % 360 + 360) % 360 / 360 * W - 0.5, y = (90 - lat) / 180 * H - 0.5;
    if (!bilinear) { const xi = ((Math.round(x) % W) + W) % W, yi = Math.max(0, Math.min(H - 1, Math.round(y))); return a[yi * W + xi]; }
    const x0 = Math.floor(x), y0 = Math.max(0, Math.min(H - 1, Math.floor(y))), y1 = Math.min(H - 1, y0 + 1), fx = x - x0, fy = Math.max(0, Math.min(1, y - y0));
    const g = (xx, yy) => a[yy * W + ((xx % W) + W) % W];
    const v = [g(x0, y0), g(x0 + 1, y0), g(x0, y1), g(x0 + 1, y1)], w = [(1 - fx) * (1 - fy), fx * (1 - fy), (1 - fx) * fy, fx * fy];
    let s = 0, ws = 0; v.forEach((q, k) => { if (Number.isFinite(q)) { s += q * w[k]; ws += w[k]; } });
    return ws > 0 ? s / ws : NaN;
  };
}
// render an equirect overlay (lon -180..180, the globe.gl convention)
function overlay(W, H, f) { const px = new Uint8Array(W * H * 4); for (let y = 0; y < H; y++) { const lat = 90 - (y + .5) / H * 180; for (let x = 0; x < W; x++) { const c = f(lat, -180 + (x + .5) / W * 360); if (c) px.set(c, (y * W + x) * 4); } } return png(W, H, px, 4); }
function grayEq(W, H, f, lo, hi) { const px = new Uint8Array(W * H); for (let y = 0; y < H; y++) { const lat = 90 - (y + .5) / H * 180; for (let x = 0; x < W; x++) { const v = f(lat, -180 + (x + .5) / W * 360); px[y * W + x] = Math.max(0, Math.min(255, Math.round((v - lo) / (hi - lo) * 255))); } } return png(W, H, px, 1); }
// value grid at 1 deg for click-to-read, quantized to uint8 (255 = no data)
function grid(f, lo, hi, log) {
  const b = new Uint8Array(360 * 180);
  for (let y = 0; y < 180; y++) for (let x = 0; x < 360; x++) { const v = f(89.5 - y, -179.5 + x); if (!Number.isFinite(v)) { b[y * 360 + x] = 255; continue; }
    const t = log ? (Math.log(v) - Math.log(lo)) / (Math.log(hi) - Math.log(lo)) : (v - lo) / (hi - lo); b[y * 360 + x] = Math.max(0, Math.min(254, Math.round(t * 254))); }
  return { lo, hi, log: !!log, b: Buffer.from(b).toString('base64') };
}
const A = (c, a) => [c[0], c[1], c[2], a];
const W = 1440, H = 720, BW = 1440, BH = 720;
const T = { mars: { layers: {}, vals: {} }, moon: { layers: {}, vals: {} }, pole: { layers: {}, vals: {} } };
const t0 = Date.now(), log = m => console.log(((Date.now() - t0) / 1000).toFixed(1) + 's ' + m);

// ================= MARS =================
// MOLA MEGDR 16 ppd, MSB int16, metres vs areoid, lon 0..360E
const mola = i16(rd('mars/megt90n000eb.img'), true); const hgt = sampler(mola, 5760, 2880, 0, true);
// TES nightside thermal inertia 20 ppd, MSB int16, lon -180..180
const tiR = i16(rd('mars/global_ti_night_2007.img'), true); const tiF = Float32Array.from(tiR, v => v > 0 ? v : NaN); const ti0 = sampler(tiF, 7200, 3600, -180, true), ti = (la, lo) => Math.abs(la) <= 60 ? ti0(la, lo) : NaN; // poleward TES TI is frost-affected; mars_ref.py uses the same 60 deg mask
// TES albedo 8 ppd, little-endian float32, lon -180..180
const albB = rd('mars/global_albedo_8ppd.img'), albF = new Float32Array(albB.length / 4); for (let i = 0; i < albF.length; i++) { const v = albB.readFloatLE(i * 4); albF[i] = v > 0 && v < 1 ? v : NaN; } const alb = sampler(albF, 2880, 1440, -180, true);
// Odyssey GRS water-equivalent hydrogen, 5 deg bins
const h2oG = new Float32Array(72 * 36).fill(NaN);
for (const ln of rd('mars/h2o_sr_5x5.tab').toString().split(/\r?\n/)) { const p = ln.trim().split(/\s+/).map(Number); if (p.length < 3 || p[2] > 9000) continue; let lo = p[1] > 180 ? p[1] - 360 : p[1]; h2oG[Math.floor((90 - p[0]) / 5) * 72 + (Math.floor((lo + 180) / 5) % 72)] = p[2]; }
const h2oN = sampler(h2oG, 72, 36, -180, false), h2o = sampler(h2oG, 72, 36, -180, true);
const pres = (la, lo) => 610 * Math.exp(-hgt(la, lo) / 11100); // same as mars_ref.py
const base = (la, lo) => { const w = h2oN(la, lo); return Number.isFinite(w) && w > 5 && hgt(la, lo) < 0 && ti(la, lo) >= 150 && Math.abs(la) <= 50; };
const tiClass = v => !Number.isFinite(v) ? null : v < 100 ? 0 : v < 150 ? 1 : v <= 400 ? 2 : v <= 1000 ? 3 : 4;
const TI_COL = ['#f4e3b5', '#d9a45b', '#b8613a', '#6d3b5e', '#1d2a5c'].map(hex);
T.mars.layers.pressure = uri(overlay(W, H, (la, lo) => A(ramp('magma', (Math.log(pres(la, lo)) - Math.log(100)) / (Math.log(1300) - Math.log(100))), 235))); log('mars pressure');
T.mars.layers.ground = uri(overlay(W, H, (la, lo) => { const c = tiClass(ti(la, lo)); return c == null ? null : A(TI_COL[c], 215); })); log('mars ground');
T.mars.layers.dust = uri(overlay(W, H, (la, lo) => { const a = alb(la, lo); return Number.isFinite(a) ? A(ramp('cividis', (a - .08) / (.32 - .08)), 225) : null; })); log('mars dust');
T.mars.layers.water = uri(overlay(W, H, (la, lo) => { const w = h2o(la, lo); return Number.isFinite(w) ? A(ramp('blues', (w - 1.5) / (8 - 1.5)), 225) : null; })); log('mars water');
T.mars.layers.base = uri(overlay(W, H, (la, lo) => base(la, lo) ? [255, 181, 71, 245] : [4, 6, 13, 120])); log('mars base');
T.mars.bump = uri(grayEq(BW, BH, hgt, -8500, 21000)); log('mars bump');
T.mars.vals = { height: grid(hgt, -8500, 21500), pressure: grid(pres, 30, 1300, true), ti: grid(ti, 20, 2000, true), albedo: grid(alb, .05, .4), water: grid(h2oN, 0, 10) };

// ================= MOON (global) =================
const ldem = i16(rd('moon/ldem_16.img'), false); const mh = sampler(Float32Array.from(ldem, v => v * .5), 5760, 2880, 0, true);
T.moon.bump = uri(grayEq(BW, BH, mh, -9000, 10500)); log('moon bump');
// Lunar Prospector GRS (Prettyman), 2 deg equal-area pixels; columns per lpgrs_elem_abundance.fmt
const G2 = { feo: new Float32Array(720 * 360).fill(NaN), tio2: new Float32Array(720 * 360).fill(NaN), th: new Float32Array(720 * 360).fill(NaN) };
for (const ln of rd('moon/lpgrs_high1_elem_abundance_2deg.tab').toString().split(/\r?\n/)) {
  const p = ln.trim().split(/\s+/).map(Number); if (p.length < 16) continue;
  const [, la0, la1, lo0, lo1] = p, v = { tio2: p[11] * 100, feo: p[12] * 100, th: p[14] };
  for (let y = Math.round((90 - la1) * 2); y < Math.round((90 - la0) * 2); y++) for (let x = Math.round((lo0 + 180) * 2); x < Math.round((lo1 + 180) * 2); x++) { const i = y * 720 + (x % 720); for (const k in v) G2[k][i] = v[k]; }
}
const fe = sampler(G2.feo, 720, 360, -180, true), tio = sampler(G2.tio2, 720, 360, -180, true), th = sampler(G2.th, 720, 360, -180, true);
T.moon.layers.feo = uri(overlay(W, H, (la, lo) => A(ramp('inferno', (fe(la, lo) - 2) / (22 - 2)), 215))); log('moon feo');
T.moon.layers.tio2 = uri(overlay(W, H, (la, lo) => A(ramp('viridis', tio(la, lo) / 8), 215))); log('moon tio2');
T.moon.layers.th = uri(overlay(W, H, (la, lo) => A(ramp('magma', th(la, lo) / 10), 215))); log('moon th');
T.moon.vals = { height: grid(mh, -9500, 11000), feo: grid(fe, 0, 25), tio2: grid(tio, 0, 12), th: grid(th, 0, 14) };

// ================= MOON south pole cap (85S to pole, polar stereographic, 60 m source) =================
// orientation checked against Shackleton, Haworth, Faustini, Sverdrup (all permanent shadow): sample = C + x/60, line = C - y/60
const N = 5058, C = (N - 1) / 2, R = 1737400, K = 6, P = Math.floor(N / K); // 843 px cap, 360 m/px
const vis = i16(rd('moon/AVGVISIB_85S_060M_201608.IMG'), false), psr = i16(rd('moon/LPSR_85S_060M_201608.IMG'), false);
const capR = 2 * R * Math.tan((Math.PI / 2 - 85 * Math.PI / 180) / 2); // stereographic radius at 85S
const sunC = new Float32Array(P * P), psrC = new Float32Array(P * P);
for (let y = 0; y < P; y++) for (let x = 0; x < P; x++) { let s = 0, n = 0, q = 0; for (let j = 0; j < K; j++) for (let i = 0; i < K; i++) { const k = (y * K + j) * N + x * K + i, v = vis[k] * 4e-5; if (v >= 0 && v <= 1) { s += v; n++; } if (psr[k] * 2.5e-5 + .5 > .5) q++; } sunC[y * P + x] = n ? s / n : NaN; psrC[y * P + x] = q / (K * K); }
const inCap = (x, y) => { const m = (N * 60) / P, dx = (x + .5 - P / 2) * m, dy = (y + .5 - P / 2) * m; return Math.hypot(dx, dy) <= capR; };
function capPng(f) { const px = new Uint8Array(P * P * 4); for (let y = 0; y < P; y++) for (let x = 0; x < P; x++) { if (!inCap(x, y)) continue; const c = f(y * P + x); if (c) px.set(c, (y * P + x) * 4); } return png(P, P, px, 4); }
T.pole.layers.sun = uri(capPng(i => Number.isFinite(sunC[i]) ? A(ramp('sun', sunC[i] / .9), 235) : null)); log('pole sun');
T.pole.layers.shadow = uri(capPng(i => psrC[i] > .5 ? [40, 120, 255, 235] : [8, 10, 20, 150])); log('pole shadow');
// Diviner polar resource product (Paige): annual max temperature and depth to stable ice, binned to the cap grid
const S = new Float64Array(P * P), Cn = new Float64Array(P * P), IceS = new Float64Array(P * P), IceN = new Float64Array(P * P), IceAny = new Float64Array(P * P);
await new Promise((res, rej) => {
  const u = spawn('unzip', ['-p', `${D}/moon/dlre_prp_south.zip`]); const rl = readline.createInterface({ input: u.stdout }); let hdr = true;
  rl.on('line', ln => { if (hdr) { hdr = false; return; } const p = ln.split(','); const la = +p[10]; if (!(la <= -85)) return; const lo = +p[9] * Math.PI / 180, tm = +p[13], ice = +p[14];
    const r = 2 * R * Math.tan((Math.PI / 2 + la * Math.PI / 180) / 2), x = Math.floor((C + r * Math.sin(lo) / 60) / K), y = Math.floor((C - r * Math.cos(lo) / 60) / K); if (x < 0 || y < 0 || x >= P || y >= P) return;
    const i = y * P + x; S[i] += tm; Cn[i]++; IceAny[i]++; if (ice >= 0) { IceS[i] += ice; IceN[i]++; } });
  rl.on('close', res); u.on('error', rej);
}); log('diviner read');
function fill(a){const o=a.slice();for(let y=1;y<P-1;y++)for(let x=1;x<P-1;x++){const i=y*P+x;if(Number.isFinite(a[i]))continue;let s=0,n=0;for(const d of [-1,1,-P,P,-P-1,-P+1,P-1,P+1])if(Number.isFinite(a[i+d])){s+=a[i+d];n++}if(n>=3)o[i]=s/n}return o}
const tmax = fill(Float32Array.from(S, (s, i) => Cn[i] ? s / Cn[i] : NaN)), iceD = Float32Array.from(IceS, (s, i) => IceN[i] / Math.max(1, IceAny[i]) >= .5 ? s / IceN[i] : NaN); const iceD2 = fill(iceD);
T.pole.layers.cold = uri(capPng(i => Number.isFinite(tmax[i]) ? A(ramp('inferno', (tmax[i] - 25) / (330 - 25)), 235) : null)); log('pole cold');
T.pole.layers.ice = uri(capPng(i => Number.isFinite(iceD2[i]) ? A(ramp('ice', Math.min(1, iceD2[i] / 1)), 235) : (Number.isFinite(tmax[i]) ? [8, 10, 20, 130] : null))); log('pole ice');
const D3 = a => { const n = Math.floor(P / 3), o = new Float32Array(n * n); for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) { let s = 0, c = 0; for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) { const v = a[(y * 3 + j) * P + x * 3 + i]; if (Number.isFinite(v)) { s += v; c++; } } o[y * n + x] = c ? s / c : NaN; } return o; };
const q8 = (a, lo, hi) => Buffer.from(Uint8Array.from(a, v => Number.isFinite(v) ? Math.max(0, Math.min(254, Math.round((v - lo) / (hi - lo) * 254))) : 255)).toString('base64');
T.pole.vals = { n: Math.floor(P / 3), m_per_px: N * 60 / Math.floor(P / 3), cap_lat: -85, sun: { lo: 0, hi: 1, b: q8(D3(sunC), 0, 1) }, shadow: { lo: 0, hi: 1, b: q8(D3(psrC), 0, 1) }, tmax: { lo: 20, hi: 340, b: q8(D3(tmax), 20, 340) }, ice: { lo: 0, hi: 2, b: q8(D3(iceD2), 0, 2) } };

// Flat ground: share of each cap cell with LOLA slope under 8 degrees (LDSM 40 m; DN 0 = missing)
{ const SN = 7584, SC = 3791.5, sl = i16(rd('moon/ldsm_85s_40m.img'), false), m = N * 60 / P, flat = new Float32Array(P * P);
  for (let y = 0; y < P; y++) for (let x = 0; x < P; x++) { const X0 = (x - P / 2) * m, Y0 = -(y - P / 2) * m; let f = 0, n = 0;
    for (let j = 0; j < 9; j++) for (let i = 0; i < 9; i++) { const X = X0 + (i + .5) / 9 * m, Y = Y0 - (j + .5) / 9 * m, s = Math.round(SC + X / 40), l = Math.round(SC - Y / 40); if (s < 0 || l < 0 || s >= SN || l >= SN) continue; const d = sl[l * SN + s]; if (!d) continue; n++; if (d * .0015 + 45 < 8) f++; }
    flat[y * P + x] = n ? f / n : NaN; }
  T.pole.layers.flat = uri(capPng(i => Number.isFinite(flat[i]) ? A(ramp('cividis', flat[i]), 235) : null)); T.pole.vals.flat = { lo: 0, hi: 1, b: q8(D3(flat), 0, 1) }; log('pole flat'); }

// Earth in view: share of the libration cycle when Earth's centre is above the local LOLA horizon (direct radio to Earth).
// Horizons from LDEM 80 m binned to 400 m, rays out to 250 km with lunar curvature, from the highest 400 m point in each km cell.
{ const LN = 7600, LC = 3799.5, dem = i16(rd('moon/ldem_80s_80m.img'), false), G = 1520, GC = (G - 1) / 2, h4 = new Float32Array(G * G);
  for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) { let s = 0; for (let j = 0; j < 5; j++) for (let i = 0; i < 5; i++) s += dem[(y * 5 + j) * LN + x * 5 + i]; h4[y * G + x] = s / 25 * .5; }
  const hAt = (X, Y) => { const c = Math.round(GC + X / 400), r = Math.round(GC - Y / 400); return c < 0 || r < 0 || c >= G || r >= G ? NaN : h4[r * G + c]; };
  const steps = []; for (let s = 400; s < 250000; s *= 1.035) steps.push(s);
  const ST = []; for (let a = 0; a < 6; a++) for (let b = 0; b < 6; b++) { const le = 6.68 * Math.sin((a + .5) / 6 * 2 * Math.PI) * Math.PI / 180, lo = 7.9 * Math.sin((b + .5) / 6 * 2 * Math.PI) * Math.PI / 180; ST.push([Math.cos(le) * Math.cos(lo), Math.cos(le) * Math.sin(lo), Math.sin(le)]); }
  const n = Math.floor(P / 3), m = N * 60 / n, earth = new Float32Array(n * n).fill(NaN);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const Xc = (x + .5 - n / 2) * m, Yc = -(y + .5 - n / 2) * m; if (Math.hypot(Xc, Yc) > capR + m) continue;
    let X = Xc, Y = Yc, h0 = -Infinity; for (let j = -1; j <= 1; j++) for (let i = -1; i <= 1; i++) { const Xi = Xc + i * 360, Yi = Yc + j * 360, h = hAt(Xi, Yi); if (h > h0) { h0 = h; X = Xi; Y = Yi; } }
    if (!Number.isFinite(h0)) continue; h0 += 2;
    const r = Math.hypot(X, Y), la = 2 * Math.atan(r / (2 * R)) - Math.PI / 2, lo = Math.atan2(X, Y), U = [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
    let up = 0;
    for (const E of ST) { const d = E[0] * U[0] + E[1] * U[1] + E[2] * U[2], e = Math.asin(d), tx = E[0] - d * U[0], ty = E[1] - d * U[1], tn = Math.hypot(tx, ty), dX = ty / tn, dY = tx / tn, te = Math.tan(e);
      let vis = true; for (const s of steps) { const h = hAt(X + dX * s, Y + dY * s); if (!Number.isFinite(h)) break; if ((h - h0 - s * s / (2 * R)) / s >= te) { vis = false; break; } }
      if (vis) up++; }
    earth[y * n + x] = up / ST.length; }
  const eP = i => { const y = Math.floor(i / P / 3), x = Math.floor(i % P / 3); return y < n && x < n ? earth[y * n + x] : NaN; };
  T.pole.layers.earth = uri(capPng(i => { const v = eP(i); return Number.isFinite(v) ? A(ramp('viridis', v), 235) : null; }));
  T.pole.vals.earth = { lo: 0, hi: 1, b: q8(earth, 0, 1) }; log('pole earth'); }

fs.writeFileSync(new URL('globe_tex.js', OUT), '/* Umbra science layers, built by code/build_globe_tex.mjs from NASA PDS data. */\nwindow.UMBRA_TEX=' + JSON.stringify(T) + ';\n');
log('wrote tex/globe_tex.js ' + (fs.statSync(new URL('globe_tex.js', OUT)).size / 1e6).toFixed(1) + ' MB');
// quick previews for checking by eye
for (const b of ['mars', 'moon', 'pole']) for (const [k, v] of Object.entries(T[b].layers)) fs.writeFileSync(new URL(`prev_${b}_${k}.png`, OUT), Buffer.from(v.split(',')[1], 'base64'));

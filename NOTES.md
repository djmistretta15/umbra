# Umbra working notes (Team Forced Futures, Space Apps 2026, challenge #10)

Running log of lenses, coverage and ideas. Newest at the bottom.

## 1. Challenge dimensions vs Umbra (audit, Sat Nov 14 evening)

| Challenge dimension | Umbra tests | Gap |
|---|---|---|
| Geology, mineralogy, surface materials | mare basalt, highland rock, impact rock, volcanic glass, ancient crust, magnetic memory, oxygen feedstock | spectral minerals (clays, sulfates) e.g. NASA EMIT |
| Terrain, slope, roughness, craters | pad rock, featureless, walk back, radio shadow, landing blast, impact rock | roughness and boulders |
| Temperature, illumination, extremes | deep cold, thermal swing, low sun, lunar night, power ridge, radiative cold, work in shadows | solid |
| Water, ice, permafrost, resources | dry permafrost, ice ratio, sun-ice edge, work in shadows | Mars-style buried glacier ice |
| Dust, wind, erosion, atmosphere | seal dust, dust devils, dust storm, soft sand, sand ratio, dust mantle, dirty panels, thin air | erosion rate |
| Biology, habitability, biosignatures | hyperarid sterile, salt biosig, oxidant soil, hydrothermal, erasers off | vegetation edge (NASA MODIS NDVI) |
| Subsurface, caves, lava tubes | lava tubes, karst caves, ringing ground | mines |
| Landing, mobility, navigation, ops, construction | pad rock, no compass, low sun, landing blast, radio shadow, walk back, dirty panels, oxygen feed | solid |
| Processes (past and present) | sand ratio, ice ratio, erasers, light-flow | Mars water past: megafloods, deltas, clay alteration |

## 2. Lenses the challenge did not name (ours)

1. Time: how fast Earth erases records (erasers_off, meteorite check).
2. Ratios: match the governing physics number, not the look (sand u*/u*t, ice frost point).
3. Paths and hubs: let physics route traffic; hubs = lunar NYC (light-flow; 5 of 12 hubs at Artemis III crater areas).
4. Orbiter's-eye view: places that read the same to an instrument (look-alike finder, TES-style fingerprints).
5. Exposure chemistry: how gear ages (UV, cycling, dust, fresh glass).
6. Fields and signals: magnetism, radio quiet, radio shadow, seismic ringing.
7. Reverse direction: what Moon and Mars tell us about Earth (meteorite check 67% vs 25%).
8. Earth's limits as a deliverable: ledger of what cannot be tested on Earth.

## 3. To build next (agreed)

- Restructure the Constraint Map by the challenge dimensions + "what they didn't name".
- Report cards for headline sites: per dimension, strong / partial / none, plus honest misses.
- Close gaps: MODIS vegetation edge, Mars megaflood and delta process analogs, buried glacier ice.

## 4. New lenses from what lasts, what differs, and bottleneck theory (Sat 6:40 PM)

What lasts
- Footprint persistence: lunar boot prints and rover tracks last for millions of years. Where on Earth do tracks last decades (desert pavements)? Planning for site disturbance and planetary protection.
- Collectors: places where something piles up because the system concentrates it. Lunar cold traps collect water; Antarctic blue-ice fields collect meteorites by sublimation. Same process, two worlds.

What makes it different
- Distance-from-Moon index: per dimension, how far the best Earth site still is from the Moon value. Turns "Earth's limits" into numbers.
- Impact glass in the open: Libyan Desert Glass and tektite strewn fields as analogs for lunar impact glass beads (Sahara again).

Instruments checking themselves
- Calibration sites: NASA and partners calibrate satellites on Earth's most unchanging deserts (pseudo-invariant sites such as Libya-4), and use the Moon itself as a calibration target for Earth satellites. The steadiest places on Earth are where a Moon-reading instrument can check itself.

Bottleneck theory (what is scarce)
- Contested ground: the Moon's best sunlit ridges cover under 1 km2 above 70% sun. Analog for planning shared, scarce real estate (light-flow hubs show where traffic jams form).
- Supply line: the true bottleneck is resupply cadence. Earth stations resupplied once a year by ship or air are the logistics analog.
- Night power: the two-week night is the power bottleneck (lunar_night test exists).

Breadcrumbs both ways
- Meteorites (done), impact glass (above), collectors (above).

## 5. System analogs: beyond places (Sat 6:50 PM)

Dan's steer: analogs are not only sites. Earth already runs systems, infrastructure, data, power and sensing that face a version of a Moon bottleneck.  The tool should show people what they are missing and could test on Earth, starting with life support.

Shape for each entry: Moon bottleneck (from the Forced Futures node map) -> Earth system already living it -> where it runs -> what transfers -> what does not.

Life support first (node map Life Beyond Earth / Habitation / Power):
- Air ledger must balance (CO2 in = CO2 out): nuclear submarines (sealed for months, oxygen by electrolysis, CO2 scrubbing); refuge chambers in underground mines; Biosphere 2's oxygen crash as the failure case.
- Every drop circles back: direct potable water reuse plants; Antarctic station greywater recycling.
- Calories per watt: vertical farms and Antarctic greenhouses report energy per kg of food.
- Waste becomes fertilizer: nutrient recovery at wastewater plants.
- Microbes in the walls: biofilm control in hospital water systems and food plants.
- Outbreak with nowhere to go: cruise ships, submarines, winter-over stations.
- Power is breath: hospitals and data centers run on tiered backup power.
- Sealed clean habitat underground: SNOLAB, a clean lab 2 km down a working nickel mine in Sudbury, all air and supplies brought down a shaft.

Borrowed senses (BFLY-style):
- Ultrasound on a chip -> wall, weld and pressure-vessel checks in habitats; robot touch.
- Wastewater surveillance (sewage sequencing) -> in a closed habitat the water loop is the sewer: sequence it for early outbreak warning.
- Car lidar -> landing and rover navigation in low sun.
- Oil-field geophones and archaeology ground radar -> finding buried ice and lava tubes.
- Farm hyperspectral cameras -> mineral and contamination checks.
- Electronic noses from food safety -> air contaminant and fire warning in sealed habitats.

Future walls the Moon will force (node map): water split between drinking and rocket fuel; power outage equals survival emergency; calories per watt; small ecosystems tipping over; biofilm; medicine far from hospitals.

## 6. Correction: the BFLY lens is about mispricing, not the device (Sat 7:55 PM)

The market priced BFLY as one medical device; we saw five technologies in it. The lens: one asset, many jobs, priced as one.
Applied to analogs: a place or system known for one analog use that quietly serves many. Value = how many analog jobs it can do. Price = how much attention it already gets.
- Underpriced analog = high multiplicity, low attention. Computable: count the distinct analog layers each block ranks top in, divided by how close it is to already-studied analog sites.
- Candidates from our own results: northern Chad / Tibesti (portfolio, dirty panels, exposure, ringing ground, Mars dust fingerprint); Saudi harrats (mare basalt, oxygen feedstock, lava tubes); western Tibet (portfolio 8, walk back, 1 km profile); Yakutia (shadow work, deep cold).
- Systems too: SNOLAB is "a physics lab" but is also a sealed habitat, underground logistics, a radiation-shielded room and a seismically quiet site.
- The Moon itself: priced as a destination, but also a fuel depot, a calibration target, a radio-quiet observatory and a lever for leaving Earth's gravity.

## 7. App refinements (Sat 11:15 PM)

- Umbra Live now ships the engine's own top-3% masks, so its expedition and job counts match the engine exactly.
- Expedition ranking changed to the rule we actually claim (tests in the top 3% inside one 2-degree block): northern Chad 9, western Tibet 8, Atacama 8, Dry Valleys 7, Saudi lava fields 7, Axel Heiberg area 7. Deck, page and form updated to match.
- New in Live: report cards (similar / how similar / different per dimension, Earth limits, download), Underpriced tab, Systems tab (life support first), 30-second guided tour.

## 8. Hidden channels in NASA Moon data (Sun morning)

Lens: each dataset is priced as one measurement but carries several channels (AirPods are "speakers" but also motion and pressure sensors).
#1 LOLA, priced as "an altimeter": time (height, slope); pulse stretch (roughness inside each 5 m spot); echo strength (brightness in its own laser light, even in dark craters: frost hint and how robot lidar sees the ground); horizon shape (sunlight, shadow, Earth in view); roughness at every scale (terrain fingerprint); laser ranging from Earth (timing, Earth-Moon laser links); crater counts (surface age).
Unused channel: Earth has its own LOLA (NASA ICESat-2 and GEDI). Match laser to laser: Earth tracks whose roughness and pulse stretch read like LOLA tracks over the south pole. Caveat: different laser colours, so brightness needs scaling.
Next on the list: #2 LROC cameras.
#2 LROC, priced as "a camera" (NAC 0.5 m, WAC 7 colours): brightness vs sun angle (how fluffy the soil is; lander blast zones show up as bright halos); shadow lengths (boulder heights, hazard); stereo (2 m height maps); repeat images (new impact craters forming today = impact risk rate; boulders that rolled after moonquakes = a seismic channel from a camera); UV colour ratio (titanium = oxygen feedstock; soil age); pits and skylights (lava tube doors); Apollo hardware and tracks photographed after 50+ years (materials aging time capsule, footprint persistence).
Unused Earth channel: desert rocket landing pads (e.g. Blue Origin's Van Horn, Texas) leave blast halos visible to Landsat/Sentinel over time: Earth's version of LROC's lander blast zones.
#3 Mini-RF, priced as "an ice detector" (S- and X-band radar on LRO): echo strength (rocks the size of the radio wave, cm to dm, including buried ones); polarization ratio (blockiness; ice and fresh rough ejecta look alike, so it is also a crater-age clock as ejecta smooths); penetration (sees about a metre down in dry regolith; titanium-rich soil absorbs more, so loss = composition); dielectric constant (soil density, how well the ground will bear a load); bistatic mode (a dish on Earth transmits, LRO listens: an Earth-Moon radio link test and an ice test by viewing angle); works in total darkness.
Earth mirror: NISAR (NASA-ISRO, launched 2025) carries S-band radar, the same band as Mini-RF S-band. In hyperarid sand, radar sees metres down: the 1981 Shuttle radar found buried river channels under the eastern Sahara. Dry Earth where radar sees deepest = analog for lunar and Martian subsurface radar (and for SHARAD/MARSIS buried ice).
#4 Diviner, priced as "a thermometer" (9 channels from reflected sunlight to far infrared): temperature (used); the cooling curve through the night (how packed the soil is with depth, dust depth); rock abundance (rocks stay warm at night; finds boulders too small to photograph; rocks break down, so it is a clock); the 8-micron channels (silicate minerals, feedstock); eclipse cooling (hours-long test of night survival); coldest spots (where ice and even CO2 can stay frozen: a carbon resource); night-time cold halos around new craters (fluffed soil, a young-impact clock); thermal roughness (sunlit vs shaded slopes inside one pixel).
Earth mirror: ASTER and ECOSTRESS read the same 8-12 micron mineral physics; ECOSTRESS on the ISS samples different hours, so it can trace cooling curves. Total solar eclipse of 2 Aug 2027 crosses North Africa (Morocco to Egypt): a planned "mini lunar night" over the Sahara to measure how desert ground cools.
#5 Illumination and Earth-visibility maps (from LOLA heights), priced as "sunlight %": average sun (used); longest unbroken darkness (sizes batteries, a different number from the average); sun direction through the month (panel and mirror placement); light vs height above ground (a 10 m mast can gain a lot of sun: vertical real estate); Earth visibility (radio windows) and Earthshine as faint light inside shadow; permanent shadow (cold traps) and light scattered off sunlit walls; moving shadow edges (thermal cycling, low-sun navigation); sun AND Earth both up (operating calendar, hub condition).
Earth mirror: VIIRS Day/Night Band (NASA/NOAA) sees the ground by moonlight, so Arctic polar night under moonlight (Svalbard, Ellesmere) is a test bed for cameras and navigation at lunar-shadow light levels. Eureka's PEARL ridge lab (610 m) is a ready place to test sun gain with mast height in polar summer.
#6 Neutron detectors (Lunar Prospector, LRO LEND), priced as "hydrogen finders". Physics: cosmic rays knock neutrons out of the soil; what comes back depends on what the soil is made of.
Channels: slowed (epithermal) neutrons missing = hydrogen in the top metre (used); thermal neutrons absorbed = iron, titanium and the rare earths gadolinium and samarium (a rare-earth / KREEP map); fast neutrons = average atomic mass (bulk composition); thermal vs epithermal ratio = whether ice is buried under a dry layer, and how deep (digging plan); the neutron flux itself = part of the crew radiation dose, including neutrons made inside regolith shielding; the long time series = solar-cycle record of cosmic rays; hydrogen trends with latitude = solar-wind hydrogen in sunlit soil (a resource outside the dark craters).
Earth mirror: Earth already uses the Moon's method. Cosmic-ray neutron sensors measure soil moisture on farms and research sites (COSMOS networks) with the same physics. Test bed for lunar neutron instruments and digging plans: high plateaus with more cosmic rays and ice under a dry layer (our Pamir block scores both: top cosmic-ray exposure and Mars-like ground-ice ratio; Dry Valleys dry permafrost over ice is the two-layer case). Rare-earth deposits with known grades could calibrate neutron rare-earth prospecting from rovers.
#7 LAMP (far-ultraviolet spectrograph on LRO), priced as "frost in the dark". It sees inside permanently shadowed craters by starlight and the faint ultraviolet glow of the sky.
Channels: brightness on vs off the water band (surface frost, about 1-2% in places); overall darkness of shadowed soil (very fluffy, highly porous ground: how far a rover sinks); daytime water band changing with time of day (water hops across the surface daily: replenishment); the thin atmosphere (helium, argon, hydrogen); impact plumes (LCROSS and GRAIL impacts released hydrogen and mercury: the ice may carry toxins); UV colour slope (how long soil has been exposed); spacecraft exhaust in the gas (contamination of the very ice we want to study).
Earth mirror: Earth's ozone blocks far-UV, so there is no orbital twin; the channels still map. Mercury in ice: Arctic permafrost stores large amounts of mercury, and thaw studies (Alaska, Yukon) are a ready test of cleaning toxic meltwater, a life-support system analog for lunar ice. Daily water hopping: Atacama salts pull water from the air overnight and dry by day, the same daily cycle. Fluffy shadowed soil: the lowest-density natural ground (fresh volcanic ash, diatomite) for rover sinkage tests.
#8 LCROSS (2009: a spent rocket stage hit Cabeus crater, a trailing probe flew through the plume), priced as "it found ~5% water".
Channels: water amount (famous); the rest of the cocktail (ammonia = nitrogen for air and fertiliser, CO2, methane, methanol = carbon, sulfur compounds incl. toxic hydrogen sulfide, plus mercury seen by LAMP); plume growth (how icy shadowed soil flies at impact: ejecta and plume physics); the crater it left, later imaged by LRO (known mass + speed -> crater size = strength of cold icy soil); the hot spot cooling (thermal properties of shadowed soil); the method (a spent stage used as a drill: junk becomes a sampling tool); one ground-truth point that calibrates every orbital ice sensor (LEND, LAMP, Mini-RF, Diviner).
Earth mirror: ice laced with volcanic gases, the LCROSS cocktail: Mount Erebus fumarolic ice caves (Antarctica) and Kverkfjoll glacier caves (Iceland). NASA Ames Vertical Gun Range fires projectiles into regolith and ice simulants: Earth's LCROSS. Calibration sites that anchor orbital sensors to one measured point (cal/val sites) are the calibration analog.
#9 Moon Mineralogy Mapper (M3, NASA instrument on India's Chandrayaan-1, 2008-09; imaging spectrometer 0.4-3 microns), priced as "found water on the surface".
Channels: 3-micron band (OH and water across the surface, famous); 1- and 2-micron bands (pyroxene, olivine, plagioclase: what every rock unit is made of; it found a new lunar rock type rich in pink spinel); exposed ice inside shadowed craters, seen by faint bounced light; the heat tail at long wavelengths (a thermometer hiding in the noise); the water band changing with time of day and latitude (daily water cycle, matches LAMP); space weathering (how long soil has been exposed; magnetic swirls like Reiner Gamma stay fresh because local magnetic fields deflect the solar wind: natural radiation shelter clue).
Earth mirror: NASA EMIT on the ISS is the same kind of instrument (0.4-2.5 microns) and maps minerals in Earth's deserts (Sahara, Arabia, Atacama). Same method on both worlds; an EMIT mineral GeoTIFF can be dropped straight into Umbra Live as a layer (needs an Earthdata login). Our Chad block already scores on "rock with strong fossil magnetism"; Earth's air hides the swirl shielding effect, so that part is a stated gap.
#10 SOFIA (NASA/DLR flying 747 telescope, retired 2022), priced as "molecular water on the sunlit Moon" (6-micron band at Clavius crater, roughly 100-400 parts per million).
Channels: the 6-micron band tells H2O apart from OH, which the 3-micron band cannot; the amount and its trap (water likely sealed in impact glass or between grains: bake the glass to get water); more water toward high latitudes (siting); heat glow at 6 microns (temperature); the platform itself (flying above most of Earth's water vapour to see water elsewhere).
Earth mirror: water in glass -> volcanic glass and impact glass (tephra, obsidian; Libyan Desert Glass, Darwin Glass) as feedstock to rehearse baking water out of glass; our volcanic-glass and impact-rock tests point to these. Above the water vapour -> the driest high sites where infrared observatories go: Chajnantor in the Atacama and Ali Observatory at 5,100 m in Ngari, western Tibet, next to our Tibet block.
#11 Lunar Prospector gamma-ray spectrometer (1998-99), priced as "element map" (thorium, potassium, uranium, iron, titanium and more).
Channels: thorium/potassium/uranium = natural radioactivity, tracing KREEP rock (potassium, rare earths, phosphorus); a far-side thorium hot spot, Compton-Belkovich, is granite-like volcanism the Moon "should not" have; heat-producing elements = where the crust runs warmer (links to heat flow); iron and titanium = mare feedstock for oxygen and metal; KREEP's phosphorus = fertiliser for lunar farms (life support); the gamma background itself = part of the radiation environment and the noise floor every future detector must handle.
Earth mirror: Earth maps K, Th and U the same way, from aircraft: Geoscience Australia's national radiometric map and USGS surveys are public layers that can be dropped into Umbra Live. KREEP-like rock on Earth = carbonatites rich in rare earths and phosphate, e.g. Mount Weld in arid Western Australia (inside the radiometric survey) or Mountain Pass, California: test processing for phosphorus and rare earths, and test whether gamma mapping finds the ore.
#12 Clementine (1994, US defense + NASA), priced as "a missile-defense sensor test" that happened to map the Moon: the mission itself is a mispricing case.
Channels: 5 visible/UV colours -> iron and titanium maps (the Lucey ratio method still used today); a soil-maturity index (how long soil has been exposed); near-infrared bands (pyroxene and olivine); a laser altimeter (first global shape of the Moon, the depth of the south-pole basin); a bistatic radar test (the first hint of polar ice, 1996, debated); star trackers (navigation, plus earthshine and faint glow images); a thermal camera; the program (built in about two years with lightweight military sensors: fast, cheap, qualified in deep space).
Earth mirror: run the same iron/titanium colour-ratio idea on Earth basalts to find the rare titanium-rich ones like high-Ti mare. Best ready match: ilmenite mines hosted in anorthosite, the Moon's two key rocks together, e.g. Lac Tio (Havre-Saint-Pierre, Quebec) and Tellnes (Norway): oxygen-extraction feedstock with highland-type host rock, already being mined.
#13 Apollo samples (382 kg from six landings; some sealed tubes opened only in 2019-2022 by NASA's ANGSA program), priced as "Moon rocks".
Channels: chemistry and minerals (the ground truth that calibrates every orbital map); radiometric ages (they calibrate crater-count dating used for the Moon, Mars and Mercury); grain shape and size (sharp, glassy dust: lung, seal and simulant design); Apollo soil mechanics (penetrometer, core tubes, bootprints: bearing strength for construction); solar-wind gases (hydrogen, helium-3, nitrogen, carbon in sunlit soil, plus a 4-billion-year record of the Sun); cosmic-ray exposure ages (how fast soil is churned: how fast footprints and hardware get buried); magnetized rocks (the Moon's ancient magnetic field); a fragment in an Apollo 14 rock that may be from early Earth (the Moon as Earth's archive); plants grown in Apollo soil in 2022 (they grew, but stressed); sealed samples opened 50 years later (curation method, a storage time capsule).
Earth mirror: Earth's earliest record survives at Jack Hills (Western Australia) and Acasta (Canada); the Moon may hold what Earth erased (breadcrumbs both ways). Farming in regolith: Lanzarote's La Geria vineyards grow crops in pits dug into basaltic ash, an existing analog for farming in lunar soil (Lanzarote is known for lava tubes, not this). Simulant quarries: lunar simulants come from Earth rock (Arizona cinder, Stillwater anorthosite in Montana); Umbra's match scores could rank candidate quarries.
#14 GRAIL (2011-12, twin probes Ebb and Flow measuring their separation to micrometres), priced as "gravity map".
Channels: gravity field (crust thickness and density); crust porosity (the upper crust is roughly 10-20% empty cracks from impacts: why moonquakes ring, how heat moves, ground stability); long buried intrusions (dikes and rifts from the early Moon); mass concentrations that tug on low orbits (orbit stability for relay satellites; a 1972 subsatellite crashed from this); gravity lows that may be large empty lava tubes (shelter); tidal flexing (interior, and the precise reference frame for landing navigation); its own final impact (plume seen by LAMP); the ranging link (precision formation flying).
Earth mirror: GRACE and GRACE-FO use the same twin-satellite method on Earth and watch groundwater drain. The Nubian Sandstone Aquifer under Egypt, Libya, Sudan and Chad holds fossil water from a wetter past with almost no recharge; Libya pumps it at Kufra (center-pivot farms visible from space), next to our Chad block. Mining a finite ancient water deposit in hyperarid ground is the lunar polar-ice and Mars ground-ice problem: depletion rates, governance, and measuring it by gravity like GRAIL. Gravity surveys also find caves on Earth (karst), the same as GRAIL's lava-tube hunt.
#15 Apollo seismometers (network on Apollo 12, 14, 15, 16; 1969-1977), priced as "moonquakes / interior".
Channels: interior layers and core (famous); long ringing (dry, cracked crust: our ringing-ground test); deep moonquakes timed by Earth's tides (a predictable monthly quake calendar); shallow moonquakes up to about magnitude 5 tied to young thrust faults (avoid fault scarps when siting; LROC's rolled boulders confirm); thermal moonquakes at every sunrise and sunset, including the Apollo 17 lander's own base creaking (structures will flex and creak daily: fatigue); about 1,700 meteoroid impacts (impact risk rate); deliberately crashed rocket stages (calibration sources); astronaut activity picked up at Apollo 11 (a seismometer is also a microphone for the whole base: footsteps, machines, faults).
Earth mirror: desert rocks crack from daily heating (thermal cracking studies in Mojave and Arizona with acoustic sensors); our big-swing sites (Chad, Tibet) are the test beds for daily structural creaking. Fibre-optic cables used as seismic sensors (distributed acoustic sensing) already hear footsteps, vehicles and quakes along telecom lines: a borrowed sense for a base-wide nervous system. Tidally timed tremor on the San Andreas near Parkfield is Earth's version of deep moonquakes. Quiet bedrock for testing: our seismic-quiet and ringing-ground layers.
#16 Apollo heat-flow experiments (Apollo 15 and 17 probes in drilled holes; Apollo 16's cable was snapped when an astronaut tripped on it), priced as "heat from the interior".
Channels: heat leaking from inside (interior make-up); a steady temperature about a metre down while the surface swings hundreds of degrees (bury habitats, batteries and electronics there); very low conductivity of the soil (regolith as insulation); the subsurface slowly warmed after the astronauts walked around, because disturbed, darker soil absorbed more sunlight (found in recovered 1970s tapes): a base changes its own ground temperature, which matters next to ice; drills that jammed in dense soil below the top layer (drilling mechanics); the tripped cable (spacesuit and cable design); tapes lost for decades and recovered (keeping data alive).
Earth mirror: Coober Pedy, South Australia: an opal-mining town where many people live in dugouts cut into the rock to escape the desert heat, a working example of mining, construction and thermal life support in one (also Matmata in Tunisia). Disturbance changing ground temperature: vehicle tracks and seismic survey lines on Arctic tundra thaw permafrost for decades, the Earth version of a base warming the soil near ice.
#17 CRaTER (LRO radiation telescope with tissue-equivalent plastic), priced as "radiation dose": dose rate in lunar orbit; particle energy deposited behind body-like plastic (what tissue under shielding gets); solar storm events (frequency and shape for warnings); protons coming UP from the lunar soil (the ground is itself a radiation source, and the yield depends on hydrogen: another water channel); a decade-plus trend through weak solar cycles (higher cosmic rays than planned); plastic aging under radiation.
Earth mirror: airline dosimetry on polar routes; ground neutron monitors (global network, mountain stations such as Jungfraujoch) that catch solar-storm spikes, the storm-warning analog; our highest-cosmic-ray layer (Pamir, Tibet). Honest gap: Earth's surface dose is far lower.
#18 Lunar Prospector magnetometer and electron reflectometer, priced as "magnetic anomaly map": crustal anomalies; electrons bouncing off small magnetic bubbles that deflect the solar wind (swirls, partial shelters); the Moon's response when it passes through Earth's magnetic tail (interior conductivity, core size); anomalies opposite giant basins (impact physics); no global field (no compass navigation).
Earth mirror: Earth anomaly maps (NOAA EMAG2, used in Umbra; ESA Swarm). Strongest crustal anomalies: Kursk (Russia, iron ore, compasses deviate) and Bangui (Central African Republic, Africa's largest, possibly impact-related), just south of Chad. Compass-free navigation tests.
#19 LADEE (2013-14) and ARTEMIS (two THEMIS probes moved to lunar orbit, 2011-), priced as "the thin atmosphere": sodium, potassium, helium, argon; a permanent lopsided dust cloud from meteoroid impacts that thickens in meteor showers (dust hazard); meteoroid streams releasing water from about 8 cm down under a dry layer (a buried hydrated layer); LADEE carried NASA's Lunar Laser Communication Demonstration (high-rate laser link from the Moon); ARTEMIS: the Moon spends several days a month inside Earth's magnetic tail, where the night side can charge to high voltages (dust and electronics hazard); the plasma wake behind the Moon.
Earth mirror: dust storms build strong electric fields (Sahara and Gobi field studies), our dust-devil sites; optical ground stations at dry sites (LLCD used Table Mountain, California, and White Sands); dry-over-moist desert soil (Atacama) for the buried hydrated layer.
#20 Apollo laser reflectors (Apollo 11, 14, 15 plus two Soviet Lunokhods), priced as "Earth-Moon distance": millimetre ranging; the Moon receding about 3.8 cm a year (tidal history); tests of general relativity; a liquid core from the Moon's wobble; Earth's own rotation and crust motion at the stations; returns are about ten times weaker than in the 1970s and drop further at full moon, consistent with dust coating the optics (50 years of dust on a surface = optics and panel soiling rate); a passive instrument still working after 55 years.
Earth mirror: satellite laser ranging to reflector satellites (LAGEOS, ILRS network); optics and panel soiling in desert solar plants (Atacama, Sahara), our dirty-panel layer.
#21 Commercial Lunar Payload Services landers (2024-), priced as "deliveries": Intuitive Machines IM-1 (Feb 2024, south polar, tipped; its laser rangefinders could not be used, NASA's lidar payload stepped in) and IM-2 (Mar 2025, near Mons Mouton, tipped; drill, mass spectrometer and a Nokia 4G network demo aboard) = landing in low sun and on slopes; Firefly Blue Ghost 1 (Mar 2025, Mare Crisium, full mission): heat-flow drill to about 1 m, GPS signals received at the Moon (LuGRE), cameras filming plume-surface interaction (SCALPSS), a working electrodynamic dust shield, regolith-adhesion tests on materials, X-ray images of Earth's magnetosphere from the Moon (LEXI: the Moon as an Earth observatory), magnetotelluric sounding, a radiation-tolerant computer, a next-generation laser reflector.
Earth mirror: plume filming = desert rocket pads (Van Horn); dust shields and adhesion = desert solar farms; GPS where satellites sit low in the sky and signals are weak = high-latitude and deep-canyon sites; private LTE networks running autonomous trucks in Pilbara iron mines (Western Australia) = the lunar robotic mining and comms system analog (Pilbara is known for stromatolites, not this).

# Team Forced Futures: NASA Space Apps 2026 submission text

Challenge: Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars
Team: Forced Futures (Dan Mistretta)
Project: Umbra

---

## 1. Project Name

Umbra: Mapping Where Earth Can and Cannot Stand In for the Moon

## 2. High-Level Project Summary

No place on Earth is the Moon or Mars, so Umbra stops asking which place looks most like them. It lets real NASA lunar and Mars orbiter data set each condition a base, robot or crew must survive, then scores every 18 km of Earth's land for each one: 36 tests mapped worldwide, from cosmic radiation and two-week nights down to lava tubes, salt that preserves life traces and soil that destroys organic molecules, plus 15 more dimensions named with their status so nothing is dropped. Three lenses no analog list uses drive it. Ratios: like a wind tunnel, it matches the numbers that govern a process, not the scenery. Erasers: it maps where water, life, earthquakes and people stop erasing Earth's record; 67% of 31,085 meteorite finds in NASA's catalogue fall in the top quarter of that map, against 25% by chance. Breadcrumbs: each world keeps records the other lost. Without being told, the engine found known analogs (ESA's Lanzarote lava tubes, Apollo's Pinacate training field, Qaidam, Axel Heiberg) and new ones: northern Chad covers nine tests in one trip, western Tibet eight and Saudi Arabia's lava fields seven, while northern Ellesmere around Eureka Sound covers six winter tests, including the two-week lunar night. A 1 km profile of western Tibet then names three spots within reach of a road, with what carries over and what does not. Every result states what will not carry over and what still needs a test chamber.

## 3. Link to Project Demo

[paste public link to the 7-slide deck: export it to PDF and share from Google Drive, or share the deck link publicly]

## 4. Link to Final Project

[paste the public Umbra Live link (the drag-and-drop dashboard), plus the public GitHub repo link for code and data]

## 5. Detailed Project Description

What it does
Umbra is an analog-site engine and explorer. You pick a Moon test (dust on seals and joints, navigation in low sun, or deep cold) and see a world map of where Earth can stand in, the top regions, how NASA's existing sites score, and which parts of that test no Earth site can cover.

How it works
1. We list what acts on hardware at the lunar south pole all the time: sharp dry dust, low sun with black shadows, deep cold, vacuum, low gravity, radiation.
2. Every 18 km patch of land is scored per test on three things: are the conditions that break the test present, for what share of the year, and what does Earth add that the Moon lacks (water, life, wind, cloud, snow). Score = presence x duration x (1 - Earth penalty).
3. Every score carries its data limits, and conditions Earth cannot reproduce are reported, not dropped.

Results
- Dust (with cold, for seals): Earth can stand in. Top regions are the high cold deserts of the Tibetan Plateau (Qaidam Basin, Changtang, Aksai Chin) and NASA's Arizona and Utah sites.
- Low-sun navigation: barely. Where the sun stays under 7 degrees, the sky is about 60% cloudy and the ground is usually snow-bright. Best regions (Mackenzie Mountains, Verkhoyansk and Chersky ranges, Alaska Range) give roughly 35 to 45 usable days a year.
- Deep cold: about a third at most. Shadowed lunar craters sit near 40 K (about -233 C); Earth's coldest ice-free ground closes 26% of that gap, the Antarctic ice sheet 35%.
- Vacuum, low gravity and space radiation: no Earth site. Chamber or flight only.

New analog types
- Paths and hubs, decided by the Moon: we routed 12,000 random trips across the lunar south pole using only physics (the energy to drive each metre from LOLA slope, divided by the sunlight LOLA says is there). Traffic squeezes into 2% of the ground, with 1.6 times the average sunlight. The strongest hubs form between Shackleton and de Gerlache craters, the same neighbourhood NASA chose for Artemis III candidate regions, without the engine being told where those are. Every hub is within 3.4 km of permanent shadow.
- Exposure analogs, the hidden chemistry: where suits, seals and electronics left outside age the way they will on the Moon and Mars. Ranking NASA POWER UV, MODIS day-night swing, MERRA-2 dust and POWER rainfall together points to the central Sahara (Tibesti and Murzuq) and southern Arabia. Fresh volcanic glass in bone-dry ground, the closest Earth gets to freshly broken lunar dust, points to the Atacama volcanic arc in Chile and Peru.
- Look-alike finder (the tool): in Umbra Live, pick a Moon or Mars fingerprint (for example "Mars dust plain: bright, low thermal inertia" from MGS TES) or click any spot on Earth, and the engine ranks every land cell by how closely it matches across all ticked layers. Any data a user drops in joins the fingerprint automatically, so the algorithm does the matching, not a person. The Mars dust plain fingerprint lands in the central Sahara (Niger, Mauritania, Chad).
- Ringing ground: Apollo seismometers recorded moonquakes that kept ringing for a long time because the lunar crust is bone dry. Dry, bare crystalline shields far from earthquakes (Tibesti, the Reguibat and Arabian shields, Hoggar) are Earth's closest match for testing lunar seismometers and the shaking from landings and mass drivers.
- Six operational analogs, for jobs a crew will actually do: landing-blast ground (Yemen and Saudi Arabia, Tarim Basin), dirty solar panels (Sudan, Chad, Niger), work in the shadows (Yakutia around Ust-Nera, Arctic Canada), radio shadow (Karakoram and Pamir valleys), the walk back (western Tibet, Pamir, the Atacama, matched to the slopes of the Moon's own corridors with LOLA elevation) and oxygen-plant feedstock (Saudi lava fields, Libya's Haruj, Namibia). All six are layers in Umbra Live.
- Underpriced analogs: for every 2 degree block we counted how many of our 43 analog layers it ranks in the top 3% on, then discounted for closeness to the analog sites already studied. Northern Chad (near Faya Largeau) does 11 analog jobs across 6 of the challenge's dimensions, almost 3,000 km from any studied site; the Atacama block does 6. Next come Saudi Arabia's lava fields near At Taif (10 jobs, including lava tubes and oxygen feedstock) and the Aksai Chin edge of the Tibetan Plateau (10).
- System analogs, life support first: Earth systems already living each lunar bottleneck (submarines and mine refuge chambers for sealed air, water-reuse plants for closed water loops, Antarctic greenhouses for calories per watt, SNOLAB for sealed underground living), with Umbra places to stress-test them and what does and does not transfer.

Validation
We scored 11 known analog sites that were never given to the engine. NASA's three lunar field-test sites (Black Point Lava Flow, Meteor Crater, Mars Desert Research Station) land at the 98th to 99th percentile. Low scores are reported with their cause: wet geology-focused sites (Iceland, Svalbard) or data limits (Mauna Kea's 18 km cell averages its wet slopes; soil data is missing for Antarctica and overstated for the Arctic).

Benefits
NASA gets, for each test, a short list of field sites plus the list of risks where no field site helps, so it can spend on field campaigns and test chambers where each actually pays off.

Tools
Python (NumPy, rasterio, matplotlib), HTML/CSS/JavaScript for the explorer page.

Limits and next steps
Dust sharpness is inferred from how the dust formed (dryness, low clay, frost shattering), not measured grain by grain. Cloud and albedo data are 1 degree tiles. Moon and Mars targets now come from real NASA orbiter maps. Next: add Earth visibility to the lunar path model, run the same light-flow on Mars, and find Earth layouts that match the lunar hubs.

## 6. NASA Data

- NASA POWER (Prediction Of Worldwide Energy Resources): monthly climatology of cloud amount (CLOUD_AMT) and all-sky surface albedo (ALLSKY_SRF_ALB), 1 degree, used to test whether low-sun days are clear and dark-ground.
- Lunar Reconnaissance Orbiter (LRO) Diviner Polar Resource Product, south pole (NASA Planetary Data System, Paige/UCLA): annual mean and maximum temperature and depth to stable water ice for 2.26 million cells south of 80S. Used to set the cold, buried-ice and night targets and to measure how far Earth falls short (99% of that ground averages colder than Earth's record low air; buried ice sits under a median 8 cm of dry soil).
- LRO LOLA polar maps (NASA PDS and LOLA team): 40 m slope, 60 m average sunlight and permanent shadow, 85S to pole. Used to set the power-ridge, sun-beside-ice and landing-ground targets (best-lit ground is a median 350 m from permanent shadow, so the engine requires sun and frozen ground in the same cell).
- NASA Engineering and Safety Center study of lunar south pole lighting (Null et al., IAASS 2023): sun never above 7 degrees at Artemis candidate sites, used as the low-sun threshold.
- Apollo regolith grain size (median about 60 to 80 micrometers), used as the dust texture target.

- Mars Global Surveyor MOLA MEGDR topography, 16 pixels per degree (NASA PDS). Converted to surface air pressure: half of Mars has under 624 Pa; Earth's highest bare ground has about 81 times that.
- Mars Global Surveyor TES nightside thermal inertia (Putzig and Mellon 2007) and albedo (NASA PDS). 22% of Mars between 60S and 60N is loose dust, which made the engine add a new test (deep loose dust) that it did not have before.
- Mars Odyssey Gamma Ray Spectrometer water-equivalent hydrogen, 5 degree bins (NASA PDS). Even dry low latitudes hold a median 4% water bound in minerals.

- NASA Meteorite Landings catalogue (data.nasa.gov): used only as an independent check. 67% of 31,085 meteorite finds on land lie in the top quarter of our map of where Earth's natural erasers (water, life, earthquakes) are weakest; chance would give 25%.
- Moon and Mars targets for the new tests: about 300 lunar pits mapped by LRO cameras (Wagner and Robinson), about 640 chloride salt deposits mapped by Mars Odyssey THEMIS (Osterloo et al. 2010), 1,319 marsquakes recorded by InSight, perchlorate found by Phoenix, crustal magnetism mapped by Mars Global Surveyor.

## 7. Space Agency Partner and Other Data

- NASA MODIS Terra land surface temperature (MOD11C3, monthly day and night, 2018 to 2022), read through NASA GIBS: ground temperature, day-night swing and coldest nights for every test that depends on temperature. Covers 99.9% of land.
- NASA POWER precipitation (PRECTOTCORR, MERRA-2 bias-corrected), global: every test that depends on dryness.
- NASA POWER surface UV index (ALLSKY_SFC_UV_INDEX, CERES SYN1deg, 2001 to 2025) and NASA MERRA-2 dust surface mass concentration (monthly, 2018 to 2022, via GIBS): the exposure analogs.
- NASA POWER all-sky surface albedo (ALLSKY_SRF_ALB): with MODIS day-night swing, gives apparent thermal inertia for the orbiter-view fingerprints.
- NASA MERRA-2 total dust deposition (monthly, 2018 to 2022, via GIBS): the dirty-panel analog.
- LRO LOLA polar elevation LDEM_80S_80M (NASA PDS): lunar corridor slopes for the walk-back analog.
- IAU / USGS Gazetteer of Planetary Nomenclature: lunar feature names used to check where the light-flow hubs fall.
- AWS Terrain Tiles (SRTM-based elevation) at zoom 6: slope, horizon and winter shade for the terrain analogs.
- For the western Tibet site profile: NASA MODIS monthly land surface temperature at 0.035 degrees via GIBS, AWS Terrain Tiles (SRTM-based elevation), and Natural Earth roads and lakes.
- WorldClim 2.1: vapor pressure, wind and elevation at 10 arc-minutes, and gap-filling where MODIS has no data.
- SoilGrids 2.0 (ISRIC): sand, silt, clay and organic carbon, 0 to 5 cm, 5 km.
- Natural Earth: glaciated areas and Antarctic ice shelves (public domain).
- Outside check: Xiao et al. (2017), "A new terrestrial analogue site for Mars research: the Qaidam Basin," Earth-Science Reviews 164.

## 8. References

Code: Python with NumPy, SciPy, pandas, rasterio, matplotlib, pyshp and ppigrf; GeoTIFF.js in the live dashboard. All Umbra code was written for this project with AI assistance (see section 9).
Data: listed in sections 6 and 7, plus the USGS/EcoTapestry global lithology map (Sayre et al.), Smithsonian Global Volcanism Program, USGS ComCat earthquake catalogue, NOAA EMAG2v3, Natural Earth, SoilGrids 2.0, WorldClim 2.1, NASA POWER, IGRF, and the Impact Earth database of confirmed impact craters (Western University, Osinski et al. 2022).
Text and facts: Wagner and Robinson (lunar pits); Osterloo et al. 2010 (Mars chlorides); Bellucci et al. 2019 and Warren and Rubin 2020 (Apollo sample 14321); Putzig and Mellon 2007 (Mars thermal inertia); Stewart et al. 2024, PLOS ONE (Umm Jirsan lava tube); ESA PANGAEA (Lanzarote); NASA JPL (Scarecrow rover).
Images: all maps and charts were generated by our code from the data above. No third-party images are used.

## 9. Use of Artificial Intelligence

We used Claude (Anthropic) as an AI assistant. It wrote the analysis code, generated the maps and charts, and drafted the explorer page, slides and project text, under the team's direction. The team defined the approach (the scoring method and the order in which a base gets built), chose the tests and checked the results. Every map and chart carries a visible label stating it was computed with AI-assisted code. No NASA logos or mission branding are used.

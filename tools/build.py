#!/usr/bin/env python3
"""Build SmokeTrail.

    python tools/build.py              -> writes index.html at the repository root
    python tools/build.py --artifact X -> also writes a body-only page to X

Edit the story in src/page.html and the bibliography in REFS below.
Citations are written {{c:key}} or {{c:key1,key2}}; they are numbered in
order of first appearance and the reference list is generated.
Charts are written {{chart:name}} and defined in CHARTS below.
"""
import html
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import scene  # noqa: E402

VERSION = "0.1.0"
DATE = "12 November 2026"

# key: (authors, year, title, venue, url, note)
REFS = {
    "sg2010": ("U.S. Department of Health and Human Services", 2010, "How Tobacco Smoke Causes Disease: The Biology and Behavioral Basis for Smoking-Attributable Disease. A Report of the Surgeon General", "Chapter 3: Chemistry and Toxicology of Cigarette Smoke and Biomarkers of Exposure and Harm", "https://www.ncbi.nlm.nih.gov/books/NBK53014/", ""),
    "baker1974": ("Baker R.R.", 1974, "Temperature distribution inside a burning cigarette", "Nature 247:405–406", "https://doi.org/10.1038/247405a0", ""),
    "nrc1986": ("National Research Council", 1986, "Environmental Tobacco Smoke: Measuring Exposures and Assessing Health Effects", "National Academies Press, Washington DC", "https://doi.org/10.17226/943", ""),
    "lihecht2022": ("Li Y., Hecht S.S.", 2022, "Carcinogenic components of tobacco and tobacco smoke: a 2022 update", "Food and Chemical Toxicology 165:113179", "https://doi.org/10.1016/j.fct.2022.113179", ""),
    "iarc83": ("International Agency for Research on Cancer", 2004, "Tobacco Smoke and Involuntary Smoking", "IARC Monographs on the Evaluation of Carcinogenic Risks to Humans, Vol. 83", "https://publications.iarc.who.int/Book-And-Report-Series/Iarc-Monographs-On-The-Identification-Of-Carcinogenic-Hazards-To-Humans/Tobacco-Smoke-And-Involuntary-Smoking-2004", "Sidestream yields: Table 1.3."),
    "iarc100e": ("International Agency for Research on Cancer", 2012, "Personal Habits and Indoor Combustions", "IARC Monographs Vol. 100E", "https://www.ncbi.nlm.nih.gov/books/NBK304391/", ""),
    "zacny1996": ("Zacny J.P., Stitzer M.L.", 1996, "Human smoking patterns", "In: The FTC Cigarette Test Method for Determining Tar, Nicotine, and Carbon Monoxide Yields of U.S. Cigarettes. NCI Smoking and Tobacco Control Monograph 7, Chapter 11", "https://cancercontrol.cancer.gov/Brp/TCRB/monographs/7/m7_11.pdf", ""),
    "hammond2007": ("Hammond D., et al.", 2007, "Revising the machine smoking regime for cigarette emissions: implications for tobacco control policy", "Tobacco Control 16:8–14", "https://doi.org/10.1136/tc.2005.015297", ""),
    "eu2014": ("European Parliament and Council", 2014, "Directive 2014/40/EU (Tobacco Products Directive)", "Official Journal of the European Union L 127, Article 3", "https://eur-lex.europa.eu/eli/dir/2014/40/oj", ""),
    "bakerdixon2006": ("Baker R.R., Dixon M.", 2006, "The retention of tobacco smoke constituents in the human respiratory tract", "Inhalation Toxicology 18:255–294", "https://doi.org/10.1080/08958370500444163", ""),
    "sahu2013": ("Sahu S.K., Tiwari M., Bhangare R.C., Pandit G.G.", 2013, "Particle size distribution of mainstream and exhaled cigarette smoke and predictive deposition in human respiratory tract", "Aerosol and Air Quality Research 13:324–332", "https://doi.org/10.4209/aaqr.2012.02.0041", ""),
    "epa1992": ("U.S. Environmental Protection Agency", 1992, "Respiratory Health Effects of Passive Smoking: Lung Cancer and Other Disorders", "EPA/600/6-90/006F", "https://www.epa.gov/sites/default/files/2014-09/documents/passive_smoke.pdf", ""),
    "bakerproctor1990": ("Baker R.R., Proctor C.J.", 1990, "The origins and properties of environmental tobacco smoke", "Environment International 16:231–245", "https://doi.org/10.1016/0160-4120(90)90117-O", ""),
    "ota1986": ("U.S. Congress, Office of Technology Assessment", 1986, "Passive Smoking in the Workplace: Selected Issues", "OTA staff paper", "https://www.princeton.edu/~ota/disk2/1986/8617/861705.PDF", ""),
    "klepeis2007": ("Klepeis N.E., Ott W.R., Switzer P.", 2007, "Real-time measurement of outdoor tobacco smoke particles", "Journal of the Air & Waste Management Association 57:522–534", "https://doi.org/10.3155/1047-3289.57.5.522", ""),
    "hwang2014": ("Hwang J., Lee K.", 2014, "Determination of outdoor tobacco smoke exposure by distance from a smoking source", "Nicotine & Tobacco Research 16:478–484", "https://doi.org/10.1093/ntr/ntt178", ""),
    "who2021aqg": ("World Health Organization", 2021, "WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide", "WHO, Geneva", "https://www.who.int/publications/i/item/9789240034228", ""),
    "hyland2008": ("Hyland A., et al.", 2008, "A 32-country comparison of tobacco smoke derived particle levels in indoor public places", "Tobacco Control 17:159–165", "https://doi.org/10.1136/tc.2007.020479", ""),
    "semple2015": ("Semple S., et al.", 2015, "Fine particulate matter concentrations in smoking households: just how much secondhand smoke do you breathe in if you live with a smoker who smokes indoors?", "Tobacco Control 24:e205–e211", "https://doi.org/10.1136/tobaccocontrol-2014-051635", ""),
    "borduas2016": ("Borduas N., Murphy J.G., Wang C., da Silva G., Abbatt J.P.D.", 2016, "Gas phase oxidation of nicotine by OH radicals: kinetics, mechanisms, and formation of HNCO", "Environmental Science & Technology Letters 3:327–331", "https://doi.org/10.1021/acs.estlett.6b00231", ""),
    "aquilina2021": ("Aquilina N.J., Havel C.M., Cheung P., Harrison R.M., Ho K.F., Benowitz N.L., Jacob P. III", 2021, "Ubiquitous atmospheric contamination by tobacco smoke: nicotine and a new marker for tobacco smoke-derived particulate matter, nicotelline", "Environment International 150:106417", "https://doi.org/10.1016/j.envint.2021.106417", ""),
    "kristiansen2016": ("Kristiansen N.I., et al.", 2016, "Evaluation of observed and modelled aerosol lifetimes using radioactive tracers of opportunity and an ensemble of 19 global models", "Atmospheric Chemistry and Physics 16:3525–3561", "https://doi.org/10.5194/acp-16-3525-2016", ""),
    "rogge1994": ("Rogge W.F., Hildemann L.M., Mazurek M.A., Cass G.R., Simoneit B.R.T.", 1994, "Sources of fine organic aerosol. 6. Cigaret smoke in the urban atmosphere", "Environmental Science & Technology 28:1375–1388", "https://doi.org/10.1021/es00056a030", ""),
    "wang2010": ("Wang X., Zhang L., Moran M.D.", 2010, "Uncertainty assessment of current size-resolved parameterizations for below-cloud particle scavenging by rain", "Atmospheric Chemistry and Physics 10:5685–5705", "https://doi.org/10.5194/acp-10-5685-2010", ""),
    "clayton2013": ("Clayton P.M., et al.", 2013, "Spectroscopic investigations into the acid–base properties of nicotine at different temperatures", "Analytical Methods 5:81–88", "https://doi.org/10.1039/c2ay25678a", ""),
    "sander2023": ("Sander R.", 2023, "Compilation of Henry's law constants (version 5.0.0) for water as solvent", "Atmospheric Chemistry and Physics 23:10901–12440", "https://doi.org/10.5194/acp-23-10901-2023", "Entry for nicotine: https://www.henrys-law.org/henry/casrn/54-11-5"),
    "bpdb": ("University of Hertfordshire", 2026, "Nicotine", "BPDB: Bio-Pesticides DataBase (accessed November 2026)", "https://sitem.herts.ac.uk/aeru/bpdb/Reports/485.htm", "Database values; Koc and soil half-life are marked as estimates there."),
    "venohr2025": ("Venohr M., et al.", 2025, "Spatial distribution of nicotine concentrations in Berlin's surface waters and their potential sources", "Environmental Science and Pollution Research 32:6784–6803", "https://doi.org/10.1007/s11356-025-36124-w", ""),
    "winickoff2009": ("Winickoff J.P., Friebely J., Tanski S.E., Sherrod C., Matt G.E., Hovell M.F., McMillen R.C.", 2009, "Beliefs about the health effects of \"thirdhand\" smoke and home smoking bans", "Pediatrics 123:e74–e79", "https://doi.org/10.1542/peds.2008-2184", ""),
    "singer2004": ("Singer B.C., Revzan K.L., Hotchi T., Hodgson A.T., Brown N.J.", 2004, "Sorption of organic gases in a furnished room", "Atmospheric Environment 38:2483–2494", "https://doi.org/10.1016/j.atmosenv.2004.02.003", ""),
    "singer2002": ("Singer B.C., Hodgson A.T., Guevarra K.S., Hawley E.L., Nazaroff W.W.", 2002, "Gas-phase organics in environmental tobacco smoke. 1. Effects of smoking rate, ventilation, and furnishing level on emission factors", "Environmental Science & Technology 36:846–853", "https://doi.org/10.1021/es011058w", ""),
    "singer2003": ("Singer B.C., Hodgson A.T., Nazaroff W.W.", 2003, "Gas-phase organics in environmental tobacco smoke: 2. Exposure-relevant emission factors and indirect exposures from habitual smoking", "Atmospheric Environment 37:5551–5561", "https://doi.org/10.1016/j.atmosenv.2003.07.015", ""),
    "sleiman2010": ("Sleiman M., Gundel L.A., Pankow J.F., Jacob P. III, Singer B.C., Destaillats H.", 2010, "Formation of carcinogens indoors by surface-mediated reactions of nicotine with nitrous acid, leading to potential thirdhand smoke hazards", "Proceedings of the National Academy of Sciences 107:6576–6581", "https://doi.org/10.1073/pnas.0912820107", ""),
    "sleiman2010b": ("Sleiman M., Destaillats H., Smith J.D., et al.", 2010, "Secondary organic aerosol formation from ozone-initiated reactions with nicotine and secondhand tobacco smoke", "Atmospheric Environment 44:4191–4198", "https://doi.org/10.1016/j.atmosenv.2010.07.023", ""),
    "destaillats2006": ("Destaillats H., Singer B.C., Lee S.K., Gundel L.A.", 2006, "Effect of ozone on nicotine desorption from model surfaces: evidence for heterogeneous chemistry", "Environmental Science & Technology 40:1799–1805", "https://doi.org/10.1021/es050914r", ""),
    "matt2011": ("Matt G.E., Quintana P.J.E., Zakarian J.M., et al.", 2011, "When smokers move out and non-smokers move in: residential thirdhand smoke pollution and exposure", "Tobacco Control 20:e1", "https://doi.org/10.1136/tc.2010.037382", ""),
    "matt2018": ("Matt G.E., Quintana P.J.E., Hoh E., et al.", 2018, "A casino goes smoke free: a longitudinal study of secondhand and thirdhand smoke pollution and exposure", "Tobacco Control 27:643–649", "https://doi.org/10.1136/tobaccocontrol-2017-054052", ""),
    "matt2004": ("Matt G.E., Quintana P.J.E., Hovell M.F., et al.", 2004, "Households contaminated by environmental tobacco smoke: sources of infant exposures", "Tobacco Control 13:29–37", "https://doi.org/10.1136/tc.2003.003889", ""),
    "hang2013": ("Hang B., Sarker A.H., Havel C., et al.", 2013, "Thirdhand smoke causes DNA damage in human cells", "Mutagenesis 28:381–391", "https://doi.org/10.1093/mutage/get013", ""),
    "ramirez2014": ("Ramírez N., Özel M.Z., Lewis A.C., Marcé R.M., Borrull F., Hamilton J.F.", 2014, "Exposure to nitrosamines in thirdhand tobacco smoke increases cancer risk in non-smokers", "Environment International, pp. 139–147", "https://doi.org/10.1016/j.envint.2014.06.012", ""),
    "bertone2002": ("Bertone E.R., Snyder L.A., Moore A.S.", 2002, "Environmental tobacco smoke and risk of malignant lymphoma in pet cats", "American Journal of Epidemiology 156", "https://doi.org/10.1093/aje/kwf044", ""),
    "sheu2020": ("Sheu R., Stönner C., Ditto J.C., Klüpfel T., Williams J., Gentner D.R.", 2020, "Human transport of thirdhand tobacco smoke: a prominent source of hazardous air pollutants into indoor nonsmoking environments", "Science Advances 6:eaay4109", "https://doi.org/10.1126/sciadv.aay4109", ""),
    "beko2017": ("Bekö G., Morrison G., Weschler C.J., et al.", 2017, "Measurements of dermal uptake of nicotine directly from air and clothing", "Indoor Air 27:427–433", "https://doi.org/10.1111/ina.12327", ""),
    "beko2018": ("Bekö G., et al.", 2018, "Dermal uptake of nicotine from air and clothing: experimental verification", "Indoor Air 28:247–257", "https://doi.org/10.1111/ina.12437", ""),
    "bahl2014": ("Bahl V., Jacob P. III, Havel C., Schick S.F., Talbot P.", 2014, "Thirdhand cigarette smoke: factors affecting exposure and remediation", "PLoS ONE 9:e108258", "https://doi.org/10.1371/journal.pone.0108258", ""),
    "northrup2022": ("Northrup T.F., et al.", 2022, "Handwashing results in incomplete nicotine removal from fingers of individuals who smoke: a randomized controlled experiment", "American Journal of Perinatology 39:1634–1642", "https://doi.org/10.1055/s-0041-1736287", ""),
    "aldelaimy2002": ("Al-Delaimy W.K., Crane J., Woodward A.", 2003, "Passive smoking, as measured by hair nicotine, and severity of acute lower respiratory illnesses among children", "Tobacco Induced Diseases 1:27", "https://doi.org/10.1186/1617-9625-1-1-27", ""),
    "sg2006": ("U.S. Department of Health and Human Services", 2006, "The Health Consequences of Involuntary Exposure to Tobacco Smoke: A Report of the Surgeon General", "Atlanta: CDC", "https://www.ncbi.nlm.nih.gov/books/NBK44324/", ""),
    "cdc_shs": ("Centers for Disease Control and Prevention", 2026, "Health problems caused by secondhand smoke", "Summary of the 2006 and 2014 Surgeon General reports (accessed November 2026)", "https://www.cdc.gov/tobacco/secondhand-smoke/health.html", ""),
    "who2026": ("World Health Organization", 2026, "Tobacco", "Fact sheet, 26 June 2026", "https://www.who.int/news-room/fact-sheets/detail/tobacco", ""),
    "oberg2011": ("Öberg M., Jaakkola M.S., Woodward A., Peruga A., Prüss-Ustün A.", 2011, "Worldwide burden of disease from exposure to second-hand smoke: a retrospective analysis of data from 192 countries", "The Lancet 377:139–146", "https://doi.org/10.1016/S0140-6736(10)61388-8", ""),
    "who2022": ("World Health Organization", 2022, "Tobacco: poisoning our planet", "WHO, Geneva", "https://www.who.int/publications/i/item/9789240051287", ""),
    "zafeiridou2018": ("Zafeiridou M., Hopkinson N.S., Voulvoulis N.", 2018, "Cigarette smoking: an assessment of tobacco's global environmental footprint across its entire supply chain", "Environmental Science & Technology 52:8087–8094", "https://doi.org/10.1021/acs.est.8b01533", ""),
    "novotny2009": ("Novotny T.E., Lum K., Smith E., Wang V., Barnes R.", 2009, "Cigarettes butts and the case for an environmental policy on hazardous cigarette waste", "International Journal of Environmental Research and Public Health 6:1691–1705", "https://doi.org/10.3390/ijerph6051691", ""),
    "novotny2014": ("Novotny T.E., Slaughter E.", 2014, "Tobacco product waste: an environmental approach to reduce tobacco consumption", "Current Environmental Health Reports 1:208–216", "https://doi.org/10.1007/s40572-014-0016-x", ""),
    "nitschke2023": ("Nitschke T., et al.", 2023, "Smokers' behaviour and the toxicity of cigarette filters to aquatic life: a multidisciplinary study", "Microplastics and Nanoplastics 3:1", "https://doi.org/10.1186/s43591-022-00050-2", ""),
    "green2023": ("Green D.S., Almroth B.C., Altman R., et al.", 2023, "Time to kick the butt of the most common litter item in the world: ban cigarette filters", "Science of the Total Environment 865:161256", "https://doi.org/10.1016/j.scitotenv.2022.161256", ""),
    "joly2018": ("Joly F.-X., Coulis M.", 2018, "Comparison of cellulose vs. plastic cigarette filter decomposition under distinct disposal environments", "Waste Management 72:349–353", "https://doi.org/10.1016/j.wasman.2017.11.023", ""),
    "bonanomi2015": ("Bonanomi G., et al.", 2015, "Cigarette butt decomposition and associated chemical changes assessed by 13C CPMAS NMR", "PLoS ONE 10:e0117393", "https://doi.org/10.1371/journal.pone.0117393", ""),
    "moerman2011": ("Moerman J.W., Potts G.E.", 2011, "Analysis of metals leached from smoked cigarette litter", "Tobacco Control 20(Suppl 1):i30–i35", "https://doi.org/10.1136/tc.2010.040196", ""),
    "slaughter2011": ("Slaughter E., Gersberg R.M., Watanabe K., Rudolph J., Stransky C., Novotny T.E.", 2011, "Toxicity of cigarette butts, and their chemical components, to marine and freshwater fish", "Tobacco Control 20(Suppl 1):i25–i29", "https://doi.org/10.1136/tc.2010.040170", ""),
    "rodergreen2014": ("Roder Green A.L., Putschew A., Nehls T.", 2014, "Littered cigarette butts as a source of nicotine in urban waters", "Journal of Hydrology 519:3466–3474", "https://doi.org/10.1016/j.jhydrol.2014.05.046", ""),
    "igb2025": ("Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB)", 2025, "Nicotine in Berlin's waters", "Press release, Forschungsverbund Berlin", "https://www.fv-berlin.de/en/info-for/the-media-and-public/news/nicotine-in-berlins-waters", ""),
    "dobaradaran2020": ("Dobaradaran S., et al.", 2020, "Polycyclic aromatic hydrocarbons (PAHs) leachates from cigarette butts into water", "Environmental Pollution 259:113916", "https://doi.org/10.1016/j.envpol.2020.113916", ""),
    "oekotox2019": ("Oekotoxzentrum (Swiss Centre for Applied Ecotoxicology)", 2019, "Zigarettenstummel", "Info sheet", "https://www.oekotoxzentrum.ch/media/194897/2019_zigarettenstummel_de.pdf", ""),
    "green2019": ("Green D.S., Boots B., Da Silva Carvalho J., Starkey T.", 2019, "Cigarette butts have adverse effects on initial growth of perennial ryegrass (gramineae: Lolium perenne L.) and white clover (leguminosae: Trifolium repens L.)", "Ecotoxicology and Environmental Safety 182:109418", "https://doi.org/10.1016/j.ecoenv.2019.109418", "Percentages as reported in press coverage of the study."),
    "selmar2018": ("Selmar D., et al.", 2018, "Uptake of nicotine from discarded cigarette butts: a so far unconsidered path of contamination of plant-derived commodities", "Environmental Pollution 238:972–976", "https://doi.org/10.1016/j.envpol.2018.01.113", ""),
    "selmar2015": ("Selmar D., et al.", 2015, "Nicotine uptake by peppermint plants as a possible source of nicotine in plant-derived products", "Agronomy for Sustainable Development 35:1185–1190", "https://doi.org/10.1007/s13593-015-0298-x", ""),
    "eu2023mrl": ("European Commission", 2023, "Commission Regulation (EU) 2023/1536 amending Annexes II and V to Regulation (EC) No 396/2005 as regards maximum residue levels for nicotine", "Official Journal of the European Union", "https://eur-lex.europa.eu/eli/reg/2023/1536/oj", ""),
    "seckar2008": ("Seckar J.A., et al.", 2008, "Environmental fate and effects of nicotine released during cigarette production", "Environmental Toxicology and Chemistry 27:1505–1514", "https://doi.org/10.1897/07-284.1", "Authors affiliated with the tobacco industry."),
    "buerge2008": ("Buerge I.J., Kahle M., Buser H.-R., Müller M.D., Poiger T.", 2008, "Nicotine derivatives in wastewater and surface waters: application as chemical markers for domestic wastewater", "Environmental Science & Technology 42:6354–6360", "https://doi.org/10.1021/es800455q", ""),
    "godfrey2007": ("Godfrey E., Woessner W.W., Benotti M.J.", 2007, "Pharmaceuticals in on-site sewage effluent and ground water, Western Montana", "Ground Water 45:263–271", "https://doi.org/10.1111/j.1745-6584.2006.00288.x", ""),
    "kozikowski2024": ("Kozikowski N., Corcoran P.L.", 2024, "Pedestrian traffic is the main driver of macro- and large microplastic debris deposition in urban stormwater drains", "Frontiers in Environmental Science 12:1459259", "https://doi.org/10.3389/fenvs.2024.1459259", ""),
    "bfs2023": ("Federal Statistical Office (FSO)", 2023, "Swiss Health Survey 2022", "Press release, 3 November 2023", "https://www.admin.ch/gov/de/start/dokumentation/medienmitteilungen.msg-id-98449.html", ""),
    "bazg2025": ("Federal Office for Customs and Border Security (FOCBS)", 2025, "Zusätzliche Finanzierungsquelle für die AHV über die Tabaksteuer", "Report, 27 February 2025", "https://www.parlament.ch/centers/documents/de/Bericht%2520BAZG%252027.02.25%2520Zus%C3%A4tzliche%2520Finanzierungsquelle%2520f%C3%BCr%2520die%2520AHV%2520%C3%BCber%2520die%2520Tabaksteuer.pdf", ""),
    "obsan_mort": ("Swiss Health Observatory (Obsan), MonAM", 2026, "Tobacco-attributable mortality", "Indicator, updated 27 January 2026", "https://ind.obsan.admin.ch/en/indicator/monam/tobacco-attributable-mortality", ""),
    "obsan_shs": ("Swiss Health Observatory (Obsan), MonAM", 2026, "Passivrauchen (Alter: 15+)", "Indicator (accessed November 2026)", "https://ind.obsan.admin.ch/de/indicator/monam/passivrauchen-alter-15", ""),
    "sr81831": ("Swiss Confederation", 2008, "Bundesgesetz zum Schutz vor Passivrauchen (SR 818.31)", "In force since 1 May 2010", "https://www.lexfind.ch/tolv/198595/de", ""),
    "vicedo2016": ("Vicedo-Cabrera A.M., et al.", 2016, "Benefits of smoking bans on preterm and early-term births: a natural experimental design in Switzerland", "Tobacco Control 25:e135–e141", "https://doi.org/10.1136/tobaccocontrol-2015-052739", ""),
    "vicedo2016b": ("Vicedo-Cabrera A.M., et al.", 2016, "Cardiorespiratory hospitalisation and mortality reductions after smoking bans in Switzerland", "Swiss Medical Weekly 146:w14381", "https://doi.org/10.4414/smw.2016.14381", ""),
    "bonetti2011": ("Bonetti P.O., et al.", 2011, "Incidence of acute myocardial infarction after implementation of a public smoking ban in Graubünden, Switzerland: two year follow-up", "Swiss Medical Weekly 141:w13206", "https://doi.org/10.4414/smw.2011.13206", ""),
    "bafu2011": ("Berger T., Sommerhalder M.", 2011, "Littering kostet. Fraktionsspezifische Reinigungskosten durch Littering in der Schweiz", "Umwelt-Wissen Nr. 1108, Federal Office for the Environment (FOEN)", "https://www.bafu.admin.ch/dam/bafu/de/dokumente/abfall/uw-umwelt-wissen/littering_kostet.pdf.download.pdf/littering_kostet.pdf", "Cost data for 2010."),
    "iqaasl": ("Federal Office for the Environment (FOEN)", 2021, "Waste along Swiss rivers and lakes (IQAASL survey 2020–2021)", "FOEN", "https://www.bafu.admin.ch/en/waste-along-swiss-rivers-and-lakes", "Lake Geneva figures: https://hammerdirt-analyst.github.io/IQAASL-End-0f-Sampling-2021/lac-leman.html"),
    "bafu_fine": ("Federal Office for the Environment (FOEN)", 2026, "Faktenblatt: Schweizweit einheitliche Littering-Busse", "Fact sheet", "https://www.bafu.admin.ch/dam/de/sd-web/VaJjizZsf40B/Faktenblatt%20Abfall%20-%20Schweizweit%20einheitliche%20Littering-Busse.pdf", ""),
    "hanke2016": ("Hanke G.", 2016, "Marine Beach Litter in Europe – Top Items", "JRC Technical Report JRC103929, European Commission Joint Research Centre", "https://mcc.jrc.ec.europa.eu/documents/Marine_Litter/MarineLitterTOPitems_final_24.1.2017.pdf", ""),
}

# ------------------------------------------------------------------ charts

def pct(v, lo, hi, log=False):
    if log:
        return (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * 100
    return (v - lo) / (hi - lo) * 100


def rows_chart(title, sub, rows, lo, hi, ticks, log=False, refs=None, legend="", wide=False):
    """rows: (label, a, b, valuetext, colorvar or None). a==b -> point."""
    out = [f'<figure class="chart{" wide" if wide else ""}"><h3>{title}</h3>']
    if sub:
        out.append(f'<p class="sub">{sub}</p>')
    out.append('<div class="rows">')
    for (label, a, b, vt, c) in rows:
        style = f' style="--c:var(--{c})"' if c else ''
        out.append(f'<div class="rb"{style}><span class="k">{label}</span><span class="track">')
        if refs:
            for rv in refs:
                out.append(f'<span class="ref" style="left:{pct(rv, lo, hi, log):.2f}%"></span>')
        if a == b:
            out.append(f'<span class="pt" style="left:{pct(a, lo, hi, log):.2f}%"></span>')
        else:
            l, r = pct(a, lo, hi, log), pct(b, lo, hi, log)
            out.append(f'<span class="fill" style="left:{l:.2f}%;width:{max(r-l,1.2):.2f}%"></span>')
        out.append(f'</span><span class="v">{vt}</span></div>')
    out.append('</div>')
    out.append('<div class="axis-row"><span class="sp"></span><span class="ticks">' + ''.join(
        f'<span style="left:{pct(v, lo, hi, log):.2f}%">{t}</span>' for v, t in ticks) + '</span><span class="sp"></span></div>')
    if legend:
        out.append(f'<p class="legend">{legend}</p>')
    out.append('</figure>')
    return '\n'.join(out)


def bars_from_zero(title, sub, rows, hi, ticks, refs=None, legend=""):
    return rows_chart(title, sub, [(l, 0, v, t, c) for (l, v, t, c) in rows], 0, hi, ticks, refs=refs, legend=legend)


CHARTS = {}

CHARTS["temp"] = ('<figure class="chart tscale"><h3>Temperatures in and around the coal</h3>'
                  '<div class="bar">'
                  f'<span class="mk dn" style="left:{350/12:.2f}%"><span>350</span></span>'
                  f'<span class="mk up" style="left:{400/12:.2f}%"><span>400</span></span>'
                  f'<span class="mk rng dn" style="left:{700/12:.2f}%;width:{100/12:.2f}%"><span>700–800</span></span>'
                  f'<span class="mk up" style="left:{900/12:.2f}%"><span>900</span></span>'
                  f'<span class="mk dn end" style="left:99.4%"><span>1,200 °C</span></span>'
                  '</div><ul>'
                  '<li><b>350 °C</b>: sidestream smoke as it leaves the cigarette {{c:nrc1986}}</li>'
                  '<li><b>400 °C</b>: coal between puffs {{c:sg2010}}</li>'
                  '<li><b>700–800 °C</b>: coal centre while smouldering, thermocouple {{c:baker1974}}</li>'
                  '<li><b>900 °C</b>: coal during a puff {{c:sg2010}}</li>'
                  '<li><b>1,200 °C</b>: brief hot spots {{c:baker1974}}</li></ul></figure>')

CHARTS["retention"] = rows_chart(
    "Share retained in a smoker's airways", "Per inhaled puff of mainstream smoke {{c:bakerdixon2006}}",
    [("Nicotine", 90, 100, "90–100%", None), ("Aldehydes", 90, 90, "≈90%", None),
     ("Particulate matter", 60, 80, "60–80%", None), ("Carbon monoxide", 55, 65, "55–65%", None)],
    0, 100, [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")])

CHARTS["ratio"] = rows_chart(
    "Sidestream vs mainstream, per cigarette", "Ratio of the amount released into the air to the amount the smoker draws in (non-filter cigarettes) {{c:nrc1986}}",
    [("Nicotine", 2.6, 3.3, "2.6–3.3×", None), ("Carbon monoxide", 2.5, 4.7, "2.5–4.7×", None),
     ("Benzo[a]pyrene", 2.5, 3.5, "2.5–3.5×", None), ("Benzene", 5, 10, "5–10×", None),
     ("NDMA (nitrosamine)", 20, 100, "20–100×", None), ("Ammonia", 40, 170, "40–170×", None)],
    1, 200, [(1, "1×"), (10, "10×"), (100, "100×")], log=True, refs=[1],
    legend='<span><i></i>1× = equal amounts</span><span>Log scale</span>')

CHARTS["distance"] = bars_from_zero(
    "PM2.5 added by one outdoor smoker", "Measured downwind, above background {{c:hwang2014}}",
    [("1 m", 72.7, "72.7 µg/m³", None), ("3 m", 11.3, "11.3 µg/m³", None), ("6 m", 4.1, "4.1 µg/m³", None), ("9 m", 2.6, "2.6 µg/m³", None)],
    80, [(0, "0"), (20, "20"), (40, "40"), (60, "60"), (80, "80 µg/m³")], refs=[15],
    legend='<span><i></i>15 µg/m³: WHO guideline for a 24-hour average {{c:who2021aqg}}, shown for scale only</span>')

CHARTS["scav"] = rows_chart(
    "How fast rain removes particles", "Observed below-cloud scavenging coefficient by particle size {{c:wang2010}}",
    [("&lt; 0.01 µm", 1e-4, 1e-4, "≈1×10⁻⁴ s⁻¹", "rain"), ("0.1–1 µm (smoke)", 1e-5, 1e-5, "≈1×10⁻⁵ s⁻¹", "ember"),
     ("3.5–10 µm", 1e-4, 3e-4, "1–3×10⁻⁴ s⁻¹", "rain")],
    1e-6, 1e-3, [(1e-6, "10⁻⁶"), (1e-5, "10⁻⁵"), (1e-4, "10⁻⁴"), (1e-3, "10⁻³ s⁻¹")], log=True,
    legend='<span>Log scale. Higher means faster removal.</span>')

CHARTS["dermal"] = bars_from_zero(
    "Nicotine taken up through the skin in 3 hours", "Volunteers breathed clean air through a hood while sitting in nicotine-laden air (420 µg/m³) {{c:beko2017}}",
    [("Bare skin", 570, "≈570 µg", None), ("Shirt pre-exposed to nicotine", 80, "≈80 µg", None), ("Clean clothes", 20, "≈20 µg", None)],
    600, [(0, "0"), (200, "200"), (400, "400"), (600, "600 µg")])

CHARTS["plants"] = bars_from_zero(
    "Butts in soil, 21-day growth test", "Reduction compared with soil without butts {{c:green2019}}",
    [("Clover: germination", 27, "−27%", "leaf"), ("Clover: shoot length", 28, "−28%", "leaf"), ("Clover: root biomass", 57, "−57%", "leaf"),
     ("Ryegrass: germination", 10, "−10%", "leaf"), ("Ryegrass: shoot length", 13, "−13%", "leaf")],
    60, [(0, "0%"), (20, "−20%"), (40, "−40%"), (60, "−60%")])

CHARTS["water"] = rows_chart(
    "Tobacco compounds in water, and an effect threshold", "Concentrations in ng per litre",
    [("Swiss lakes, cotinine (max.)", 15, 15, "15", "rain"), ("Berlin, nicotine (mean)", 73, 73, "73", "rain"),
     ("Swiss lakes, 3′-OH-cotinine (max.)", 80, 80, "80", "rain"), ("Berlin, nicotine (max.)", 1500, 1500, "≈1,500", "rain"),
     ("Nicotine no-effect level", 2400, 2400, "2,400", "ember"), ("Water flea 48-h EC50", 242000, 242000, "242,000", "ember")],
    1, 1e6, [(1, "1"), (10, "10"), (100, "100"), (1e3, "1k"), (1e4, "10k"), (1e5, "100k"), (1e6, "1M ng/L")], log=True,
    legend='<span>Swiss lakes {{c:buerge2008}} · Berlin {{c:venohr2025}} · threshold {{c:oekotox2019}} · EC50 {{c:bpdb}} · log scale</span>', wide=True)

CHARTS["risk"] = rows_chart(
    "Higher risk in adults who never smoked", "Regular exposure to secondhand smoke {{c:sg2006,cdc_shs}}",
    [("Lung cancer", 20, 30, "+20–30%", None), ("Coronary heart disease", 25, 30, "+25–30%", None), ("Stroke", 20, 30, "+20–30%", None)],
    0, 40, [(0, "0%"), (10, "+10%"), (20, "+20%"), (30, "+30%"), (40, "+40%")])

# ------------------------------------------------------------------ calculator rows

AIR = [  # label, lo, hi (ng per cigarette), basis text
    ("Particulate matter (tar)", 10.5e6, 34.4e6, "10.5–34.4 mg"),
    ("Carbon monoxide", 31.5e6, 54.1e6, "31.5–54.1 mg"),
    ("Nicotine", 1.9e6, 5.3e6, "1.9–5.3 mg"),
    ("Formaldehyde", 540e3, 968e3, "540–968 µg"),
    ("Benzene", 70.7e3, 134.3e3, "70.7–134.3 µg"),
    ("Cadmium", 122, 265, "122–265 ng"),
    ("NNK (nitrosamine)", 50.7, 95.7, "50.7–95.7 ng"),
    ("Benzo[a]pyrene", 51.8, 94.5, "51.8–94.5 ng"),
]


def calc_tables():
    a = []
    for (label, lo, hi, basis) in AIR:
        a.append(f'<tr><th scope="row">{label}</th><td class="val" data-u="mass" data-lo="{lo:g}" data-hi="{hi:g}">–</td>'
                 f'<td class="basis">{basis} per cigarette</td></tr>')
    air = '\n'.join(a)
    butt = '\n'.join([
        '<tr><th scope="row">Butts produced</th><td class="val" data-u="count" data-lo="1" data-hi="1">–</td><td class="basis">1 per cigarette</td></tr>',
        '<tr><th scope="row">Butts dropped on the ground</th><td class="val" data-u="count" data-lo="0.65" data-hi="0.80">–</td><td class="basis">65–80% of smokers litter {{c:who2022,novotny2014}}</td></tr>',
        '<tr><th scope="row">Plastic fibres in those butts</th><td class="val" data-u="count" data-lo="7800" data-hi="12000">–</td><td class="basis">12,000–15,000 fibres per filter {{c:novotny2009,green2023}} × littered share</td></tr>',
        '<tr><th scope="row">Nicotine left in littered butts</th><td class="val" data-u="mass" data-lo="1.3e6" data-hi="1.6e6">–</td><td class="basis">≈2 mg per butt {{c:igb2025}} × littered share</td></tr>',
        '<tr><th scope="row">Water those butts could push above the nicotine no-effect level</th><td class="val" data-u="vol" data-lo="650" data-hi="800">–</td><td class="basis">≈1,000 L per butt {{c:oekotox2019}} × littered share</td></tr>',
        '<tr><th scope="row">Water at the 96-hour fish LC50</th><td class="val" data-u="vol" data-lo="0.59" data-hi="0.82">–</td><td class="basis">0.97–1.1 butts per litre {{c:slaughter2011}} × littered share <span class="derived">derived</span></td></tr>',
    ])
    return air, butt


# ------------------------------------------------------------------ render

def render(body_tpl):
    order = []

    def num(key):
        if key not in REFS:
            raise KeyError(f"unknown reference {key}")
        if key not in order:
            order.append(key)
        return order.index(key) + 1

    body = body_tpl
    for name, ch in CHARTS.items():
        body = body.replace("{{chart:%s}}" % name, ch)
    air, butt = calc_tables()
    body = body.replace("{{CALC_AIR}}", air).replace("{{CALC_BUTT}}", butt)
    body = body.replace("{{WORLD}}", scene.world_svg()).replace("{{LENS}}", scene.lens_svg()).replace("{{LOGO}}", scene.LOGO)
    body = body.replace("{{VERSION}}", VERSION).replace("{{DATE}}", DATE)

    def cite(m):
        keys = [k.strip() for k in m.group(1).split(',')]
        nums = [num(k) for k in keys]
        links = ', '.join(f'<a href="#ref-{n}">{n}</a>' for n in nums)
        return f'<span class="cite">[{links}]</span>'

    body = re.sub(r"\{\{c:([a-z0-9_,\s]+)\}\}", cite, body)
    unused = [k for k in REFS if k not in order]
    if unused:
        print("note: unused references:", ', '.join(unused))
    items = []
    for i, k in enumerate(order, 1):
        au, yr, ti, ve, url, note = REFS[k]
        disp = url.replace('https://', '')
        if len(disp) > 70:
            disp = disp[:67] + '…'
        n = f' <span class="note">{html.escape(note)}</span>' if note else ''
        tt = f'{html.escape(ti)}. ' if ti else ''
        items.append(f'<li id="ref-{i}">{html.escape(au)} ({yr}). {tt}<i>{html.escape(ve)}</i>. '
                     f'<a href="{html.escape(url)}" rel="noopener" target="_blank">{html.escape(disp)}</a>{n}</li>')
    body = body.replace("{{REFS}}", '\n'.join(items))
    body = body.replace("{{NREFS}}", str(len(order)))
    left = re.findall(r"\{\{[^}]+\}\}", body)
    if left:
        raise SystemExit(f"unresolved placeholders: {left[:5]}")
    return body


HEAD = '''<title>SmokeTrail</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Follow the pollution from one cigarette: combustion, inhalation, secondhand and thirdhand smoke, rain, butts, soil, plants and water. With sources and a calculator.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="assets/css/styles.css">'''


def main():
    tpl = open(os.path.join(ROOT, 'src', 'page.html'), encoding='utf-8').read()
    body = render(tpl)
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + HEAD + '\n<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">\n'
            '<meta property="og:title" content="SmokeTrail">\n'
            '<meta property="og:description" content="The journey of cigarette smoke pollution, from the ember to the groundwater.">\n'
            '</head>\n<body>\n' + body + '\n<script src="assets/js/app.js" defer></script>\n</body>\n</html>\n')
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(full)
    with open(os.path.join(ROOT, 'assets', 'img', 'favicon.svg'), 'w', encoding='utf-8') as fh:
        fh.write(scene.FAVICON)
    if '--artifact' in sys.argv:
        dst = sys.argv[sys.argv.index('--artifact') + 1]
        with open(dst, 'w', encoding='utf-8') as fh:
            fh.write(HEAD + '\n' + body + '\n<script src="assets/js/app.js" defer></script>\n')
    print("built", os.path.join(ROOT, 'index.html'), f"{len(full)/1024:.0f} KB")


if __name__ == '__main__':
    main()

from schema import *

# 1. Smallest Components (Verlichting, Toestel, Prieze, Contax) #############

# Verlichting
lamp1 = Verlichting("eettafel 60W smartlamp", "Living", "LED", 1, "wv5", "5g2.5", 14, "20x20", driver="Meanwell")
ct1 = Contax("ct1", "1.7", "pompregenput  kringE")

# Priezen
prieze1 = Prieze("PR-poort", "garage", 1, "flex", 2.5)
prieze2 = Prieze("CEE-lastafel", "garage", 1, "flex", 2.5)
prieze_1algemeen = Prieze("alg", "nvt", 1, "flex", 2.5)

priezemereltv = Prieze("mereltv", "merel", 1, "flex", 2.5)
# kring


kringliving = Kring("living")
kringliving.vullenmet(Prieze("living"), 8)  # Adds pr up to 5 times, or until max_priezen is reached

kringzolder = Kring("zolder")
kringzolder.vullenmet(prieze_1algemeen, 8)  # Adds pr up to 5 times, or until max_priezen is reached

kringdressing = Kring("dressing")
kringdressing.vullenmet(prieze_1algemeen, 3)  # Adds pr up to 5 times, or until max_priezen is reached
kringdressing.add_prieze(priezemereltv)

# Toestellen
toestel1 = Toestel("Vaatwasser", "kkn", "Stopcontact", "3g2.5", "20x20", 5, "bi", kabellijst="wv3")
toestel2 = Toestel("Fornuis", "kkn", "Boite", "3g2.5", "20x20", 5, "bi", kabellijst="ws2")
laadpaal1 = Toestel("blitz", "kkn", "Prieze", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")
luifel1 = Toestel("blitz", "kkn", "boite", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")
luifel2 = Toestel("blitz", "kkn", "boite", "5g2.5", "20x20", 5, "bu", kabellijst="ws19")

# DomoModules with Verlichting
umd0 = DomoModule("0", 8, "relay")
umd0.channels[0] = Verlichting("eettafel 60w smartlamp", "living", kabellijst="wv1")
umd0.channels[1] = Verlichting("eettafel 100w 2e aansluitpunt niet gebruikt", "living", kabellijst="wv2")
umd0.channels[2] = Verlichting("led strip _50% ", "keuken", kabellijst="wv3")
umd0.channels[3] = Verlichting("led strip 100% ", "keuken", kabellijst="wv4blbr")
umd0.channels[4] = Verlichting("garage kapot niet gebruiken 5.5gebruikt", "garage", kabellijst="wv4grzw")
umd0.channels[5] = Verlichting("keukentafel", "keuken", kabellijst="wv10")
umd0.channels[6] = Verlichting("zetel", "living", kabellijst="wv10")
umd0.channels[7] = Verlichting("ledstrip grootraam", "living", kabellijst="wv81")

umd1 = DomoModule("1", 8, "relay")
umd1.channels[0] = Verlichting("dressing", "dressing")
umd1.channels[1] = Verlichting("dressing", "traphal")
umd1.channels[2] = Verlichting("daan", "nachtlamp")
umd1.channels[3] = Verlichting("daan", "slpk alg")
umd1.channels[4] = Verlichting("master", "alg")
umd1.channels[5] = Verlichting("silvie", "nachtlamp")
umd1.channels[6] = Verlichting("vincent", "nachtlamp")
umd1.channels[7] = ct1

umd4 = DomoModule("4", 8, "relay")
umd4.channels[0] = "vrij"
umd4.channels[1] = Prieze("res dlp goot", "traphal")
umd4.channels[2] = Verlichting("daan", "nachtlamp")
umd4.channels[3] = Verlichting("daan", "slpk alg")
umd4.channels[4] = Verlichting("master", "alg")
umd4.channels[5] = Verlichting("silvie", "nachtlamp")
umd4.channels[6] = Verlichting("vincent", "nachtlamp")
umd4.channels[7] = ct1

ct2 = Contax("ct2", "hier", "hier")
ct2.add_verlichting(Verlichting("ledstrip", "dressoir", driver="acdc"))

umd2 = DomoModule("2", 8, "relay")
umd2.channels[0] = ct2
umd2.channels[1] = Verlichting("spotjes tv", "living", aantal=3)
umd2.channels[2] = Verlichting("voordeur", "inkom")
umd2.channels[3] = "contact vrijgave dimmers"
umd2.channels[4] = Verlichting("voetbaltafel", "zolder", aantal=4)
umd2.channels[5] = Verlichting("alg", "merel", aantal=4)
umd2.channels[6] = Verlichting("nachtlamp", "merel")
umd2.channels[7] = Verlichting("buro", "merel", aantal=3)
verl_berging = Verlichting("alg", "berging", aantal=1, bedien="enkelpolig")

dim0 = DomoModule("dim0", 2, "dim")

dim0.channels[0] = Verlichting("trap", "zolder", aantal=4)
dim0.channels[1] = Verlichting("cinema", "zolder")

rolluikmod = DomoModule("3", 2, "relay")
rolluikmod.channels[0] = luifel1
rolluikmod.channels[1] = luifel2

# 2. Circuit Protection (Zekeringen) #########################################

# Create zekeringen
zekA = Zekering("A", 16, 10, "5g2", 7)
zekB = Zekering("B", 16, 16, "5g2", 7)
zekC = Zekering("C", 16, 10, "5g2", 7)
zekD = Zekering("D", 16, 10, "5g2", 7)
zekE = Zekering("E", 16, 10, "5g2", 7)
zekF = Zekering("F", 16, 16, "5g2", 7)
zekG = Zekering("G", 16, 10, "5g2", 7)
zekH = Zekering("H", 16, 10, "5g2", 7)
zekI = Zekering("I", 16, 10, "5g2", 7)
zekJ = Zekering("J", 16, 10, "5g2", 7, scheef="ja")

# Add components to zekeringen
zekF.add_prieze(Prieze("tvboven", 2))
zekF.add_prieze(Prieze("modem", 3))
zekA.add_domomodule(umd0)
zekB.add_domomodule(umd1)
zekE.add_contax(ct1)
zekE.add_kring(kringdressing)

zekD.add_domomodule(rolluikmod)
zekI.add_kring(kringzolder)
zekG.add_kring(kringliving)
zekH.add_domomodule(umd4)

zekC.add_domomodule(umd2)
zekC.add_domomodule(dim0)
zekC.add_verlichting(verl_berging)
# 3. Safety Devices (Differentielen) #########################################

diff1 = Differentieel("Diff1", 40, 4, 300, "A", 6)
diff2 = Differentieel("Diff2", 40, 4, 30, omschrijvng="vochtigeruitmtes")

# Add zekeringen to differentielen
diff1.add_zekering(zekA)
diff1.add_zekering(zekB)
diff1.add_zekering(zekC)
diff1.add_zekering(zekD)
diff1.add_zekering(zekE)
diff1.add_zekering(zekF)
diff1.add_zekering(zekG)

diff1.add_zekering(zekI)
diff2.add_zekering(zekJ)

# 4. Distribution Boards (Verdeelborden) #####################################


# 7. Output and Testing ######################################################
startopbject_in_output = diff1  # vul hier in wat er op de kop vd json getoont moet worden

json_str = json.dumps(startopbject_in_output.as_dict(), indent=2)  # json string {{}}

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")


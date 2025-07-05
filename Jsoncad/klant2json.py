from json_objecten import *

# 1. Smallest Components (Verlichting, Toestel, Prieze, Contax) #############

# contaxen

ct1 = Contax("ct1", "1.7", "pompregenput  kringE")
ct2 = Contax("ct2"  , "hier" , "hier")
ct3 = Contax("ct3"  , "hier" , "hier")
ct4 = Contax("ct4"  , "hier" , "hier")
ct5 = Contax("ct5"  , "hier" , "hier")
ct6 = Contax("ct6"  , "hier" , "hier")

# Priezen
prieze_poort = Prieze("PR-poort", "garage", 1, "flex", 2.5)
prieze_CEElastafel = Prieze("CEE-lastafel", "garage", 1, "flex", 2.5)
prieze_1algemeen = Prieze("alg", "nvt", 1, "flex", 2.5)
prieze_modem = Prieze("modem", "garage", 2, "flex", 2.5 , hydro="hudro")
prieze_tvboven = Prieze("tv", "master", 2, "flex", 2.5 )
priezemereltv= Prieze("mereltv", "merel", 1, "flex", 2.5)
#kring


kringliving = Kring ("living")
kringliving.vullenmet(Prieze("living"), 8)  # Adds pr up to 5 times, or until max_priezen is reached

kringzolder = Kring ("zolder")
kringzolder.vullenmet(prieze_1algemeen, 8)  # Adds pr up to 5 times, or until max_priezen is reached


kringdressing = Kring ("dressing")
kringdressing.vullenmet(prieze_1algemeen, 3)  # Adds pr up to 5 times, or until max_priezen is reached
kringdressing.add_prieze(priezemereltv)



# Toestellen
toestel1 = Toestel("Vaatwasser", "kkn","Stopcontact", "3g2.5", "20x20", 5, "bi", kabellijst="wv3")
toestel2 = Toestel("Fornuis", "kkn","Boite", "3g2.5", "20x20", 5, "bi", kabellijst="ws2")
laadpaal1 = Toestel("blitz", "kkn","Prieze", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")
luifel1 = Toestel("luifel", "koer","rechtstreeks", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")
luifel2 = Toestel("rolluik", "voor","rechtstreeks", "5g2.5", "20x20", 5, "bu", kabellijst="ws19")


# DomoModules with Verlichting
ct2.add_verlichting(Verlichting("ledstrip grootraam", "living", kabellijst="wv81"))
ct3.add_verlichting(Verlichting("led strip _50% ", "keuken", kabellijst="wv3"))
ct4.add_verlichting(Verlichting("led strip 100% ", "keuken", kabellijst="wv4blbr"))
ct5.add_verlichting(Verlichting("zetel", "living", kabellijst="wv10"))

umd0 = DomoModule("0", 8, "relay")
umd0.channels[0] = Verlichting("eettafel 60w smartlamp", "living", kabellijst="wv1")
umd0.channels[1] = Verlichting("eettafel 100w 2e aansluitpunt niet gebruikt", "living", kabellijst="wv2")
umd0.channels[2] = ct3
umd0.channels[3] = ct4
umd0.channels[4] = Verlichting("garage kapot niet gebruiken 5.5gebruikt", "garage", kabellijst="wv4grzw")
umd0.channels[5] = Verlichting("keukentafel", "keuken", kabellijst="wv10")
umd0.channels[6] = Verlichting("zetel", "living", kabellijst="wv10")
umd0.channels[7] = ct2

umd1 = DomoModule("1", 8, "relay")
umd1.channels[0] = Verlichting("dressing", "dressing")
umd1.channels[1] = Verlichting("dressing", "traphal")
umd1.channels[2] = Verlichting("daan", "nachtlamp")
umd1.channels[3] = Verlichting("daan", "slpk alg")
umd1.channels[4] = Verlichting("master", "alg")
umd1.channels[5] = Verlichting("silvie", "nachtlamp")
umd1.channels[6] = Verlichting("vincent", "nachtlamp")
umd1.channels[7] = ct1


ryld = DomoModule("4ryld", 4, "ryld-relay")
ryld.channels[0] = Prieze("dlp1", "dlp")
ryld.channels[1] = Prieze("dlp2", "dlp")
ryld.channels[2] = Prieze("dlp3", "dlp")
ryld.channels[3] = Prieze("dlp4", "dlp")




ct6.add_verlichting(Verlichting("ledstrip", "dressoir" , driver="acdc"))

umd2 = DomoModule("2", 8, "relay")
umd2.channels[0] =  ct6
umd2.channels[1] = Verlichting("spotjes tv", "living" , aantal=3)
umd2.channels[2] = Verlichting("voordeur", "inkom")
umd2.channels[3] = "contact vrijgave dimmers"
umd2.channels[4] = Verlichting("voetbaltafel", "zolder" , aantal=4)
umd2.channels[5] = Verlichting("alg", "merel" , aantal=4)
umd2.channels[6] = Verlichting("nachtlamp", "merel")
umd2.channels[7] = Verlichting("buro", "merel" , aantal=3)
verl_berging = Verlichting("alg", "berging" , aantal=1 , bedien= "enkelpolig")

dim0 = DomoModule("dim0", 2, "dim")

dim0.channels[0] = Verlichting("trap", "zolder" , aantal=4)
dim0.channels[1] = Verlichting("cinema", "zolder")


rolluikmod = DomoModule("3", 2, "rolluik")
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
#zekF.add_prieze(Prieze("tvboven",None ,2))
#zekF.add_prieze(Prieze("modem", 3))
zekA.add_domomodule(umd0)
zekB.add_domomodule(umd1)
zekE.add_contax(ct1)
zekE.add_kring(kringdressing)
zekF.add_prieze(prieze_tvboven)
zekF.add_prieze(prieze_modem)
zekD.add_domomodule(rolluikmod)
zekI.add_kring(kringzolder)
zekG.add_kring(kringliving)
zekH.add_domomodule(ryld)
zekH.add_contax(ct3)
zekH.add_contax(ct4)
zekH.add_contax(ct5)
zekH.add_contax(ct6)

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

sk1 = Verdeelbord("Bord SK1", "garage", 10, merk="geen")
sk1.add_differentieel(diff1)
diff1.add_differentieel(diff2)

# 5. Main Components (Hoofdschakelaar, Teller) ###############################

hs1 = Hoofdschakelaar("HS1", 4, 63)
teller = Teller("Conteur", kleur="geel")
teller.vorm = "vierkant"
teller.add_verdeelbord(sk1)

# 6. Building Structure (Gebouw) #############################################

gebouw1 = Gebouw("Woning vincent", "51.12345, 4.56789", test="ja")
gebouw1.add_teller(teller)



#compleet zetten

zekA.compleet = "ja"
zekB.compleet = "ja"
zekC.compleet = "ja"
zekD.compleet = "ja"
zekE.compleet = "ja"
zekF.compleet = "ja"

# 7. Output and Testing ######################################################
startopbject_in_output = gebouw1   #vul hier in wat er op de kop vd json getoont moet worden



root_json = startopbject_in_output.to_root_json()  #geschikt om schemas te maken
root_json_str = json.dumps(root_json, indent=2)
print(root_json_str)

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=root_json_str)
    print(" JSON copied to clipboard!")




with open('root_json_str.json', 'w', encoding='utf-8') as f:
    f.write(root_json_str)


#oude dict zonder root
json_str = json.dumps(startopbject_in_output.as_dict(), indent=2)
print(json_str)
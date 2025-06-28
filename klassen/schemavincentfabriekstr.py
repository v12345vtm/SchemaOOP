

from schema import *

# 1. Basiselementen ##########################################################

# Priezen
prieze1 = Prieze("PR-poort", 2, "3g2.5", "20x20", 8, hydro="IP44", enk_dubb="enkel")
prieze2 = Prieze("CEE-lastafel", 2, "3g2.5", "20x20", 8, hydro="IP44", enk_dubb="enkel")


# Verlichting LIVING :
lamp1 = Verlichting("eettafel 60W smartlamp", "Living","LED", 1, "wv5", "5g2.5", 14, "20x20", driver="Meanwell")












ct1 = Contax("ct1", "1.7" , "pomp kringE")




umd0 = DomoModule("0", 8, "relay")
umd0.channels[0]  = Verlichting("eettafel 60w smartlamp", "living")
umd0.channels[1]  = Verlichting("eettafel 100w 2e aansluitpunt niet gebruikt", "living")
umd0.channels[2]  = Verlichting("led strip _50% ", "keuken")
umd0.channels[3]  = Verlichting("led strip 100% ", "keuken")
umd0.channels[4]  = Verlichting("garage kapot niet gebruiken 5.5gebruikt", "garage")
umd0.channels[5]  = Verlichting("keukentafel", "keuken")
umd0.channels[6]  = Verlichting("zetel", "living")
umd0.channels[7]  = Verlichting("ledstrip grootraam", "living")


umd1 = DomoModule("1", 8, "relay")
umd1.channels[0]  = Verlichting("dressing", "dressing")
umd1.channels[1]  = Verlichting("dressing", "traphal")
umd1.channels[2]  = Verlichting("daan", "nachtlamp")
umd1.channels[3]  = Verlichting("daan", "slpk alg")
umd1.channels[4]  = Verlichting("master", "alg")
umd1.channels[5]  = Verlichting("silvie", "nachtlamp")
umd1.channels[6]  = Verlichting("vincent", "nachtlamp")
umd1.channels[7]  = ct1

#ct1 = Contax("ct1", "1.7" , "pomp kringE")



#rel1_2 = VelbusRelay(2, "nvt", "ja", "nvt")
#rel1_1.add_verlichting(lamp1)
#rel1_2.add_verlichting(lamp2)


# VelbusContacten
#ryno1_1 = VelbusContact(1, "Voordeur", "5g6", "Blauw")
#ryno1_2 = VelbusContact(2, "Tuinpad", "4g1", "Bruin")



# Toestellen
toestel1 = Toestel("Vaatwasser", "Stopcontact", "3g2.5", "20x20", 5, "bi", kabellijst="wv3")
toestel2 = Toestel("Fornuis", "Boite", "3g2.5", "20x20", 5, "bi", kabellijst="ws2")
laadpaal1 = Toestel("blitz", "Prieze", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")

# 2. Modules en Contax #######################################################

# VelbusModules
#ryno1 = VelbusModule(1)
#ryno1.add_channel(ryno1_1)
#ryno1.add_channel(ryno1_2)

#ryld1 = VelbusModule(2)
#ryld1.add_channel(rel1_1)
#ryld1.add_channel(rel1_2)

# Contax
#ct1 = Contax("CT5", "klok")
#ct1.add_velbusmodule(VelbusModule(3))

# 3. Zekeringen ##############################################################

zekA = Zekering("A", 16, 10, "5g2", 7)
zekB = Zekering("B", 16, 16, "5g2", 7)
zekC = Zekering("C", 16, 10, "5g2", 7)
zekD = Zekering("D", 16, 10, "5g2", 7)
zekE = Zekering("E", 16, 10, "5g2", 7)
zekF = Zekering("F", 16, 16, "5g2", 7)
zekG = Zekering("G", 16, 10, "5g2", 7)
zekH = Zekering("H", 16, 10, "5g2", 7)
zekI = Zekering("I", 16, 10, "5g2", 7)
zekJ = Zekering("J", 16, 10, "5g2", 7 , scheef= "ja")


zekA.add_domomodule(umd0)
zekB.add_domomodule(umd1)
zekE.add_contax(ct1)
#Q1007 = Zekering("Q1007", 16, 10, "5g2", 7)
#Q1007.add_toestel(laadpaal1)

#Q1008 = Zekering("Q1008", 16, 20, "5g2", 7)
#Q1008.add_verlichting(lamp3)

#Q1009 = Zekering("Q1009", 6, 16, "5g2.5", 3)
#Q1009.add_velbusmodule(ryno1)
#Q1009.add_velbusmodule(ryld1)
#Q1009.add_ct(ct1)
#Q1009.add_toestel(toestel1)
#Q1009.add_toestel(toestel2)

#Q1010 = Zekering("Q1010", 6, 16, "5g2.5", 3)
#Q1010.add_prieze(prieze1)
#Q1010.add_toestel(toestel1)
#Q1010.add_prieze(prieze2)

# 4. Differentielen ##########################################################

diff1 = Differentieel("Diff1", 40, 4, 300, "A", 6)
diff2 = Differentieel("Diff2", 40, 4 , 30, omschrijvng= "vochtigeruitmtes")


diff1.add_zekering(zekA)
diff1.add_zekering(zekB)
diff1.add_zekering(zekC)
diff1.add_zekering(zekD)
diff1.add_zekering(zekE)
diff1.add_zekering(zekF)

diff2.add_zekering(zekJ)

#diff2_3 = Differentieel("Diff2_3", 40, 4, 300, "A", 6)
#diff2 = Differentieel("Diff2", 40, 4, 300, "A", 6)
#diff2.add_differentieel(diff2_3)

# 5. Hoofdzekering ###########################################################

#hoofdzekering = Zekering("Hoofdzekering", 6, 16, "5g2.5", 3)
#hoofdzekering.add_differentieel(diff1)

# 6. Hoofdschakelaar #########################################################

hs1 = Hoofdschakelaar("HS1", 4, 63)
#hs1.add_zekering(Q1009)
#print(hs1)

# 7. Verdeelborden ###########################################################

sk1 = Verdeelbord("Bord SK1", "garage", 10 , merk="geen")

sk1.add_differentieel(diff1)
sk1.add_differentieel(diff2)



#sk2 = Verdeelbord("Bord SK2", "Gelijkvloer", 14533 , vernieud = "ja")
#sk2.add_zekering(Q1008)
#sk2.add_hoofdschakelaar(hs1)

#sk2_1 = Verdeelbord("Bord SK2.1", "Gelijkvloer", 14533, lengte=5)
#sk2.add_verdeelbord(sk2_1)

# 8. Gebouw en Teller ########################################################

#teller = Teller("1234567890123", 40, "EXVB", 16 , merk = "siconia")
teller = Teller()
#teller2 = Teller("1234567890123", 40, "EXVB", 16 , merk = "siconia")
#vbarg = Verdeelbord("test" , "pc" , 2000 , "5g66" , merk = "obodoos" )
teller.add_verdeelbord(sk1)


gebouw1 = Gebouw("Woning vincent", "51.12345, 4.56789",  test= "ja")
gebouw1.add_teller(teller)




json_str = json.dumps(gebouw1.as_dict(), indent=2)

# Kopieer naar clipboard (alleen op Windows)

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")



print ("dicttester")
#print (vb1.as_dict())
print ("**dicttester")


from schema import *

# 1. Basiselementen ##########################################################

# Priezen
prieze1 = Prieze("PR-poort", 2, "3g2.5", "20x20", 8, hydro="IP44", enk_dubb="enkel")
prieze2 = Prieze("CEE-lastafel", 2, "3g2.5", "20x20", 8, hydro="IP44", enk_dubb="enkel")


# Verlichting
lamp1 = Verlichting("Spots Keuken", "LED", 8, "wv5", "5g2.5", 14, "20x20", driver="Meanwell")
lamp2 = Verlichting("Spots trap", "LED", 1, "wv6", "5g2.5", 4, "20x20", transfo="tr1 100W")
lamp3 = Verlichting("far tuin", "LED", 8, "wv5", "5g2.5", 14, "20x20", driver="Meanwell")
lamp4 = Verlichting("rgb strip", "LED", 1, "wv6", "5g2.5", 4, "20x20", transfo="tr1 100W")

# VelbusContacten
ryno1_1 = VelbusContact(1, "Voordeur", "5g6", "Blauw")
ryno1_2 = VelbusContact(2, "Tuinpad", "4g1", "Bruin")

# VelbusRelays
rel1_1 = VelbusRelay(1, "nvt", "nvt", "nvt")
rel1_2 = VelbusRelay(2, "nvt", "ja", "nvt")
rel1_1.add_verlichting(lamp1)
rel1_2.add_verlichting(lamp2)

# Toestellen
toestel1 = Toestel("Vaatwasser", "Stopcontact", "3g2.5", "20x20", 5, "bi", kabellijst="wv3")
toestel2 = Toestel("Fornuis", "Boite", "3g2.5", "20x20", 5, "bi", kabellijst="ws2")
laadpaal1 = Toestel("blitz", "Prieze", "5g2.5", "20x20", 5, "bu", kabellijst="ws1")

# 2. Modules en Contax #######################################################

# VelbusModules
ryno1 = VelbusModule(1)
ryno1.add_channel(ryno1_1)
ryno1.add_channel(ryno1_2)

ryld1 = VelbusModule(2)
ryld1.add_channel(rel1_1)
ryld1.add_channel(rel1_2)

# Contax
ct1 = Contax("CT5", "klok")
ct1.add_velbusmodule(VelbusModule(3))

# 3. Zekeringen ##############################################################

Q1007 = Zekering("Q1007", 16, 10, "5g2", 7)
Q1007.add_toestel(laadpaal1)

Q1008 = Zekering("Q1008", 16, 20, "5g2", 7)
Q1008.add_verlichting(lamp3)

Q1009 = Zekering("Q1009", 6, 16, "5g2.5", 3)
Q1009.add_velbusmodule(ryno1)
Q1009.add_velbusmodule(ryld1)
Q1009.add_ct(ct1)
Q1009.add_toestel(toestel1)
Q1009.add_toestel(toestel2)

Q1010 = Zekering("Q1010", 6, 16, "5g2.5", 3)
Q1010.add_prieze(prieze1)
Q1010.add_toestel(toestel1)
Q1010.add_prieze(prieze2)

# 4. Differentielen ##########################################################

diff1 = Differentieel("Diff1", 40, 4, 300, "A", 6)
diff1.add_zekering(Q1009)
diff1.add_zekering(Q1008)

diff2_3 = Differentieel("Diff2_3", 40, 4, 300, "A", 6)
diff2 = Differentieel("Diff2", 40, 4, 300, "A", 6)
diff2.add_differentieel(diff2_3)

# 5. Hoofdzekering ###########################################################

hoofdzekering = Zekering("Hoofdzekering", 6, 16, "5g2.5", 3)
hoofdzekering.add_differentieel(diff1)

# 6. Hoofdschakelaar #########################################################

hs1 = Hoofdschakelaar("HS1", 4, 63)
hs1.add_zekering(Q1009)
print(hs1)

# 7. Verdeelborden ###########################################################

sk1 = Verdeelbord("Bord SK1", "Kelder", 10)
sk1.add_zekering(hoofdzekering)
sk1.add_differentieel(diff2)

sk2 = Verdeelbord("Bord SK2", "Gelijkvloer", 14533)
sk2.add_zekering(Q1008)
sk2.add_hoofdschakelaar(hs1)

sk2_1 = Verdeelbord("Bord SK2.1", "Gelijkvloer", 14533, lengte=5)
sk2.add_verdeelbord(sk2_1)

# 8. Gebouw en Teller ########################################################

teller = Teller("1234567890123", 40, "EXVB", 10)
teller.add_verdeelbord(sk2)


gebouw1 = Gebouw("Woning vincent", "51.12345, 4.56789", "Netbeheerder")
gebouw1.add_teller(teller)
gebouw1.add_Verdeelbord(sk1)




json_str = json.dumps(gebouw1.as_dict(), indent=2)

# Kopieer naar clipboard (alleen op Windows)

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")

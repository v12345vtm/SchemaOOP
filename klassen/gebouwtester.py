from OOPschema import *

hs1 = Hoofdschakelaar("HS1", 4, 63)
teller = Teller("Conteur", kleur="geel")
teller.vorm = "vierkant"
teller.add_hoofdschakelaar(hs1)

# 6. Building Structure (Gebouw) #############################################

gebouw1 = Gebouw("Woning vincent", "51.12345, 4.56789", test="ja")
#gebouw1.add_teller(teller)



# 7. Output and Testing ######################################################
startopbject_in_output = gebouw1  #vul hier in wat er op de kop vd json getoont moet worden

json_str = json.dumps(startopbject_in_output.as_dict(), indent=2) #json string {{}}

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")


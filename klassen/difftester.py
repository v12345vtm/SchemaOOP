from OOPschema import *

# 2. Circuit Protection (Zekeringen) #########################################

# Create zekeringen
zekZ = Zekering("A", 16, 10, "5g2", 7)

zekY = Zekering("J", 16, 10, "5g2", 7, scheef="ja")

# Add components to zekeringen

# 3. Safety Devices (Differentielen) #########################################


diff1 = Differentieel("Diff1", 40, 4, 30, omschrijvng="hoofd")

diff2 = Differentieel("Diff2", 40, 4, 30, omschrijvng="vochtigeruitmtes")

# Add zekeringen to differentielen
diff2.add_zekering(zekY)

diff2.add_zekering(zekZ)
diff2.add_differentieel(diff1)
# 4. Distribution Boards (Verdeelborden) #####################################

teller = Teller("telmet2difs")
verdeelbord1 = Verdeelbord("sk1"  , "garage" , 10 )

teller.add_verdeelbord(verdeelbord1)
verdeelbord1.add_differentieel(diff2)
# 7. Output and Testing ######################################################
startopbject_in_output = teller  # vul hier in wat er op de kop vd json getoont moet worden

json_str = json.dumps(startopbject_in_output.as_dict(), indent=2)  # json string {{}}

root_json = startopbject_in_output.to_root_json()
json_str = json.dumps(root_json, indent=2)
print(json_str)

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")


from OOPschema import *

umd4 = DomoModule("4", 8, "relay")
umd4.channels[0] = "vrij"
umd4.channels[1] = Prieze("res dlp goot", "traphal")
umd4.channels[2] = Verlichting("daan", "nachtlamp")
umd4.channels[3] = Verlichting("daan", "slpk alg")
umd4.channels[4] = Verlichting("master", "alg")
umd4.channels[5] = Verlichting("silvie", "nachtlamp")
umd4.channels[6] = Verlichting("vincent", "nachtlamp")
umd4.channels[7] = "ct1"

print (umd4.as_dict())



testobjecttojson = umd4
json_str = json.dumps(testobjecttojson.as_dict(), indent=2)
#print(json_str)

json_zolderkring = json.dumps(testobjecttojson.as_dict(), indent=2)




if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_zolderkring)
    print(" JSON copied to clipboard!")
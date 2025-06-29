from schema import *

a= Verlichting("daan", "nachtlamp")
b= Verlichting("daan", "slpk alg")
c= Verlichting("master", "alg")
d = Verlichting("silvie", "nachtlamp")
e = Verlichting("vincent", "nachtlamp")

kruis = Bediening("kruis")

wissel = Bediening("wissel")

enk = Bediening("enkelpolig")

dub = Bediening("dubbelpolig")
enk_indicatie = Bediening("enkelp met indicatie")



print (umd4.as_dict())



testobjecttojson = umd4
json_str = json.dumps(testobjecttojson.as_dict(), indent=2)
#print(json_str)

json_zolderkring = json.dumps(testobjecttojson.as_dict(), indent=2)




if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_zolderkring)
    print(" JSON copied to clipboard!")
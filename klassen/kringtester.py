from schema import *
pr = Prieze("zolder" , "muur")


zolderkring = Kring ("zolder")
zolderkring.add_prieze(pr)
zolderkring.add_prieze(pr)
zolderkring.vullenmet(pr, 9)  # Adds pr up to 5 times, or until max_priezen is reached


print (zolderkring.as_dict())
print (pr.as_dict())



json_str = json.dumps(pr.as_dict(), indent=2)
#print(json_str)

json_zolderkring = json.dumps(zolderkring.as_dict(), indent=2)

print("Aantal Priezen in Kring:", len(zolderkring.priezen))


if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_zolderkring)
    print(" JSON copied to clipboard!")
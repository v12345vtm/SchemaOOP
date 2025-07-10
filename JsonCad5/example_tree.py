# example_tree.py

from components import *

# Build the tree
cabine = Voeding("cabine", "voeding")
voeding2 = Voeding("Voeding2", "voeding")
zek1voeding2 = CircuitBreaker("voeding2Zekering1", "circuit_breaker")
voeding = Voeding("Voeding", "voeding")
diff300 = Differential("Diff300", "differential")
diff30 = Differential("Diff30", "differential")
diff3 = Differential("Diff9", "differential")
zek1 = CircuitBreaker("Zekering1", "circuit_breaker")
zek2 = CircuitBreaker("Zekering102", "circuit_breaker")
zek3 = CircuitBreaker("Zekering99", "circuit_breaker")
zek4 = CircuitBreaker("Zekering4", "circuit_breaker")
vaatwas = Appliance("Vaatwas", "appliance")
keuken = Appliance("Keuken", "appliance")
dif9_3 = Appliance("3etoestel", "appliance" , volgorde=2 )
oven = Appliance("Oven", "appliance")
microOven = Appliance("microOven", "appliance")
contaxopvoeding = Contax("contaxvoeding" , "appliance")
domo1 = Domomodule("Domo1", "domomodule")
ct1 = Contax("ct1", "contax")
ct2 = Contax("ct2", "contax")
ct3 = Contax("ct3", "contax")
ct4 = Contax("ct4", "contax")
ct5 = Contax("ct5", "contax")
ct6 = Contax("ct6", "contax")
ct7 = Contax("ct7", "contax")
ct8 = Contax("ct8", "contax")

verlichting1 = Verlichting("Verlicht1", "verlichting")

diffa = Differential("DiffA", "differential")
diffb = Differential("DIFFB", "differential")
zekc = CircuitBreaker("Zekeringc", "circuit_breaker")
tv = Appliance("tv", "appliance")
tv2 = Appliance("tv2", "appliance")
voeding2.add_child(zek1voeding2)
cabine.add_child(voeding)
cabine.add_child(voeding2)

voeding.add_child(diffa)
diffa.add_child(diffb)
diffb.add_child(zekc)
zekc.add_child(tv)
zekc.add_child(tv2)
voeding.add_child(contaxopvoeding)
voeding.add_child(diff300)
voeding.add_child(diff30)
voeding.add_child(diff3)
voeding.add_child(verlichting1)

diff300.add_child(zek1)
diff30.add_child(zek2)
zek1.add_child(vaatwas)
zek2.add_child(keuken)
zek2.add_child(oven)
diff30.add_child(zek3)
diff30.add_child(microOven)
diff30.add_child(zek4)

diff3.add_child(domo1)
diff3.add_child(ct1 , ct2 , ct3 , ct4 , ct5 , ct6 , ct7 , ct8)
diff3.add_child(dif9_3)

# Export the root node
te_tekenen_startpunt = cabine

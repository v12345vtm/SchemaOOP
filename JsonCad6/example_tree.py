

from components import * #alles van de klasse importeren

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
cabine.add_child(voeding , voeding2)
diff3.add_child(domo1 , dif9_3 , ct1 , ct2 , ct3 , ct4 , ct5 , ct6 , ct7 , ct8)
diff30.add_child(microOven , zek2 , zek3 , zek4)
diff300.add_child(zek1)
diffa.add_child(diffb)
diffb.add_child(zekc)
voeding.add_child(diff3 , verlichting1 , diffa ,diff300 ,  contaxopvoeding , diff30)
voeding2.add_child(zek1voeding2)
zek1.add_child(vaatwas)
zek2.add_child(keuken , oven)
zekc.add_child(tv , tv2)

# Export the root node
te_tekenen_startpunt = cabine


import json
import subprocess #klembord schrijven
import platform #voor klembord

def toon_automaten_per_bord(gebouw):
    """
    Toont alle automaten per verdeelbord, inclusief differentiëlen en zekeringen (ook genest).
    """
    for vb in gebouw.verdeelborden:
        print(f"\nVerdeelbord: {vb.naam} ({vb.lokatie})")

        def rec(obj, indent=2):
            sp = ' ' * indent
            if isinstance(obj, Zekering):
                print(sp + obj.maak_automatenlijstlijn())
                for diff in obj.differentielen:
                    rec(diff, indent + 2)

            elif isinstance(obj, Differentieel):
                print(sp + f"{obj.naam} {obj.polen}P {obj.amp}A (Diff)")
                for zek in obj.zekeringen:
                    rec(zek, indent + 2)
                for subdiff in obj.differentielen:
                    rec(subdiff, indent + 2)

        for zek in vb.zekeringen:
            rec(zek)

        for diff in vb.differentielen:
            rec(diff)



def verzamel_alle_automaten_recursief(obj):
    """
    Recursief verzamel alle zekeringen én differentiëlen als 'automaten', in de juiste volgorde.
    Elke automaat wordt als tuple (type, object) teruggegeven, bv. ('zekering', <Zekering>) of ('differentieel', <Differentieel>)
    """
    gevonden = []

    if isinstance(obj, Gebouw):
        for vb in obj.verdeelborden:
            gevonden.extend(verzamel_alle_automaten_recursief(vb))

    elif isinstance(obj, Verdeelbord):
        for zek in obj.zekeringen:
            gevonden.extend(verzamel_alle_automaten_recursief(zek))
        for diff in obj.differentielen:
            gevonden.extend(verzamel_alle_automaten_recursief(diff))

    elif isinstance(obj, Zekering):
        gevonden.append(('zekering', obj))
        for diff in obj.differentielen:
            gevonden.extend(verzamel_alle_automaten_recursief(diff))

    elif isinstance(obj, Differentieel):
        gevonden.append(('differentieel', obj))
        for zek in obj.zekeringen:
            gevonden.extend(verzamel_alle_automaten_recursief(zek))
        for subdiff in obj.differentielen:
            gevonden.extend(verzamel_alle_automaten_recursief(subdiff))

    return gevonden


def toon_gebouwstructuur(gebouw):
    def print_diff(diff, indent=4):
        prefix = ' ' * indent
        print(f"{prefix}- Differentieel: {diff.naam}")
        for zek in diff.zekeringen:
            print(f"{prefix}  - Zekering: {zek.naam}")
        for subdiff in diff.differentielen:
            print_diff(subdiff, indent + 4)

    print(f"Gebouw: {gebouw.naam}")
    for vb in gebouw.verdeelborden:
        print(f"  Verdeelbord: {vb.naam}")
        for diff in vb.differentielen:
            print_diff(diff, indent=4)
        for zek in vb.zekeringen:
            print(f"    - Zekering: {zek.naam}")




class Prieze:
    def __init__(self, naam, aantal, kabel, carre, lengte, hydro=None, enk_dubb=None):
        self.naam = naam
        self.aantal = aantal
        self.kabel = kabel
        self.carre = carre
        self.lengte = lengte
        self.hydro = hydro      # Optioneel
        self.enk_dubb = enk_dubb  # Optioneel

    def as_dict(self):
        return {
            'naam': self.naam,
            'aantal': self.aantal,
            'kabel': self.kabel,
            'carre': self.carre,
            'lengte': self.lengte,
            'hydro': self.hydro,
            'enk_dubb': self.enk_dubb
        }

class Gebouw:
    def __init__(self, naam, pos, toevoervan):
        self.naam = naam
        self.pos = pos
        self.toevoervan = toevoervan
        self.verdeelborden = []  # lijst voor Verdeelbord-objecten
        self.tellers = []        # lijst voor Teller-objecten

    def add_Verdeelbord(self, verdeelbord):
        if not isinstance(verdeelbord, Verdeelbord):
            raise ValueError("Only Verdeelbord instances can be added")
        self.verdeelborden.append(verdeelbord)

    def add_teller(self, teller):
        if not isinstance(teller, Teller):
            raise ValueError("Only Teller instances can be added")
        self.tellers.append(teller)

    def as_dict(self):
        return {
            'naam': self.naam,
            'pos': self.pos,
            'toevoervan': self.toevoervan,
            'verdeelborden': [vb.as_dict() for vb in self.verdeelborden],
            'tellers': [t.as_dict() for t in self.tellers]
        }

class Verlichting:
    def __init__(self, naam, soort, aantal, kabellijst, kabel, lengte, carre, driver=None, transfo=None):
        self.naam = naam
        self.driver = driver      # Optioneel
        self.transfo = transfo    # Optioneel
        self.soort = soort
        self.aantal = aantal
        self.kabellijst = kabellijst
        self.kabel = kabel
        self.lengte = lengte
        self.carre = carre

    def as_dict(self):
        return {
            'naam': self.naam,
            'driver': self.driver,
            'transfo': self.transfo,
            'soort': self.soort,
            'aantal': self.aantal,
            'kabellijst': self.kabellijst,
            'kabel': self.kabel,
            'lengte': self.lengte,
            'carre': self.carre
        }


class VelbusModule:
    def __init__(self, module_id):
        self.module_id = module_id
        self.subdevices = []
        self.subdevice_type = None  # 'relay' or 'contact'

    def as_dict(self):
        subdevice_dicts = [sub.as_dict() for sub in self.subdevices]
        return {
            'velbusmodule': self.subdevice_type,
            'module_id': self.module_id,
            'channels': subdevice_dicts

        }

    def add_channel(self, subdevice):
        if not self.subdevices:
            if isinstance(subdevice, VelbusRelay):
                self.subdevice_type = 'relayRYLD'
            elif isinstance(subdevice, VelbusContact):
                self.subdevice_type = 'contactRYNO'
            else:
                raise ValueError("Unknown subdevice type")
        current_type = self.subdevice_type
        if (current_type == 'relay' and not isinstance(subdevice, VelbusRelay)) or \
                (current_type == 'contact' and not isinstance(subdevice, VelbusContact)):
            raise ValueError(f"Cannot add {type(subdevice).__name__}: module already has {current_type}s")
        if len(self.subdevices) >= 4:
            raise ValueError("Cannot add more than 4 subdevices to a module")
        self.subdevices.append(subdevice)



class VelbusRelay:
    def __init__(self, channelID, code_HA, code_Caneco, kleur):
        self.module_id = channelID
        self.code_HA = code_HA
        self.code_Caneco = code_Caneco
        self.kleur = kleur
        self.verlichting = []  # <-- lijst voor Verlichting-objecten

    def add_verlichting(self, verlichting):
        if not isinstance(verlichting, Verlichting):
            raise ValueError("Only Verlichting instances can be added")
        self.verlichting.append(verlichting)

    def as_dict(self):
        data = self.__dict__.copy()
        # Zorg dat verlichting correct geserialiseerd wordt
        data['verlichting'] = [v.as_dict() for v in self.verlichting]
        return data

class VelbusContact:
    def __init__(self, channelID, naam, kabel, kleur):
        self.module_id = channelID
        self.naam = naam
        self.kabel = kabel
        self.kleur = kleur

    def as_dict(self):
        return self.__dict__.copy()

class Differentieel:
    def __init__(self, naam, amp, polen, millies, type_, kA):
        self.naam = naam
        self.amp = amp
        self.polen = polen
        self.millies = millies
        self.type = type_
        self.kA = kA
        self.velbusmodules = []   # List for VelbusModule objects
        self.ct_objects = []      # List for Contax objects
        self.toestellen = []      # List for Toestel objects
        self.zekeringen = []      # List for Zekering objects
        self.differentielen = []  # <-- Toegevoegd
        self.priezen = []  # <-- Toegevoegd

    def add_velbusmodule(self, module):
        if not isinstance(module, VelbusModule):
            raise ValueError("Only VelbusModule instances can be added")
        self.velbusmodules.append(module)

    def add_ct(self, ct):
        if not isinstance(ct, Contax):
            raise ValueError("Only Contax instances can be added")
        self.ct_objects.append(ct)

    def add_toestel(self, toestel):
        if not isinstance(toestel, Toestel):
            raise ValueError("Only Toestel instances can be added")
        self.toestellen.append(toestel)

    def add_zekering(self, zekering):
        if not isinstance(zekering, Zekering):
            raise ValueError("Only Zekering instances can be added")
        self.zekeringen.append(zekering)

    def add_differentieel(self, differentieel):
        if not isinstance(differentieel, Differentieel):
            raise ValueError("Only Differentieel instances can be added")
        self.differentielen.append(differentieel)

    def add_prieze(self, prieze):
        if not isinstance(prieze, Prieze):
            raise ValueError("Only Prieze instances can be added")
        self.priezen.append(prieze)

    def as_dict(self):
        return {
            'naam': self.naam,
            'amp': self.amp,
            'polen': self.polen,
            'millies': self.millies,
            'type': self.type,
            'kA': self.kA,
            'velbusmodules': [mod.as_dict() for mod in self.velbusmodules],
            'contaxen': [ct.as_dict() for ct in self.ct_objects],
            'toestellen': [toestel.as_dict() for toestel in self.toestellen],
            'zekeringen': [zek.as_dict() for zek in self.zekeringen],
            'priezen': [p.as_dict() for p in self.priezen]  # <-- Toegevoegd
        }

class Zekering:
    def __init__(self, naam, ka, amp, kabelonder, polen):
        self.naam = naam
        self.ka = ka
        self.amp = amp
        self.kabelonder = kabelonder
        self.polen = polen
        self.velbusmodules = []   # List for VelbusModule objects
        self.ct_objects = []      # List for CT objects
        self.toestellen = []      # List for Toestel objects
        self.differentielen = []  # List for Differentieel objects
        self.priezen = []  # <-- Toegevoegd
        self.verlichtingen = []  # <-- nieuw toegevoegd attribuut

    def controleer_verlichting_veiligheid(self):
        # Verzamel alle verlichting, direct en via VelbusRelay
        verlichtingen = list(self.verlichtingen)

        for module in self.velbusmodules:
            for ch in module.subdevices:
                if isinstance(ch, VelbusRelay):
                    verlichtingen.extend(ch.verlichting)

        # Als er verlichting is en ampère > 16, geef waarschuwing
        if verlichtingen and self.amp > 16:
            return f" Waarschuwing: verlichting op zekering {self.naam} ({self.amp}A) > 16A!"
        else:
            return f" Zekering {self.naam} oké (verlichting of amp <= 16A)"


    def maak_automatenlijstlijn(self):
        onderdelen = []

        # Voeg namen van Contax objecten toe
        onderdelen.extend(ct.naam for ct in self.ct_objects)

        # Voeg namen van Priezen toe
        onderdelen.extend(prieze.naam for prieze in self.priezen)

        # Voeg namen van Toestellen toe
        onderdelen.extend(toestel.naam for toestel in self.toestellen)

        # Voeg direct gekoppelde verlichting toe
        onderdelen.extend(v.naam for v in self.verlichtingen)

        # Voeg verlichting toe via velbusmodules (alle relays)
        for mod in self.velbusmodules:
            for ch in mod.subdevices:
                if isinstance(ch, VelbusRelay):
                    onderdelen.extend(v.naam for v in ch.verlichting)

        prefix = f"{self.naam} {self.polen}P {self.amp}A:"
        return f"{prefix} " + ", ".join(onderdelen)
    def add_verlichting(self, verlichting):
        if not isinstance(verlichting, Verlichting):
            raise ValueError("Only Verlichting instances can be added")
        self.verlichtingen.append(verlichting)


    def add_velbusmodule(self, module):
        if not isinstance(module, VelbusModule):
            raise ValueError("Only VelbusModule instances can be added")
        self.velbusmodules.append(module)

    def add_ct(self, ct):
        if not isinstance(ct, Contax):
            raise ValueError("Only CT instances can be added")
        self.ct_objects.append(ct)

    def add_toestel(self, toestel):
        if not isinstance(toestel, Toestel):
            raise ValueError("Only Toestel instances can be added")
        self.toestellen.append(toestel)

    def add_differentieel(self, differentieel):
        if not isinstance(differentieel, Differentieel):
            raise ValueError("Only Differentieel instances can be added")
        self.differentielen.append(differentieel)

    def add_prieze(self, prieze):
        if not isinstance(prieze, Prieze):
            raise ValueError("Only Prieze instances can be added")
        self.priezen.append(prieze)

    def as_dict(self):
        return {
            'naam': self.naam,
            'ka': self.ka,
            'amp': self.amp,
            'kabelonder': self.kabelonder,
            'polen': self.polen,
            'velbusmodules': [mod.as_dict() for mod in self.velbusmodules],
            'contaxen': [ct.as_dict() for ct in self.ct_objects],
            'toestellen': [toestel.as_dict() for toestel in self.toestellen],
            'differentielen': [diff.as_dict() for diff in self.differentielen],
            'priezen': [p.as_dict() for p in self.priezen],
            'verlichtingen': [v.as_dict() for v in self.verlichtingen]  # <-- nieuw toegevoegd
        }


class Contax:
    def __init__(self, naam, spoel_van):
        self.naam = naam
        self.spoel_van = spoel_van
        self.velbusmodules = []
        self.priezen = []  # <-- Toegevoegd

    def add_velbusmodule(self, module):
        if not isinstance(module, VelbusModule):
            raise ValueError("Only VelbusModule instances can be added")
        self.velbusmodules.append(module)

    def add_prieze(self, prieze):
        if not isinstance(prieze, Prieze):
            raise ValueError("Only Prieze instances can be added")
        self.priezen.append(prieze)

    def as_dict(self):
        return {
            'naam': self.naam,
            'spoel_van': self.spoel_van,
            'velbusmodules': [mod.as_dict() for mod in self.velbusmodules],
            'priezen': [p.as_dict() for p in self.priezen]  # <-- Toegevoegd
        }

class Teller:
    def __init__(self, ean, amp, toevoerkabel=None, carre=None):
        self.ean = ean                # EAN-nummer (uniek identificatienummer)
        self.amp = amp                # Stroomsterkte in ampère
        self.toevoerkabel = toevoerkabel  # bv. 'EXVB', 'H07RN-F', ...
        self.carre = carre            # doorsnede in mm²
        self.zekeringen = []
        self.differentielen = []
        self.hoofdschakelaars = []
        self.verdeelborden = []

    def add_zekering(self, zekering):
        if not isinstance(zekering, Zekering):
            raise ValueError("Only Zekering instances can be added")
        self.zekeringen.append(zekering)

    def add_differentieel(self, differentieel):
        if not isinstance(differentieel, Differentieel):
            raise ValueError("Only Differentieel instances can be added")
        self.differentielen.append(differentieel)

    def add_hoofdschakelaar(self, hoofdschakelaar):
        if not isinstance(hoofdschakelaar, Hoofdschakelaar):
            raise ValueError("Only Hoofdschakelaar instances can be assigned")
        self.hoofdschakelaars.append(hoofdschakelaar)

    def add_verdeelbord(self, verdeelbord):
        if not isinstance(verdeelbord, Verdeelbord):
            raise ValueError("Only Verdeelbord instances can be added")
        print(f"WAARSCHUWING: Bent u zeker dat u een verdeelbord zonder zekering ertussen wil aankoppelen?\n"
              f"Teller: '{self.ean}'\n"
              f"Sub-verdeelbord: '{verdeelbord.naam}' (locatie: {verdeelbord.lokatie})")
        self.verdeelborden.append(verdeelbord)

    def as_dict(self):
        return {
            'ean': self.ean,
            'amp': self.amp,
            'toevoerkabel': self.toevoerkabel,
            'carre': self.carre,
            'zekeringen': [zek.as_dict() for zek in self.zekeringen],
            'differentielen': [diff.as_dict() for diff in self.differentielen],
            'hoofdschakelaars': [hos.as_dict() for hos in self.hoofdschakelaars],
            'verdeelborden': [vb.as_dict() for vb in self.verdeelborden]
        }


class Verdeelbord:
    def __init__(self, naam, lokatie, kA, toevoerkabel=None, carre=None, lengte=None):
        self.naam = naam
        self.lokatie = lokatie
        self.kA = kA
        self.toevoerkabel = toevoerkabel  # bv. 'EXVB', 'H07RN-F', ...
        self.carre = carre                # doorsnede in mm²
        self.lengte = lengte              # lengte in meter
        self.zekeringen = []
        self.differentielen = []
        self.hoofdschakelaars = []
        self.verdeelborden = []

    def add_zekering(self, zekering):
        if not isinstance(zekering, Zekering):
            raise ValueError("Only Zekering instances can be added")
        self.zekeringen.append(zekering)

    def add_differentieel(self, differentieel):
        if not isinstance(differentieel, Differentieel):
            raise ValueError("Only Differentieel instances can be added")
        self.differentielen.append(differentieel)

    def add_hoofdschakelaar(self, hoofdschakelaar):
        if not isinstance(hoofdschakelaar, Hoofdschakelaar):
            raise ValueError("Only Hoofdschakelaar instances can be assigned")
        self.hoofdschakelaars.append(hoofdschakelaar)

    def add_verdeelbord(self, verdeelbord):
        if not isinstance(verdeelbord, Verdeelbord):
            raise ValueError("Only Verdeelbord instances can be added")
        print(f"WAARSCHUWING: Bent u zeker dat u een verdeelbord zonder zekering ertussen wil aankoppelen?\n"
              f"Hoofdverdeelbord: '{self.naam}' (locatie: {self.lokatie})\n"
              f"Sub-verdeelbord: '{verdeelbord.naam}' (locatie: {verdeelbord.lokatie})")
        self.verdeelborden.append(verdeelbord)

    def as_dict(self):
        return {
            'naam': self.naam,
            'lokatie': self.lokatie,
            'kA': self.kA,
            'toevoerkabel': self.toevoerkabel,
            'carre': self.carre,
            'lengte': self.lengte,
            'zekeringen': [zek.as_dict() for zek in self.zekeringen],
            'differentielen': [diff.as_dict() for diff in self.differentielen],
            'hoofdschakelaars': [hos.as_dict() for hos in self.hoofdschakelaars],
            'verdeelborden': [vb.as_dict() for vb in self.verdeelborden]
        }


class Hoofdschakelaar:
    def __init__(self, naam, polen, amp):
        self.naam = naam
        self.polen = polen
        self.amp = amp
        self.zekeringen = []       # List for Zekering objects
        self.differentielen = []   # List for Differentieel objects

    def add_zekering(self, zekering):
        if not isinstance(zekering, Zekering):
            raise ValueError("Only Zekering instances can be added")
        self.zekeringen.append(zekering)

    def add_differentieel(self, differentieel):
        if not isinstance(differentieel, Differentieel):
            raise ValueError("Only Differentieel instances can be added")
        self.differentielen.append(differentieel)


    def as_dict(self):
        return {
            'naam': self.naam,
            'polen': self.polen,
            'amp': self.amp,
            'zekeringen': [zek.as_dict() for zek in self.zekeringen],
            'differentielen': [diff.as_dict() for diff in self.differentielen],
        }

    def __str__(self):
        return f"{self.naam} {self.polen}P {self.amp}A"

class Toestel:
    def __init__(self, naam, aansluiting, kabel, carre, lengte, bibu ,kabellijst=None):
        self.naam = naam
        self.aansluiting = aansluiting
        self.kabel = kabel
        self.carre = carre
        self.lengte = lengte
        self.bibu = bibu
        self.kabellijst = kabellijst  # Nieuw attribuut

    def as_dict(self):
        return {
            'naam': self.naam,
            'aansluiting': self.aansluiting,
            'kabel': self.kabel,
            'carre': self.carre,
            'lengte': self.lengte,
            'bibu': self.bibu,
            'kabellijst': self.kabellijst
        }


# 1. Basiselementen ##########################################################

# Priezen
prieze1 = Prieze("CEE-poort", 2, "3g2.5", "20x20", 8, hydro="IP44", enk_dubb="enkel")
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


gebouw1 = Gebouw("Woning Janssens", "51.12345, 4.56789", "Netbeheerder")
gebouw1.add_teller(teller)
gebouw1.add_Verdeelbord(sk1)



# 9. Export naar JSON + Clipboard (Windows) ##################################


json_str = json.dumps(gebouw1.as_dict(), indent=2)

# Kopieer naar clipboard (alleen op Windows)

if platform.system() == "Windows":
    subprocess.run('clip', universal_newlines=True, input=json_str)
    print(" JSON copied to clipboard!")

# Toon in console het gebouw
#print(json_str)
#print(Q1008.maak_automatenlijstlijn())
#print(Q1010.controleer_verlichting_veiligheid())
#toon_gebouwstructuur(gebouw1) #met de klantnaam



toon_automaten_per_bord(gebouw1)

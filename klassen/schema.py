
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
    def __init__(self, naam, pos= None, toevoervan = None, *args, **kwargs):
        self.naam = naam
        self.pos = pos
        self.toevoervan = toevoervan
        self.verdeelborden = []  # lijst voor Verdeelbord-objecten
        self.tellers = []        # lijst voor Teller-objecten
        self._args = args        # extra positional arguments
        self._extra_attrs = kwargs  # extra keyword arguments
        # Set extra attributes as instance variables
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_Verdeelbord(self, verdeelbord):
        if not isinstance(verdeelbord, Verdeelbord):
            raise ValueError("Only Verdeelbord instances can be added")
        self.verdeelborden.append(verdeelbord)

    def add_teller(self, teller):
        if not isinstance(teller, Teller):
            raise ValueError("Only Teller instances can be added")
        self.tellers.append(teller)

    def as_dict(self):
        # Start with the fixed attributes
        data = {
            'naam': self.naam,
            'pos': self.pos,
            'toevoervan': self.toevoervan,
        }
        # Insert args if present
        if self._args:
            data['args'] = self._args
        # Insert kwargs (extra attributes)
        data.update(self._extra_attrs)
        # Now add the object arrays
        data['verdeelborden'] = [vb.as_dict() for vb in self.verdeelborden]
        data['tellers'] = [t.as_dict() for t in self.tellers]
        return data

class Verlichting:
    def __init__(
        self, naam, locatie , soort=None, aantal=None, kabellijst=None, kabel=None,
        lengte=None, carre=None, driver=None, transfo=None,   *args, **kwargs
    ):
        self.naam = naam
        self.soort = soort
        self.aantal = aantal
        self.kabellijst = kabellijst
        self.kabel = kabel
        self.lengte = lengte
        self.carre = carre
        self.driver = driver
        self.transfo = transfo
        self.locatie = locatie
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self):
        data = {
            'naam': self.naam,
            'soort': self.soort,
            'aantal': self.aantal,
            'kabellijst': self.kabellijst,
            'kabel': self.kabel,
            'lengte': self.lengte,
            'carre': self.carre,
            'driver': self.driver,
            'transfo': self.transfo,
            'locatie': self.locatie,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        return data


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
    def __init__(self, naam, amp=None, polen=None, millies=None, type_=None, kA=None, *args, **kwargs):
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
        self.differentielen = []  # List for Differentieel objects
        self.priezen = []         # List for Prieze objects
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        data = {
            'naam': self.naam,
            'amp': self.amp,
            'polen': self.polen,
            'millies': self.millies,
            'type': self.type,
            'kA': self.kA,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Arrays at the bottom
        data['velbusmodules'] = [mod.as_dict() for mod in self.velbusmodules]
        data['contaxen'] = [ct.as_dict() for ct in self.ct_objects]
        data['toestellen'] = [toestel.as_dict() for toestel in self.toestellen]
        data['zekeringen'] = [zek.as_dict() for zek in self.zekeringen]
        data['differentielen'] = [diff.as_dict() for diff in self.differentielen]
        data['priezen'] = [p.as_dict() for p in self.priezen]
        return data
class Zekering:
    def __init__(self, naam, ka=None, amp=None, kabelonder=None, polen=None, *args, **kwargs):
        self.naam = naam
        self.ka = ka
        self.amp = amp
        self.kabelonder = kabelonder
        self.polen = polen
        self.velbusmodules = []   # List for VelbusModule objects
        self.ct_objects = []      # List for CT objects
        self.toestellen = []      # List for Toestel objects
        self.differentielen = []  # List for Differentieel objects
        self.priezen = []         # List for Prieze objects
        self.verlichtingen = []   # List for Verlichting objects
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def controleer_verlichting_veiligheid(self):
        verlichtingen = list(self.verlichtingen)
        for module in self.velbusmodules:
            for ch in module.subdevices:
                if isinstance(ch, VelbusRelay):
                    verlichtingen.extend(ch.verlichting)
        if verlichtingen and self.amp and self.amp > 16:
            return f" Waarschuwing: verlichting op zekering {self.naam} ({self.amp}A) > 16A!"
        else:
            return f" Zekering {self.naam} oké (verlichting of amp <= 16A)"

    def maak_automatenlijstlijn(self):
        onderdelen = []
        onderdelen.extend(ct.naam for ct in self.ct_objects)
        onderdelen.extend(prieze.naam for prieze in self.priezen)
        onderdelen.extend(toestel.naam for toestel in self.toestellen)
        onderdelen.extend(v.naam for v in self.verlichtingen)
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
        data = {
            'naam': self.naam,
            'ka': self.ka,
            'amp': self.amp,
            'kabelonder': self.kabelonder,
            'polen': self.polen,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Arrays at the bottom
        data['velbusmodules'] = [mod.as_dict() for mod in self.velbusmodules]
        data['contaxen'] = [ct.as_dict() for ct in self.ct_objects]
        data['toestellen'] = [toestel.as_dict() for toestel in self.toestellen]
        data['differentielen'] = [diff.as_dict() for diff in self.differentielen]
        data['priezen'] = [p.as_dict() for p in self.priezen]
        data['verlichtingen'] = [v.as_dict() for v in self.verlichtingen]
        return data

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
    def __init__(self, ean= None, amp = None, toevoerkabel=None, carre=None, spanning=None, polen=None, ohm=None, **kwargs):
        self.ean = ean                # EAN-nummer (uniek identificatienummer)
        self.amp = amp                # Stroomsterkte in ampère
        self.toevoerkabel = toevoerkabel  # bv. 'EXVB', 'H07RN-F', ...
        self.carre = carre            # doorsnede in mm²
        self.spanning = spanning      # spanning in volt (bijv. 230V/400V)
        self.polen = polen            # aantal polen (bijv. 1P, 3P)
        self.ohm = ohm                # aardingweerstand in ohm
        self.zekeringen = []
        self.differentielen = []
        self.hoofdschakelaars = []
        self.verdeelborden = []
        # Store extra attributes
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        # Start with the fixed attributes
        data = {
            'ean': self.ean,
            'amp': self.amp,
            'toevoerkabel': self.toevoerkabel,
            'carre': self.carre,
            'spanning': self.spanning,
            'polen': self.polen,
            'ohm': self.ohm,
        }
        # Insert extra attributes from kwargs here
        data.update(self._extra_attrs)
        # Add the list attributes at the end
        data['zekeringen'] = [zek.as_dict() for zek in self.zekeringen]
        data['differentielen'] = [diff.as_dict() for diff in self.differentielen]
        data['hoofdschakelaars'] = [hos.as_dict() for hos in self.hoofdschakelaars]
        data['verdeelborden'] = [vb.as_dict() for vb in self.verdeelborden]
        return data


class Verdeelbord:
    def __init__(self, naam, lokatie, kA, toevoerkabel=None, carre=None, lengte=None, **kwargs):
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
        # Store extra attributes
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        data = {
            'naam': self.naam,
            'lokatie': self.lokatie,
            'kA': self.kA,
            'toevoerkabel': self.toevoerkabel,
            'carre': self.carre,
            'lengte': self.lengte,
        }
        # Add extra attributes
        data.update(self._extra_attrs)
        # Add list attributes
        data['zekeringen'] = [zek.as_dict() for zek in self.zekeringen]
        data['differentielen'] = [diff.as_dict() for diff in self.differentielen]
        data['hoofdschakelaars'] = [hos.as_dict() for hos in self.hoofdschakelaars]
        data['verdeelborden'] = [vb.as_dict() for vb in self.verdeelborden]
        return data


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



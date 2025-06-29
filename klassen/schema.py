
import json
import subprocess #klembord schrijven
import platform #voor klembord

def print_paths_to_kabellijst(root, target_value, path=None, print_messages=True):
    """
    Recursively searches for objects where kabellijst matches target_value.
    Automatically prints a friendly message for each path found.
    If print_messages=False, it will collect and return the paths as a list of strings.
    """
    if path is None:
        path = []
    if print_messages is True:
        found = None
    else:
        found = []

    current_path = list(path)
    if hasattr(root, 'naam'):
        current_path = path + [getattr(root, 'naam')]

    if hasattr(root, 'kabellijst'):
        kabellijst = getattr(root, 'kabellijst')
        if (isinstance(kabellijst, (list, tuple)) and target_value in kabellijst) or \
           (isinstance(kabellijst, str) and target_value == kabellijst):
            path_str = ', '.join(current_path)
            msg = f"path naar kabellijst '{target_value}' is: {path_str}"
            if print_messages:
                print(msg)
            else:
                found.append(msg)

    if hasattr(root, '__dict__'):
        for attr, value in vars(root).items():
            if attr.startswith('_'):
                continue
            if isinstance(value, (list, tuple)):
                for item in value:
                    if print_messages:
                        print_paths_to_kabellijst(item, target_value, current_path)
                    else:
                        found.extend(
                            print_paths_to_kabellijst(item, target_value, current_path, False)
                        )
            elif isinstance(value, dict):
                for item in value.values():
                    if print_messages:
                        print_paths_to_kabellijst(item, target_value, current_path)
                    else:
                        found.extend(
                            print_paths_to_kabellijst(item, target_value, current_path, False)
                        )
            else:
                if print_messages:
                    print_paths_to_kabellijst(value, target_value, current_path)
                else:
                    found.extend(
                        print_paths_to_kabellijst(value, target_value, current_path, False)
                    )
    return found if not print_messages else None


def find_name_paths(root, target_name, path=None, found=None):
    """
    Recursively finds all objects with .naam == target_name, starting from root.
    Returns a list of lists, each containing the .naam values along the path.
    """
    if path is None:
        path = []
    if found is None:
        found = []

    # If the object has a .naam, add it to the current path
    current_path = list(path)
    if hasattr(root, 'naam'):
        current_path = path + [getattr(root, 'naam')]

    # If this is a match, add the path
    if hasattr(root, 'naam') and getattr(root, 'naam') == target_name:
        found.append(current_path)

    # Recursively search attributes
    if hasattr(root, '__dict__'):
        for attr, value in vars(root).items():
            if attr.startswith('_'):
                continue
            if isinstance(value, (list, tuple)):
                for item in value:
                    find_name_paths(item, target_name, current_path, found)
            elif isinstance(value, dict):
                for item in value.values():
                    find_name_paths(item, target_name, current_path, found)
            else:
                find_name_paths(value, target_name, current_path, found)
    return found



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

class Kring:
    def __init__(self, naam, **kwargs):
        self.naam = naam           # Required
        self.priezen = []          # List to hold Prieze objects
        self.max_priezen = 8       # Default maximum
        self._warned = False       # To avoid repeated warnings
        self._args = None          # For consistency with your example
        self._extra_attrs = kwargs # Store extra kwargs for as_dict
        # Add any extra kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_prieze(self, prieze):
        if len(self.priezen) >= self.max_priezen:
            if not self._warned:
                print(f"Waarschuwing: Kring '{self.naam}' kan maximaal {self.max_priezen} Prieze objecten bevatten!")
                self._warned = True
            return False
        self.priezen.append(prieze)
        return True

    def vullenmet(self, prieze, aantal):
        for _ in range(aantal):
            if not self.add_prieze(prieze):
                break

    def as_dict(self):
        data = {
            'naam': self.naam,
            'max_priezen': self.max_priezen,
            'priezen': [p.as_dict() for p in self.priezen]
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        return data

class Prieze:
    def __init__(self, naam, locatie=None, aantal=None, kabel=None, carre=None, lengte=None, kabellijst=None, *args, **kwargs):
        self.naam = naam
        self.locatie = locatie
        self.aantal = aantal
        self.kabel = kabel
        self.carre = carre
        self.lengte = lengte
        self.kabellijst = kabellijst
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self):
        data = {
            'naam': self.naam,
            'locatie': self.locatie,
            'aantal': self.aantal,
            'kabel': self.kabel,
            'carre': self.carre,
            'lengte': self.lengte,
            'kabellijst': self.kabellijst,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        return data

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
            'locatie': self.locatie,
            'soort': self.soort,
            'aantal': self.aantal,
            'kabellijst': self.kabellijst,
            'kabel': self.kabel,
            'lengte': self.lengte,
            'carre': self.carre,
            'driver': self.driver,
            'transfo': self.transfo,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        return data


class DomoModule:
    def __init__(self, naam, num_channels, channeltype, *args, **kwargs):
        self.naam = naam
        self.num_channels = num_channels
        self.channeltype = channeltype
        self.channels = [None] * num_channels
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_num_channels(self):
        return self.num_channels

    def as_dict(self):
        data = {
            'naam': self.naam,
            'num_channels': self.num_channels,
            'channeltype': self.channeltype,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)

        def serialize_channel(ch, idx):
            if ch is None:
                return None
            type_name = type(ch).__name__
            key = f"{type_name} {self.naam}.{idx}"
            if hasattr(ch, "as_dict") and callable(getattr(ch, "as_dict")):
                return {key: ch.as_dict()}
            else:
                return {key: repr(ch)}

        data['channels'] = [serialize_channel(ch, idx) for idx, ch in enumerate(self.channels)]
        return data




class DomoRelay:
    def __init__(self, channelid, code_HA=None, code_Caneco=None, kleur=None, *args, **kwargs):
        self.channelid = channelid
        self.code_HA = code_HA
        self.code_Caneco = code_Caneco
        self.kleur = kleur
        self.verlichting = []     # List for Verlichting objects
        self.ct_objects = []      # List for Contax objects
        self.priezen = []         # List for Prieze objects
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_verlichting(self, verlichting):
        if not isinstance(verlichting, Verlichting):
            raise ValueError("Only Verlichting instances can be added")
        self.verlichting.append(verlichting)

    def add_contax(self, contax):
        if not isinstance(contax, Contax):
            raise ValueError("Only Contax instances can be added")
        self.ct_objects.append(contax)

    def add_prieze(self, prieze):
        if not isinstance(prieze, Prieze):
            raise ValueError("Only Prieze instances can be added")
        self.priezen.append(prieze)

    def as_dict(self):
        data = {
            'channelid': self.channelid,
            'code_HA': self.code_HA,
            'code_Caneco': self.code_Caneco,
            'kleur': self.kleur,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Arrays at the bottom
        data['verlichting'] = [v.as_dict() for v in self.verlichting]
        data['contaxen'] = [ct.as_dict() for ct in self.ct_objects]
        data['priezen'] = [p.as_dict() for p in self.priezen]
        return data

class DomoContact:
    def __init__(self, naam, locatie=None, kabel=None, kleur=None, *args, **kwargs):
        self.naam = naam
        self.locatie = locatie
        self.kabel = kabel
        self.kleur = kleur
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self):
        data = {
            'naam': self.naam,
            'locatie': self.locatie,
            'kabel': self.kabel,
            'kleur': self.kleur,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        return data

class Differentieel:
    def __init__(self, naam, amp=None, polen=None, millies=None, type_=None, kA=None, *args, **kwargs):
        self.naam = naam
        self.amp = amp
        self.polen = polen
        self.millies = millies
        self.type = type_
        self.kA = kA
        self.domomodules = []   # List for domoModule objects
        self.ct_objects = []      # List for Contax objects
        self.toestellen = []      # List for Toestel objects
        self.zekeringen = []      # List for Zekering objects
        self.differentielen = []  # List for Differentieel objects
        self.priezen = []         # List for Prieze objects
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_domomodule(self, module):
        if not isinstance(module, DomoModule):
            raise ValueError("Only DomoModule instances can be added")
        self.domomodules.append(module)

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
        data['domomodules'] = [mod.as_dict() for mod in self.domomodules]
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
        self.domomodules = []
        self.ct_objects = []
        self.toestellen = []
        self.differentielen = []
        self.priezen = []
        self.verlichtingen = []
        self.kringen = []  # NEW: Container for Kring objects
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def controleer_verlichting_veiligheid(self):
        verlichtingen = list(self.verlichtingen)
        for module in self.domomodules:
            for ch in module.subdevices:
                if isinstance(ch, DomoRelay):
                    verlichtingen.extend(ch.verlichting)
        if verlichtingen and self.amp and self.amp > 16:
            return f" Waarschuwing: verlichting op zekering {self.naam} ({self.amp}A) > 16A!"
        else:
            return f" Zekering {self.naam} oké (verlichting of amp <= 16A)"

    def maak_automatenlijstlijn(self):
        onderdelen = []
        onderdelen.extend(ct.naam for ct in self.ct_objects if hasattr(ct, 'naam'))
        onderdelen.extend(prieze.naam for prieze in self.priezen if hasattr(prieze, 'naam'))
        onderdelen.extend(toestel.naam for toestel in self.toestellen if hasattr(toestel, 'naam'))
        onderdelen.extend(v.naam for v in self.verlichtingen if hasattr(v, 'naam'))

        for mod in self.domomodules:
            for ch in getattr(mod, 'channels', []):
                if ch is None:
                    continue
                # Add the channel's name if it has one
                if hasattr(ch, 'naam'):
                    onderdelen.append(ch.naam)
                # If this channel is a DomoRelay with verlichting, add those names too
                if hasattr(ch, 'verlichting'):
                    onderdelen.extend(v.naam for v in getattr(ch, 'verlichting', []) if hasattr(v, 'naam'))

        prefix = f"{self.naam} {self.polen}P {self.amp}A:"
        return f"{prefix} " + ", ".join(onderdelen)

    def add_verlichting(self, verlichting):
        if not isinstance(verlichting, Verlichting):
            raise ValueError("Only Verlichting instances can be added")
        self.verlichtingen.append(verlichting)

    def add_domomodule(self, module):
        if not isinstance(module, DomoModule):
            raise ValueError("Only DomoModule instances can be added")
        self.domomodules.append(module)

    def add_ct(self, ct):
        if not isinstance(ct, Contax):
            raise ValueError("Only Contax instances can be added")
        self.ct_objects.append(ct)

    def add_contax(self, contax):
        if not isinstance(contax, Contax):
            raise ValueError("Only Contax instances can be added")
        self.ct_objects.append(contax)

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

    def add_kring(self, kring):  # NEW: Add this method
        """Add a Kring object to this Zekering"""
        if not isinstance(kring, Kring):
            raise ValueError("Only Kring instances can be added")
        self.kringen.append(kring)

    def as_dict(self):
        # Start with the fixed attributes
        data = {
            'naam': self.naam,
            'ka': self.ka,
            'amp': self.amp,
            'kabelonder': self.kabelonder,
            'polen': self.polen,
        }
        # Add args and extra attrs (from kwargs)
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Add all other non-private attributes, except the special lists and underscore-prefixed
        special_lists = [
            'domomodules', 'ct_objects', 'toestellen', 'differentielen',
            'priezen', 'verlichtingen', 'kringen',
        ]
        for attr, value in self.__dict__.items():
            if (attr not in data and
                    not attr.startswith('_') and
                    attr not in special_lists):
                data[attr] = value
        # Serialize the lists of objects
        data['domomodules'] = [mod.as_dict() for mod in self.domomodules]
        data['contaxen'] = [ct.as_dict() for ct in self.ct_objects]
        data['toestellen'] = [toestel.as_dict() for toestel in self.toestellen]
        data['differentielen'] = [diff.as_dict() for diff in self.differentielen]
        data['priezen'] = [p.as_dict() for p in self.priezen]
        data['verlichtingen'] = [v.as_dict() for v in self.verlichtingen]
        data['kringen'] = [k.as_dict() for k in self.kringen]
        return data


class Contax:
    def __init__(self, naam, spoel_van=None, contact_op=None, *args, **kwargs):
        self.naam = naam
        self.spoel_van = spoel_van
        self.contact_op = contact_op
        self.domomodules = []
        self.priezen = []
        self.verlichtingen = []  # NEW: List for verlichtingen
        self._args = args
        self._extra_attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_domomodule(self, module):
        if not isinstance(module, DomoModule):
            raise ValueError("Only DomoModule instances can be added")
        self.domomodules.append(module)

    def add_prieze(self, prieze):
        if not isinstance(prieze, Prieze):
            raise ValueError("Only Prieze instances can be added")
        self.priezen.append(prieze)

    def add_verlichting(self, verlichting):
        if not isinstance(verlichting, Verlichting):
            raise ValueError("Only Verlichting instances can be added")
        self.verlichtingen.append(verlichting)


    def as_dict(self):
        data = {
            'naam': self.naam,
            'spoel_van': self.spoel_van,
            'contact_op': self.contact_op,
        }
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Arrays at the bottom
        data['domomodules'] = [mod.as_dict() for mod in self.domomodules]
        data['priezen'] = [p.as_dict() for p in self.priezen]
        data['verlichtingen'] = [v.as_dict() for v in self.verlichtingen]  # NEW: Include verlichtingen
        return data

class Teller:
    def __init__(self, naam, ean=None, amp=None, toevoerkabel=None, carre=None, spanning=None, polen=None, ohm=None, *args, **kwargs):
        self.naam = naam                # Naam van de teller (required)
        self.ean = ean                  # EAN-nummer (uniek identificatienummer)
        self.amp = amp                  # Stroomsterkte in ampère
        self.toevoerkabel = toevoerkabel  # bv. 'EXVB', 'H07RN-F', ...
        self.carre = carre              # doorsnede in mm²
        self.spanning = spanning        # spanning in volt (bijv. 230V/400V)
        self.polen = polen              # aantal polen (bijv. 1P, 3P)
        self.ohm = ohm                  # aardingweerstand in ohm
        self.zekeringen = []
        self.differentielen = []
        self.hoofdschakelaars = []
        self.verdeelborden = []
        self._args = args
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
              f"Teller: '{self.naam}'\t >>"
              f"Sub-verdeelbord: '{verdeelbord.naam}' (locatie: {verdeelbord.lokatie})\n\n")
        self.verdeelborden.append(verdeelbord)

    def as_dict(self):
        # Start with the fixed attributes
        data = {
            'naam': self.naam,
            'ean': self.ean,
            'amp': self.amp,
            'toevoerkabel': self.toevoerkabel,
            'carre': self.carre,
            'spanning': self.spanning,
            'polen': self.polen,
            'ohm': self.ohm,
        }
        # Add args and extra attrs (from kwargs)
        if self._args:
            data['args'] = self._args
        data.update(self._extra_attrs)
        # Add all other non-private attributes, except lists
        for attr, value in self.__dict__.items():
            if (attr not in data and
                    not attr.startswith('_') and
                    attr not in ['zekeringen', 'differentielen', 'hoofdschakelaars', 'verdeelborden']):
                data[attr] = value
        # Add the lists of objects
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
    def __init__(self, naam, locatie=None ,aansluiting=None, kabel=None, carre=None, lengte=None, bibu=None, kabellijst=None, **kwargs):
        self.naam = naam                # Required
        self.aansluiting = aansluiting  # Optional
        self.kabel = kabel              # Optional
        self.carre = carre              # Optional
        self.lengte = lengte            # Optional
        self.bibu = bibu                # Optional
        self.kabellijst = kabellijst    # Optional
        self.locatie = locatie          # Optional (new)
        # Add any extra kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self):
        # Start with fixed attributes
        data = {
            'naam': self.naam,
            'aansluiting': self.aansluiting,
            'kabel': self.kabel,
            'carre': self.carre,
            'lengte': self.lengte,
            'bibu': self.bibu,
            'kabellijst': self.kabellijst,
            'locatie': self.locatie
        }
        # Add any dynamically added attributes (from kwargs)
        for attr, value in self.__dict__.items():
            if attr not in data and not attr.startswith('_'):
                data[attr] = value
        return data



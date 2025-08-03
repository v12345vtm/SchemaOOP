import pandas as pd
from bigtree import Node


import re

def natural_key(name):
    # Split string into list of strings and ints to allow natural numeric ordering
    parts = re.split(r'(\d+)', name)
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key

# ---- Component classes ----

class Component(Node):
    def __init__(self, name, node_type="generic", **kwargs):
        super().__init__(name)
        self.node_type = node_type
        for k, v in kwargs.items():
            # Clean up leading/trailing spaces from all values
            if isinstance(v, str):
                v = v.strip()
            setattr(self, k, v)

    @property
    def display_name(self):
        """A custom property to format the node's display string for the tree."""
        attrs_to_show = []
        # Attributes to display in the tree view
        key_attrs = ['amp', 'millies', 'polen', 'tiepe',  'wat' , 'naar', 'lengte']

        for attr in key_attrs:
            val = getattr(self, attr, None)
            if val is not None and not (isinstance(val, float) and pd.isna(val)) and str(val).strip() != "":
                attrs_to_show.append(f"{attr}={val}")

        base = f"{self.name}"
        if attrs_to_show:
            base += " (" + " | ".join(attrs_to_show) + ")"
        return base

    def __repr__(self):
        # This will now be used by default if show() is called without arguments
        return self.display_name

    def summarize(self):
        """Returns a detailed, multi-line summary of the node."""
        # This function remains the same as before
        fields = []
        parent_display = None
        if hasattr(self, "parent_name"):
            parent_raw = getattr(self, "parent_name")
            if parent_raw is not None and not (isinstance(parent_raw, float) and pd.isna(parent_raw)):
                parent_display = str(parent_raw).strip()

        for k, v in vars(self).items():
            if k in ['name', 'node_type', 'parent', '_parent', '_children', 'parent_name', 'display_name']:
                continue
            if k.startswith('_'):
                continue
            if v is not None and not (isinstance(v, float) and pd.isna(v)) and str(v).strip() != "":
                fields.append(f"{k}={v}")

        base = f"{self.name}: {self.node_type}"
        if parent_display:
            base += f" | parent={parent_display}"
        if fields:
            return base + " | " + " | ".join(fields)
        else:
            return base

# ... (The rest of your classes: Teller, Toestel, Zekering, etc. remain unchanged) ...
class Teller(Component):
    def __init__(self, name, polen=None, amp=None, opmerking=None, **kwargs):
        super().__init__(name, "Teller", polen=polen, amp=amp, opmerking=opmerking, **kwargs)

class Toestel(Component):
    def __init__(self, name, aansluitpunt=None, opmerking=None, **kwargs):
        super().__init__(name, "Toestel", aansluitpunt=aansluitpunt, opmerking=opmerking, **kwargs)


class Prieze(Component):
    def __init__(self, name, locatie=None, enk_dubb=None, hydro=None, schak=None, aarding=None, kinder=None, parent=None, **kwargs):
        super().__init__(name, "Prieze",
                         locatie=locatie, enk_dubb=enk_dubb, hydro=hydro,
                         schak=schak, aarding=aarding, kinder=kinder,
                         parent_name=parent, **kwargs)  # keep raw parent for now



class ContaxContact(Component):
    def __init__(self, name, part_type, parent_name, opmerking=None, **kwargs):
        # part_type: "spoel" or "contact"
        comp_name = f"{name}_{part_type}"
        node_type = f"ContaxContact_{part_type}"
        # Save original name for potential use
        super().__init__(comp_name, node_type=node_type, opmerking=opmerking, **kwargs)
        self.original = name
        self.part_type = part_type
        self.parent_name = parent_name  # Used for delayed assignment

    def summarize(self):
        return f"{self.name}: {self.node_type} | parent={self.parent_name} | opmerking={getattr(self, 'opmerking', '')}"


class Zekering(Component):
    def __init__(self, name, polen=None, amp=None, kiloamp=None, tiepe=None, opmerking=None, **kwargs):
        super().__init__(name, "Zekering", polen=polen, amp=amp, kiloamp=kiloamp, tiepe=tiepe, opmerking=opmerking, **kwargs)

    def create_zekeringenoverzicht(self):
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)

        # INLINE integer conversion for float or int (and blank if missing)
        polen_str = ""
        if polen is not None and not (isinstance(polen, float) and pd.isna(polen)):
            try:
                polen_str = str(int(float(polen)))
            except Exception:
                polen_str = str(polen)
        amp_str = ""
        if amp is not None and not (isinstance(amp, float) and pd.isna(amp)):
            try:
                amp_str = str(int(float(amp)))
            except Exception:
                amp_str = str(amp)

        prefix = ""
        if polen_str and amp_str:
            prefix = f"= {polen_str}P {amp_str}A "
        elif polen_str:
            prefix = f"({polen_str}P) "
        elif amp_str:
            prefix = f"({amp_str}A) "

        pairs = self._collect_kabel_pairs(self)
        if not pairs:
            return f"{self.name} {prefix}= _"
        concatenated = " / ".join(pairs)
        return f"{self.name} {prefix}= {concatenated}"



    def _collect_kabel_pairs(self, node):
        """Recursively collect all wat/naar pairs from Kabel descendants."""
        pairs = []
        for child in node.children:
            # If it's a Kabel, collect its wat/naar
            if isinstance(child, Kabel):
                van = getattr(child, 'wat', None)
                naar = getattr(child, 'naar', None)
                van_str = str(van).strip() if van and not (isinstance(van, float) and pd.isna(van)) else ""
                naar_str = str(naar).strip() if naar and not (isinstance(naar, float) and pd.isna(naar)) else ""
                if van_str or naar_str:
                    pairs.append(f"{van_str} {naar_str}".strip())
            # Regardless of type, continue recursively!
            pairs.extend(self._collect_kabel_pairs(child))
        return pairs

    def oudfloeat_create_zekeringenoverzicht(self):
        # Prepare polen and amp strings if available
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)
        polen_str = str(polen).strip() if polen is not None and not (
                    isinstance(polen, float) and pd.isna(polen)) else ""
        amp_str = str(amp).strip() if amp is not None and not (isinstance(amp, float) and pd.isna(amp)) else ""

        prefix = ""
        if polen_str and amp_str:
            prefix = f"= {polen_str}P {amp_str}A "
        elif polen_str:
            prefix = f"({polen_str}P) "
        elif amp_str:
            prefix = f"({amp_str}A) "

        # Use the recursive function to gather all pairs
        pairs = self._collect_kabel_pairs(self)

        # If pairs is empty (no Kabels with wat/naar found), underscore line with prefix
        if not pairs:
            return f"{self.name} {prefix}= _"

        concatenated = " / ".join(pairs)
        return f"{self.name} {prefix}= {concatenated}"



    def oudcreate_zekeringenoverzicht(self):
        # Prepare polen and amp strings if available
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)

        polen_str = str(polen).strip() if polen is not None and not (
                    isinstance(polen, float) and pd.isna(polen)) else ""
        amp_str = str(amp).strip() if amp is not None and not (isinstance(amp, float) and pd.isna(amp)) else ""

        prefix = ""
        if polen_str and amp_str:
            prefix = f"= {polen_str}P {amp_str}A "
        elif polen_str:
            prefix = f"({polen_str}P) "
        elif amp_str:
            prefix = f"({amp_str}A) "

        # If no children, return underscore line with prefix
        if not self.children:
            return f"{self.name} {prefix}= _"

        pairs = []
        for child in self.children:
            van = getattr(child, 'wat', None)
            naar = getattr(child, 'naar', None)

            van_str = str(van).strip() if van and not (isinstance(van, float) and pd.isna(van)) else ""
            naar_str = str(naar).strip() if naar and not (isinstance(naar, float) and pd.isna(naar)) else ""

            # Only add if at least one of van or naar is present
            if van_str or naar_str:
                pairs.append(f"{van_str} {naar_str}".strip())

        # If pairs is empty (no valid van/naar), return line with prefix and empty right side
        if not pairs:
            return f"{self.name} {prefix}="

        concatenated = " / ".join(pairs)
        return f"{self.name} {prefix}= {concatenated}"


class Kabel(Component):
    def __init__(self, name, puntje=None, aders=None, tiepe=None, van=None, wat=None, naar=None, lengte=None, opmerk=None, **kwargs):
        super().__init__(name, "Kabel", puntje=puntje, aders=aders, tiepe=tiepe, van=van, wat=wat, naar=naar, lengte=lengte, opmerk=opmerk, **kwargs)


class Differentieel(Component):
    def __init__(self, name, polen=None, amp=None, millies=None, kiloamp=None, kiloamp_1=None, diftype=None, opmerking=None, **kwargs):
        super().__init__(name, "Differentieel", polen=polen, amp=amp, millies=millies, kiloamp=kiloamp, kiloamp_1=kiloamp_1, diftype=diftype, opmerking=opmerking, **kwargs)



    def oudfloat_create_automatelijst(self):
        # Prepare polen, amp, millies strings for the differentieel itself
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)
        millies = getattr(self, 'millies', None)

        polen_str = str(polen).strip() if polen and not (isinstance(polen, float) and pd.isna(polen)) else ""
        amp_str = str(amp).strip() if amp and not (isinstance(amp, float) and pd.isna(amp)) else ""
        millies_str = str(millies).strip() if millies and not (isinstance(millies, float) and pd.isna(millies)) else ""

        diff_line_parts = []
        if polen_str:
            diff_line_parts.append(f"{polen_str}p")
        if amp_str:
            diff_line_parts.append(f"{amp_str}A")
        if millies_str:
            diff_line_parts.append(f"{millies_str}ma")

        diff_line = f"{self.name} = {' '.join(diff_line_parts)}"
        lines = [diff_line]

        for child in sorted(self.children, key=lambda x: natural_key(x.name)):
            if isinstance(child, Zekering):
                # Prepare Zekering prefix for polen and amp
                zk_polen = getattr(child, 'polen', None)
                zk_amp = getattr(child, 'amp', None)
                zk_polen_str = str(zk_polen).strip() if zk_polen and not (isinstance(zk_polen, float) and pd.isna(zk_polen)) else ""
                zk_amp_str = str(zk_amp).strip() if zk_amp and not (isinstance(zk_amp, float) and pd.isna(zk_amp)) else ""

                zk_prefix = ""
                if zk_polen_str and zk_amp_str:
                    zk_prefix = f"{zk_polen_str}P {zk_amp_str}A"
                elif zk_polen_str:
                    zk_prefix = f"{zk_polen_str}P"
                elif zk_amp_str:
                    zk_prefix = f"{zk_amp_str}A"

                # Use recursive Kabel collector here:
                pairs = child._collect_kabel_pairs(child)

                if not pairs:
                    line = f"{child.name} = {zk_prefix} = _"
                else:
                    concatenated = " / ".join(pairs)
                    line = f"{child.name} = {zk_prefix} = {concatenated}"

                lines.append(line)

        return "\n".join(lines)



    def create_automatelijst(self):
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)
        millies = getattr(self, 'millies', None)

        # Inline int conversion for main differentieel line
        def intify_val(val):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            try:
                f = float(val)
                if f.is_integer():
                    return str(int(f))
                return str(f)
            except Exception:
                return str(val)

        polen_str = intify_val(polen)
        amp_str = intify_val(amp)
        millies_str = intify_val(millies)

        diff_line_parts = []
        if polen_str:
            diff_line_parts.append(f"{polen_str}p")
        if amp_str:
            diff_line_parts.append(f"{amp_str}A")
        if millies_str:
            diff_line_parts.append(f"{millies_str}ma")

        diff_line = f"{self.name} = {' '.join(diff_line_parts)}"
        lines = [diff_line]

        # Recursive kabel collector (inline)
        def collect_kabel_pairs(node):
            pairs = []
            for child in node.children:
                if isinstance(child, Kabel):
                    van = getattr(child, 'wat', None)
                    naar = getattr(child, 'naar', None)
                    van_str = str(van).strip() if van and not (isinstance(van, float) and pd.isna(van)) else ""
                    naar_str = str(naar).strip() if naar and not (isinstance(naar, float) and pd.isna(naar)) else ""
                    if van_str or naar_str:
                        pairs.append(f"{van_str} {naar_str}".strip())
                pairs.extend(collect_kabel_pairs(child))
            return pairs

        for child in sorted(self.children, key=lambda x: natural_key(x.name)):
            if isinstance(child, Zekering):
                zk_polen = getattr(child, 'polen', None)
                zk_amp = getattr(child, 'amp', None)

                # Inline int conversion for Zekering polen and amp
                zk_polen_str = ""
                if zk_polen is not None and not (isinstance(zk_polen, float) and pd.isna(zk_polen)):
                    try:
                        f = float(zk_polen)
                        zk_polen_str = str(int(f)) if f.is_integer() else str(f)
                    except Exception:
                        zk_polen_str = str(zk_polen)

                zk_amp_str = ""
                if zk_amp is not None and not (isinstance(zk_amp, float) and pd.isna(zk_amp)):
                    try:
                        f = float(zk_amp)
                        zk_amp_str = str(int(f)) if f.is_integer() else str(f)
                    except Exception:
                        zk_amp_str = str(zk_amp)

                zk_prefix = ""
                if zk_polen_str and zk_amp_str:
                    zk_prefix = f"{zk_polen_str}P {zk_amp_str}A"
                elif zk_polen_str:
                    zk_prefix = f"{zk_polen_str}P"
                elif zk_amp_str:
                    zk_prefix = f"{zk_amp_str}A"

                pairs = collect_kabel_pairs(child)

                if not pairs:
                    line = f"{child.name} = {zk_prefix} = _"
                else:
                    concatenated = " / ".join(pairs)
                    line = f"{child.name} = {zk_prefix} = {concatenated}"

                lines.append(line)

        return "\n".join(lines)

    def oudcreate_automatelijst(self):
        # Prepare polen, amp, millies strings for the differentieel itself
        polen = getattr(self, 'polen', None)
        amp = getattr(self, 'amp', None)
        millies = getattr(self, 'millies', None)

        polen_str = str(polen).strip() if polen and not (isinstance(polen, float) and pd.isna(polen)) else ""
        amp_str = str(amp).strip() if amp and not (isinstance(amp, float) and pd.isna(amp)) else ""
        millies_str = str(millies).strip() if millies and not (isinstance(millies, float) and pd.isna(millies)) else ""

        diff_line_parts = []
        if polen_str:
            diff_line_parts.append(f"{polen_str}p")
        if amp_str:
            diff_line_parts.append(f"{amp_str}A")
        if millies_str:
            diff_line_parts.append(f"{millies_str}ma")

        diff_line = f"{self.name} = {' '.join(diff_line_parts)}"
        lines = [diff_line]

        # Sort children naturally by name
        for child in sorted(self.children, key=lambda x: natural_key(x.name)):
            if isinstance(child, Zekering):
        # ... rest remains same ...

        # For each child Zekering, create its atomatenlijst line (reuse that method if exists!)

                # We reuse the create_atomatenlijst logic but omit the Differentieel prefix
                # So generate line without the Zekering name prefix, just right side of "="

                # Prepare Zekering prefix for polen and amp
                zk_polen = getattr(child, 'polen', None)
                zk_amp = getattr(child, 'amp', None)
                zk_polen_str = str(zk_polen).strip() if zk_polen and not (isinstance(zk_polen, float) and pd.isna(zk_polen)) else ""
                zk_amp_str = str(zk_amp).strip() if zk_amp and not (isinstance(zk_amp, float) and pd.isna(zk_amp)) else ""

                zk_prefix = ""
                if zk_polen_str and zk_amp_str:
                    zk_prefix = f"{zk_polen_str}P {zk_amp_str}A"
                elif zk_polen_str:
                    zk_prefix = f"{zk_polen_str}P"
                elif zk_amp_str:
                    zk_prefix = f"{zk_amp_str}A"

                # Collect 'wat' and 'naar' pairs of zk children
                pairs = []
                for c_child in child.children:
                    van = getattr(c_child, 'wat', None)
                    naar = getattr(c_child, 'naar', None)
                    van_str = str(van).strip() if van and not (isinstance(van, float) and pd.isna(van)) else ""
                    naar_str = str(naar).strip() if naar and not (isinstance(naar, float) and pd.isna(naar)) else ""
                    if van_str or naar_str:
                        pairs.append(f"{van_str} {naar_str}".strip())

                if not pairs:
                    # no valid van/naar = underscore
                    line = f"{child.name} = {zk_prefix} = _"
                else:
                    concatenated = " / ".join(pairs)
                    line = f"{child.name} = {zk_prefix} = {concatenated}"

                lines.append(line)

            else:
                # Could handle other child types if needed
                pass

        return "\n".join(lines)


# ---- Sheet-to-Class mapping ----
SHEET_TO_CLASS = {
    "Teller": Teller,
    "Toestel": Toestel,
    "Zekering": Zekering,
    "Kabel": Kabel,
    "Differentieel": Differentieel,
    "Domomodule": Component, # Handle typo
    "ContaxContact": ContaxContact,
    "Prieze": Prieze,
    "Component": Component,
}


def oudbuild_tree_from_excel(file_path):
    # This function remains the same
    xls = pd.ExcelFile(file_path)
    all_nodes = {}

    for sheet in xls.sheet_names:
        if sheet not in SHEET_TO_CLASS:
            print(f"Skipping unknown sheet: {sheet}")
            continue

        Cls = SHEET_TO_CLASS[sheet]
        df = pd.read_excel(xls, sheet)
        df.columns = df.columns.str.strip()

        for idx, row in df.iterrows():
            name = row.get('naam')
            if pd.isna(name) or str(name).strip() == "":
                continue
            name = str(name).strip()
            kwargs = {col: row.get(col) for col in df.columns if col not in ['naam', 'parent']}
            node = Cls(name, **kwargs)

            parent_val = row.get('parent')
            node._parent_tmp = parent_val
            node.parent_name = parent_val

            all_nodes[name] = node

    for node in all_nodes.values():
        parent_name = getattr(node, "_parent_tmp", None)
        if parent_name is not None and not (isinstance(parent_name, float) and pd.isna(parent_name)) and str(parent_name).strip() != "":
            parent_name_str = str(parent_name).strip()
            if parent_name_str in all_nodes:
                node.parent = all_nodes[parent_name_str]
            else:
                print(f"WARNING: Parent '{parent_name_str}' not found for node '{node.name}'")
        delattr(node, "_parent_tmp")

    roots = [node for node in all_nodes.values() if node.parent is None and len(node.children) > 0]
    return all_nodes, roots


def build_tree_from_excel(file_path):
    xls = pd.ExcelFile(file_path)
    all_nodes = {}

    for sheet in xls.sheet_names:
        if sheet not in SHEET_TO_CLASS:
            print(f"Skipping unknown sheet: {sheet}")
            continue

        Cls = SHEET_TO_CLASS[sheet]
        df = pd.read_excel(xls, sheet)
        df.columns = df.columns.str.strip()

        # Handle ContaxContact separately if needed (from your earlier code)
        if sheet == "ContaxContact":
            # Special case: each row becomes two nodes!
            for idx, row in df.iterrows():
                name = row.get('naam')
                if pd.isna(name) or str(name).strip() == "":
                    continue
                name = str(name).strip()
                opmerking = row.get('opmerking')
                # 1. spoel node
                spoel_parent = row.get('spoel_parent')
                spoel_node = Cls(name, part_type="spoel", parent_name=spoel_parent, opmerking=opmerking)
                spoel_node._parent_tmp = spoel_parent
                all_nodes[f"{name}_spoel"] = spoel_node
                # 2. contact node
                contact_parent = row.get('parent')
                contact_node = Cls(name, part_type="contact", parent_name=contact_parent, opmerking=opmerking)
                contact_node._parent_tmp = contact_parent
                all_nodes[f"{name}_contact"] = contact_node
        else:
            for idx, row in df.iterrows():
                name = row.get('naam')
                if pd.isna(name) or str(name).strip() == "":
                    continue
                name = str(name).strip()
                kwargs = {col: row.get(col) for col in df.columns if col not in ['naam', 'parent']}
                parent_val = row.get('parent')
                # Sentinel logic for parent splitting:
                parent_str = None
                if isinstance(parent_val, str):
                    parent_str = parent_val.strip()
                    if '.' in parent_str:
                        parent_str = parent_str.split('.', 1)[0]  # get part before '.'

                # Create the node instance with all other kwargs
                node = Cls(name, **kwargs)
                node._parent_tmp = parent_str
                node.parent_name = parent_val  # raw for summary
                all_nodes[name] = node

    # After creating nodes, assign their parents
    for node in all_nodes.values():
        parent_name = getattr(node, "_parent_tmp", None)
        if parent_name is not None and not (isinstance(parent_name, float) and pd.isna(parent_name)) and str(parent_name).strip() != "":
            parent_name_str = str(parent_name).strip()
            if parent_name_str in all_nodes:
                node.parent = all_nodes[parent_name_str]
            else:
                print(f"WARNING: Parent '{parent_name_str}' not found for node '{node.name}'")
        delattr(node, "_parent_tmp")

    roots = [node for node in all_nodes.values() if node.parent is None and len(node.children) > 0]
    return all_nodes, roots


def geenPrieze_build_tree_from_excel(file_path):
    xls = pd.ExcelFile(file_path)
    all_nodes = {}

    for sheet in xls.sheet_names:
        if sheet not in SHEET_TO_CLASS:
            print(f"Skipping unknown sheet: {sheet}")
            continue
        Cls = SHEET_TO_CLASS[sheet]
        df = pd.read_excel(xls, sheet)
        df.columns = df.columns.str.strip()

        if sheet == "ContaxContact":
            # Special case: each row becomes two nodes!
            for idx, row in df.iterrows():
                name = row.get('naam')
                if pd.isna(name) or str(name).strip() == "":
                    continue
                name = str(name).strip()
                opmerking = row.get('opmerking')
                # 1. spoel node
                spoel_parent = row.get('spoel_parent')
                spoel_node = Cls(name, part_type="spoel", parent_name=spoel_parent, opmerking=opmerking)
                spoel_node._parent_tmp = spoel_parent
                all_nodes[f"{name}_spoel"] = spoel_node
                # 2. contact node
                contact_parent = row.get('parent')
                contact_node = Cls(name, part_type="contact", parent_name=contact_parent, opmerking=opmerking)
                contact_node._parent_tmp = contact_parent
                all_nodes[f"{name}_contact"] = contact_node
        else:
            # Normal single-node handling
            for idx, row in df.iterrows():
                name = row.get('naam')
                if pd.isna(name) or str(name).strip() == "":
                    continue
                name = str(name).strip()
                kwargs = {col: row.get(col) for col in df.columns if col not in ['naam', 'parent']}
                node = Cls(name, **kwargs)
                parent_val = row.get('parent')
                node._parent_tmp = parent_val
                node.parent_name = parent_val
                all_nodes[name] = node

    # Fix up parents for ALL nodes (including ContaxContact)
    for node in all_nodes.values():
        parent_name = getattr(node, "_parent_tmp", None)
        if parent_name is not None and not (isinstance(parent_name, float) and pd.isna(parent_name)) and str(parent_name).strip() != "":
            parent_name_str = str(parent_name).strip()
            # The parent might be either a "main" name or a ..._contact or ..._spoel; always try both
            if parent_name_str in all_nodes:
                node.parent = all_nodes[parent_name_str]
            elif f"{parent_name_str}_spoel" in all_nodes:
                node.parent = all_nodes[f"{parent_name_str}_spoel"]
            elif f"{parent_name_str}_contact" in all_nodes:
                node.parent = all_nodes[f"{parent_name_str}_contact"]
            else:
                print(f"WARNING: Parent '{parent_name_str}' not found for node '{node.name}'")
        delattr(node, "_parent_tmp")
    roots = [node for node in all_nodes.values() if node.parent is None and len(node.children) > 0]
    return all_nodes, roots


# ==== Main execution ====
if __name__ == "__main__":
    file_path = "input.xlsx"

    nodes, roots = build_tree_from_excel(file_path)

    print("\n--- All nodes summaries ---")
    for node in nodes.values():
        print(node.summarize())

    print("\n--- Tree(s) from root node(s) ---")
    for root in roots:
        print(f"Root: {root.name} ({root.node_type})")
        # **THIS IS THE KEY CHANGE**
        # We tell show() to use our new 'display_name' property for the tree labels.
        root.show(attr_list=["display_name"])

    # Example 1: Using the method on each Zekering node
    print("\nzekeringenoverzicht from all Zekering nodes:")
    for node in nodes.values():
        if isinstance(node, Zekering):
            out = node.create_zekeringenoverzicht()
            if out:
                print(out)


    print("\nAutomatenlijst from Differentieel nodes:")
    for node in nodes.values():
        if isinstance(node, Differentieel):
            print(node.create_automatelijst())
            print()  # blank line for readability between differentiels


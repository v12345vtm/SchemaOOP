import json

# Load your JSON once globally
with open('root_json_str.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


def find_all_elements(element_name):
    found = []

    def recurse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == element_name and isinstance(value, list):
                    found.extend(value)
                    for item in value:
                        recurse(item)
                else:
                    recurse(value)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(data)
    return found

def find_all_elements_with_parent(element_name, parent_name):
    found = []
    def recurse(obj, parent=None):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == element_name and isinstance(value, list):
                    # Check if parent dict has the key 'parent_name'
                    if parent and parent_name in parent:
                        found.extend(value)
                    for item in value:
                        recurse(item, obj)
                else:
                    recurse(value, obj)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, parent)
    recurse(data, None)
    return found



def find_child_and_kleinkinderen(element_name, parent_key):
    """
    Find all child_key en kleinkinderen lists that are direct values of parent_key in the JSON,
    meaning only child_key lists that are immediate children of parent_key.
    """
    found = []

    def recurse(obj, parent=None):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == element_name and isinstance(value, list):
                    # Check if immediate parent dict has the parent_key
                    if parent and parent_key in parent:
                        found.extend(value)
                # Recurse deeper, passing current obj as parent
                recurse(value, obj)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, parent)

    recurse(data, None)
    return found

def find_directe_kinderen(parent_key, child_key):
    """
    Find all child_key lists that are direct values of parent_key in the JSON,
    meaning only child_key lists that are immediate children of parent_key.
    """
    found = []

    def recurse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # If this key is the parent key and its value is a list of dicts
                if key == parent_key and isinstance(value, list):
                    # Look for child_key in each dict directly inside this list
                    for item in value:
                        if isinstance(item, dict) and child_key in item:
                            child_value = item.get(child_key)
                            if isinstance(child_value, list):
                                found.extend(child_value)
                else:
                    recurse(value)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(data)
    return found


# Example usage:
all_differentielen = find_all_elements("differentielen")
print(f"Found {len(all_differentielen)} 'differentielen':")
for diff in all_differentielen:
    print(" -", diff.get("naam"))

all_tellers = find_all_elements("tellers")
print(f"\nFound {len(all_tellers)} 'tellers':")
for teller in all_tellers:
    print(" -", teller.get("naam"))


all_diffs_under_teller = find_all_elements_with_parent("differentielen", "verdeelborden")
print(f"Found {len(all_diffs_under_teller)} 'differentielen' inside parents containing 'tellers'")
for diff in all_diffs_under_teller:
    print(" -", diff.get("naam"))



diffs_under_tellers = find_child_and_kleinkinderen("differentielen", "verdeelborden")
print(f"Found {len(diffs_under_tellers)} 'differentielen' with immediate parent containing 'verdeelborden'")
for diff in diffs_under_tellers:
    print(" -", diff.get("naam"))


diffs_directly_under_verdeelborden = find_directe_kinderen("verdeelborden", "differentielen")
print(f"Found {len(diffs_directly_under_verdeelborden)} 'differentielen' directly under 'verdeelborden':")
for diff in diffs_directly_under_verdeelborden:
    print(" -", diff.get("naam"))

# jsonontleder.py

def find_all_elements(jsonbestand, element_name):
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

    recurse(jsonbestand)
    return found


def find_all_elements_with_parent(jsonbestand, element_name, parent_name):
    found = []

    def recurse(obj, parent=None):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == element_name and isinstance(value, list):
                    if parent and parent_name in parent:
                        found.extend(value)
                    for item in value:
                        recurse(item, obj)
                else:
                    recurse(value, obj)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, parent)
    recurse(jsonbestand, None)
    return found


def find_child_and_kleinkinderen(jsonbestand, element_name, parent_key):
    """
    Find all element_name lists that are immediate children of any dict containing parent_key.
    """
    found = []

    def recurse(obj, parent=None):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == element_name and isinstance(value, list):
                    if parent and parent_key in parent:
                        found.extend(value)
                recurse(value, obj)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, parent)

    recurse(jsonbestand, None)
    return found


def find_directe_kinderen(jsonbestand, parent_key, child_key):
    """
    Find all child_key lists that are immediate children of parent_key lists.
    """
    found = []

    def recurse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == parent_key and isinstance(value, list):
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

    recurse(jsonbestand)
    return found

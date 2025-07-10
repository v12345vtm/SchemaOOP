# components.py
import re

class Component:
    def __init__(self, label, type,  **kwargs):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = "horizontal"   # "horizontal" or "vertical"
        self.COMPONENT_SIZE = 20  # Default size, can be parameterized
        self.stack_on_top_of_brother = False  # New attribute!
        self.allow_stack_on_top_of_parent  = False  # Default behavior
        self.kwargs = kwargs  # Store all extra arguments in a dict

        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)




    @property
    def stroomrichting(self):
        return self._stroomrichting

    @stroomrichting.setter
    def stroomrichting(self, value):
        if value not in ("horizontal", "vertical"):
            raise ValueError("stroomrichting must be 'horizontal' or 'vertical'")
        self._stroomrichting = value

    @property
    def connectionpoint_input(self):
        if self.x is None or self.y is None:
            return None
        if self.stroomrichting == "horizontal":
            # Input is left center
            return (self.x, self.y + self.COMPONENT_SIZE // 2)
        else:
            # Input is bottom center
            return (self.x + self.COMPONENT_SIZE // 2, self.y)

    @property
    def connectionpoint_output(self):
        if self.x is None or self.y is None:
            return None
        if self.stroomrichting == "horizontal":
            # Output is right center
            return (self.x + self.COMPONENT_SIZE, self.y + self.COMPONENT_SIZE // 2)
        else:
            # Output is top center
            return (self.x + self.COMPONENT_SIZE // 2, self.y + self.COMPONENT_SIZE)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def add_child(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    def sort_children(self):
        """Sort children by number in label, fallback to alphabetical."""
        self.children.sort(key=lambda c: (Component.extract_int(c.label), c.label))
        for child in self.children:
            child.sort_children()

    def print_ascii_tree(self, prefix=""):
        print(f"{prefix}{self.label} ({self.x},{self.y})")
        for i, child in enumerate(self.children):
            connector = "└── " if i == len(self.children) - 1 else "├── "
            child_prefix = prefix + ("    " if i == len(self.children) - 1 else "│   ")
            print(f"{prefix}{connector}", end="")
            child.print_ascii_tree(child_prefix)

    @staticmethod
    def extract_int(label):
        """Extract the first integer found in the label, or return inf if not found."""
        match = re.search(r'\d+', label)
        return int(match.group()) if match else float('inf')

    @staticmethod
    def assign_coords_safe_stacking(component, depth=0, counter=[0], occupied=None):
        if occupied is None:
            occupied = set()

        if component.parent is None:
            component.x = counter[0]
            component.y = depth
            occupied.add((component.x, component.y))
            counter[0] += 1
        else:
            parent = component.parent
            siblings = parent.children
            index = siblings.index(component)

            def is_invalid_stack_on_parent():
                return (
                    component.allow_stack_on_top_of_parent and
                    parent.stroomrichting == "vertical" and
                    component.stroomrichting == "horizontal"
                )

            def is_invalid_stack_on_brother(prev_sibling):
                return (
                    component.stack_on_top_of_brother and
                    prev_sibling.stroomrichting == "vertical" and
                    component.stroomrichting == "horizontal"
                )

            if index == 0:
                if component.allow_stack_on_top_of_parent and not is_invalid_stack_on_parent():
                    component.x = parent.x
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                else:
                    component.x = counter[0]
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                    counter[0] += 1
            else:
                prev_sibling = siblings[index - 1]
                if component.stack_on_top_of_brother and not is_invalid_stack_on_brother(prev_sibling):
                    component.x = prev_sibling.x
                    component.y = prev_sibling.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                else:
                    component.x = counter[0]
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                    counter[0] += 1

        for child in component.children:
            Component.assign_coords_safe_stacking(child, depth + 1, counter, occupied)

# Subclasses
class Differential(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True
        self.stroomrichting = "vertical"

class CircuitBreaker(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True
        self.stroomrichting = "vertical"

class Appliance(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting="horizontal"

class Domomodule(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Contax(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Verlichting(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Voeding(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"

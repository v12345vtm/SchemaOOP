class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.x = None
        self.y = None

def assign_increasing_x(node, depth=0, counter=[0]):
    node.y = depth
    node.x = counter[0]
    counter[0] += 1
    for child in node.children:
        assign_increasing_x(child, depth+1, counter)

def print_ascii_tree(node, prefix=""):
    print(f"{prefix}{node.name} ({node.x},{node.y})")
    for i, child in enumerate(node.children):
        connector = "└── " if i == len(node.children) - 1 else "├── "
        child_prefix = prefix + ("    " if i == len(node.children) - 1 else "│   ")
        print(f"{prefix}{connector}", end="")
        print_ascii_tree(child, child_prefix)

# Build your example tree
root = Node("Root", [
    Node("Child 1", [
        Node("Grandchild 1"),
        Node("Grandchild 2")
    ]),
    Node("Child 2")
])

# Assign coordinates and print
assign_increasing_x(root)
print_ascii_tree(root)

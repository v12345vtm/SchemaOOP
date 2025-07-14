import json

with open("tree.json") as f:
    data = json.load(f)

def assign_coords_tree(tree):
    used_coords = set()
    column_directions = {}

    def assign_coords(node, x, y):
        # Find next valid (x, y) that is unused and has consistent stroomrichting
        while (x, y) in used_coords or (x in column_directions and column_directions[x] != node['stroomrichting']):
            y += 1

        # Assign coordinates
        node['x'] = x
        node['y'] = y
        used_coords.add((x, y))
        column_directions.setdefault(x, node['stroomrichting'])

        children = node.get("children", [])
        if not children:
            return

        if node['stroomrichting'] == 'vertical':
            horiz_children = [c for c in children if c['stroomrichting'] == 'horizontal']
            vert_children = [c for c in children if c['stroomrichting'] == 'vertical']

            # First handle vertical children: stack below parent
            for i, child in enumerate(vert_children):
                assign_coords(child, x, y + i + 1)

            # Then horizontal children: first at (x+1, y+1), stack further up
            for j, child in enumerate(horiz_children):
                assign_coords(child, x + 1, y + 1 + j)

        elif node['stroomrichting'] == 'horizontal':
            horiz_children = [c for c in children if c['stroomrichting'] == 'horizontal']
            vert_children = [c for c in children if c['stroomrichting'] == 'vertical']

            # Horizontal child: spread right
            for i, child in enumerate(horiz_children):
                assign_coords(child, x + i + 1, y)

            # Vertical child: start one below and to the right
            for j, child in enumerate(vert_children):
                assign_coords(child, x + j + 1, y + 1)

    # Start recursion at root
    assign_coords(tree, 0, 0)
    return tree


updated = assign_coords_tree(data)

# To inspect or save it:
print(json.dumps(updated, indent=2))

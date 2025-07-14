class Component:
    def __init__(self, id, label, type, x_mm, y_mm, **kwargs):
        self.id = id
        self.label = label
        self.type = type
        self.x_mm = x_mm
        self.y_mm = y_mm
        self.connections = []  # List of other Component objects this is connected to
        # Any additional properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_connection(self, other_component):
        self.connections.append(other_component)

    def draw(self, c=None):
        # Placeholder for drawing logic, to be overridden by subclasses
        print(f"Drawing {self.type} '{self.label}' at ({self.x_mm},{self.y_mm})")

    def __repr__(self):
        return f"<{self.type.capitalize()} {self.label} at ({self.x_mm},{self.y_mm})>"

class Differential(Component):
    def __init__(self, id, label, x_mm, y_mm, rating, **kwargs):
        super().__init__(id, label, "differential", x_mm, y_mm, rating=rating, **kwargs)

    def draw(self, c=None):
        print(f"Drawing Differential '{self.label}' ({self.rating}) at ({self.x_mm},{self.y_mm})")

class CircuitBreaker(Component):
    def __init__(self, id, label, x_mm, y_mm, rating, circuit, **kwargs):
        super().__init__(id, label, "circuit_breaker", x_mm, y_mm, rating=rating, circuit=circuit, **kwargs)

    def draw(self, c=None):
        print(f"Drawing CircuitBreaker '{self.label}' ({self.rating}, {self.circuit}) at ({self.x_mm},{self.y_mm})")

class Appliance(Component):
    def __init__(self, id, label, x_mm, y_mm, **kwargs):
        super().__init__(id, label, "appliance", x_mm, y_mm, **kwargs)

    def draw(self, c=None):
        print(f"Drawing Appliance '{self.label}' at ({self.x_mm},{self.y_mm})")

if __name__ == "__main__":
    # Create components
    diff1 = Differential(1, "Diff1", 20, 150, "300mA")
    breakerA = CircuitBreaker(2, "BreakerA", 60, 150, "16A", "Vaatwas")
    diff2 = Differential(3, "Diff2", 100, 150, "30mA")
    breakerB = CircuitBreaker(4, "BreakerB", 140, 150, "16A", "Keuken")
    vaatwas = Appliance(5, "Vaatwas", 60, 100)
    keuken = Appliance(6, "KeukenStop", 140, 100)

    # Connect components (nested)
    diff1.add_connection(breakerA)
    breakerA.add_connection(diff2)
    diff2.add_connection(breakerB)
    breakerA.add_connection(vaatwas)
    breakerB.add_connection(keuken)

    # Store all in a list for iteration
    components = [diff1, breakerA, diff2, breakerB, vaatwas, keuken]

    # Example: Print all components and their connections
    for comp in components:
        print(f"{comp} connects to {[c.label for c in comp.connections]}")

    # Example: Draw all components (stub)
    for comp in components:
        comp.draw()

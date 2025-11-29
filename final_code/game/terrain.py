import abc

# Abstract base class representing terrain types with movement, water, and food costs plus a color.
class Terrain(abc.ABC):
    """
    Base terrain with costs. Initialize terrain costs and display color.
    """
    def __init__(self, movement_cost, water_cost, food_cost, color):
        self.movement_cost = movement_cost
        self.water_cost = water_cost
        self.food_cost = food_cost
        self.color = color

# Plains terrain with low movement, water, and food costs and a light green color.
class Plains(Terrain):
    # Construct a Plains terrain with preset cost and color values.
    def __init__(self): super().__init__(1, 1, 1, "#a7c957")

# Forest terrain with higher movement and food costs and a dark green color.
class Forest(Terrain):
    # Construct a Forest terrain with preset cost and color values.
    def __init__(self): super().__init__(2, 1, 2, "#386641")

# Mountain terrain with very high movement cost and a gray color.
class Mountain(Terrain):
    # Construct a Mountain terrain with preset cost and color values.
    def __init__(self): super().__init__(4, 2, 1, "#6a707c")

# Desert terrain with moderate movement cost, high water cost, and a sandy color.
class Desert(Terrain):
    # Construct a Desert terrain with preset cost and color values.
    def __init__(self): super().__init__(2, 4, 1, "#f2e8cf")

# Swamp terrain with elevated movement and water costs and a murky color.
class Swamp(Terrain):
    # Construct a Swamp terrain with preset cost and color values.
    def __init__(self): super().__init__(3, 2, 1, "#585123")
import abc

class Terrain(abc.ABC):
    """
    Base terrain with costs.
    """
    def __init__(self, movement_cost, water_cost, food_cost, color):
        self.movement_cost = movement_cost
        self.water_cost = water_cost
        self.food_cost = food_cost
        self.color = color

class Plains(Terrain):
    def __init__(self): super().__init__(1, 1, 1, "#a7c957")

class Forest(Terrain):
    def __init__(self): super().__init__(2, 1, 2, "#386641")

class Mountain(Terrain):
    def __init__(self): super().__init__(4, 2, 1, "#6a707c")

class Desert(Terrain):
    def __init__(self): super().__init__(2, 4, 1, "#f2e8cf")

class Swamp(Terrain):
    def __init__(self): super().__init__(3, 2, 1, "#585123")
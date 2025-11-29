import abc
import random

class Item(abc.ABC):
    """
    Base item on the map.
    """
    def __init__(self, is_repeating, symbol):
        self.is_repeating = is_repeating
        self.symbol = symbol

    @abc.abstractmethod
    def on_collect(self, player, gui_logger):
        pass

class FoodBonus(Item):
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "F")
        self.amount = random.randint(5, 15)
    def on_collect(self, p, log):
        p.current_food = min(p.max_food, p.current_food + self.amount)
        log(f"Found {self.amount} food.")

class WaterBonus(Item):
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "W")
        self.amount = random.randint(5, 15)
    def on_collect(self, p, log):
        p.current_water = min(p.max_water, p.current_water + self.amount)
        log(f"Found {self.amount} water.")

class GoldBonus(Item):
    def __init__(self):
        super().__init__(False, "G")
        self.amount = random.randint(1, 10)
    def on_collect(self, p, log):
        p.current_gold += self.amount
        log(f"Found {self.amount} gold.")
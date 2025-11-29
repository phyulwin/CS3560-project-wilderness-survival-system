import abc
import random

# Abstract base class for items that can appear on the map
class Item(abc.ABC):
    """
    Base item on the map.
    Initialize common item properties like repeatability and symbol
    """
    def __init__(self, is_repeating, symbol):
        self.is_repeating = is_repeating
        self.symbol = symbol

    # Called when a player collects the item; must be implemented by subclasses
    @abc.abstractmethod
    def on_collect(self, player, gui_logger):
        pass

# Consumable item that restores a random amount of food
class FoodBonus(Item):
    # Create a food bonus with a random amount and the "F" symbol
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "F")
        self.amount = random.randint(5, 15)

    # Apply the food restore to the player and log the event
    def on_collect(self, p, log):
        p.current_food = min(p.max_food, p.current_food + self.amount)
        log(f"Found {self.amount} food.")

# Consumable item that restores a random amount of water
class WaterBonus(Item):
    # Create a water bonus with a random amount and the "W" symbol
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "W")
        self.amount = random.randint(5, 15)

    # Apply the water restore to the player and log the event
    def on_collect(self, p, log):
        p.current_water = min(p.max_water, p.current_water + self.amount)
        log(f"Found {self.amount} water.")

# Collectible item that gives a random amount of gold
class GoldBonus(Item):
    # Create a gold bonus with a random amount and the "G" symbol
    def __init__(self):
        super().__init__(False, "G")
        self.amount = random.randint(1, 10)

    # Add gold to the player's inventory and log the event
    def on_collect(self, p, log):
        p.current_gold += self.amount
        log(f"Found {self.amount} gold.")
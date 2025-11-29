import abc
from game.items import Item

# Trader item that triggers a transaction when collected
class Trader(Item):
    """
    Base Trader class.
    Traders act as items that trigger a transaction when collected.
    """
    # Initialize trader item with name, symbol, and display color
    def __init__(self, name, symbol, color):
        # Traders are repeating (don't disappear immediately)
        super().__init__(is_repeating=True, symbol=symbol)
        self.name = name
        self.color = color

    # Abstract trading method to determine if trade succeeds and cost
    @abc.abstractmethod
    def negotiate(self, player_gold, base_cost):
        """
        Abstract method for trading logic.
        Returns: (success: bool, message: str, final_cost: int)
        """
        pass
    
    # Handle player collecting trader: negotiate and apply trade effects
    def on_collect(self, player, log_func):
        # Standard trade: Buy supplies (Food/Water refuel)
        base_cost = 10
        success, msg, cost = self.negotiate(player.current_gold, base_cost)
        
        if success:
            player.current_gold -= cost
            # Refuel player
            player.current_food = min(player.max_food, player.current_food + 20)
            player.current_water = min(player.max_water, player.current_water + 20)
            log_func(f"[{self.name}] Deal! {msg} (-{cost} G)")
        else:
            log_func(f"[{self.name}] {msg}")

# --- 2 Types of Traders (Max Points: 20) ---

# Trader that offers a discount to the player
class FriendlyTrader(Trader):
    """Offers discounts to the player."""
    # Create a friendly trader with name, symbol, and color
    def __init__(self):
        super().__init__("Friendly Merchant", "T", "#2ecc71") # Green
    
    # Apply discount logic and check player gold
    def negotiate(self, player_gold, base_cost):
        # Friendly logic: Offers a discount
        discounted = max(1, base_cost - 3)
        if player_gold >= discounted:
            return True, "Here's a discount for a traveler.", discounted
        return False, "I'd help, but you have no gold.", 0

# Trader that demands higher price or rejects trade
class GreedyTrader(Trader):
    """Demands a markup or rejects the trade."""
    # Create a greedy trader with name, symbol, and color
    def __init__(self):
        super().__init__("Greedy Goblin", "$", "#f1c40f") # Gold
        
    # Apply markup logic and determine trade outcome
    def negotiate(self, player_gold, base_cost):
        # Greedy logic: Adds a markup (Counteroffer)
        markup = base_cost + 5
        
        if player_gold >= markup:
            return True, "Heh heh... pleasure doing business.", markup
        elif player_gold >= base_cost:
            # Counteroffer rejection
            return False, f"Price is {markup}! Don't lowball me!", 0
        else:
            return False, "Get away, pauper!", 0
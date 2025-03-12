import random

class Card:
    """Represents a single card in the deck."""
    def __init__(self, suit: str, rank: str, point_value: int):
        self.suit = suit
        self.rank = rank
        self.point_value = point_value

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    """Represents a deck of cards, handles shuffling and dealing."""
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    RANKS = ["Ace", "Ten", "King", "Queen", "Jack", "Nine", "Eight", "Seven", "Six"]
    POINT_VALUES = {"Ace": 11, "Ten": 10, "King": 4, "Queen": 3, "Jack": 2,
                    "Nine": 0, "Eight": 0, "Seven": 0, "Six": 0}
    
    def __init__(self):
        self.cards = [Card(suit, rank, self.POINT_VALUES[rank]) for suit in self.SUITS for rank in self.RANKS]
        self.cards.append(Card("Joker", "Joker", 0))  # Add the Joker card

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def deal(self, num_players=3, cards_per_player=12):
        """Deal cards to players."""
        hands = {i: [] for i in range(num_players)}
        for i in range(cards_per_player):
            for player in range(num_players):
                if self.cards:
                    hands[player].append(self.cards.pop(0))
        return hands

    def reveal_trump(self):
        """Reveal the last card as the trump suit."""
        if self.cards:
            trump_card = self.cards.pop(0)
            return trump_card
        return None


class Player:
    """Represents a player in the game."""
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.bid = None
        self.score = 0

    def receive_cards(self, cards):
        """Assign dealt cards to the player."""
        self.hand = cards

    def display_hand(self):
        """Display player's hand in a structured format."""
        print(f"\n{self.name}'s Hand:")
        for i, card in enumerate(self.hand, 1):
            print(f"{i}. {card}")
        print("=" * 25)


# Initial Setup
if __name__ == "__main__":
    print("Initializing CounterPoint Game...\n")

    # Display Legend
    print("**Card Point Values:**")
    print("Ace = 11 | Ten = 10 | King = 4 | Queen = 3 | Jack = 2 | Nine-Eight-Seven-Six = 0")
    print("=" * 40, "\n")

    # Create deck and shuffle
    deck = Deck()
    deck.shuffle()

  # Get player names from input
    player_names = []
    for i in range(3):
        name = input(f"Enter name for Player {i + 1}: ").strip()
        while not name:
            print("Name cannot be empty. Please enter a valid name.")
            name = input(f"Enter name for Player {i + 1}: ").strip()
        player_names.append(name)

    # Create players with input names
    players = [Player(name) for name in player_names]

    # Deal cards
    hands = deck.deal(num_players=len(players), cards_per_player=12)
    for i, player in enumerate(players):
        player.receive_cards(hands[i])
        player.display_hand()

    # Reveal trump card
    trump_card = deck.reveal_trump()
    print(f"\nTrump Card: {trump_card if trump_card else 'No Trump (Joker or Nine)'}")
    print("\nSetup complete. Ready for bidding phase!")

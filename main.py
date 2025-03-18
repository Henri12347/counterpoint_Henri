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

# Bidding Phase
print("\nBidding Phase: Each player must discard 3 cards to set their bid.")
bids = {}

for player in players:
    print(f"\n{player.name}'s Turn to Bid:")
    player.display_hand()

    discarded_cards = []
    for i in range(3):
        while True:
            try:
                choice = int(input(f"Select a card to discard (1-{len(player.hand)}): ")) - 1
                if 0 <= choice < len(player.hand):
                    discarded_cards.append(player.hand.pop(choice))
                    break
                else:
                    print("Invalid choice, select a valid card number.")
            except ValueError:
                print("Please enter a valid number.")

    # Calculate bid based on discarded cards' suits
    bid_value = sum(10 if card.suit == "Spades" else 20 if card.suit == "Hearts"
                    else 30 if card.suit == "Clubs" else 0 for card in discarded_cards)

    bids[player.name] = bid_value
    player.bid = bid_value

    print(f"{player.name} bid {bid_value} points.")
    print("=" * 25)

# Turn Management
turn_index = 0



# Trick-Taking Phase
print("\nTrick-Taking Phase Begins!")

tricks_won = {player.name: 0 for player in players}

for trick in range(9):  # 9 tricks per round
    print(f"\n--- Trick {trick + 1} ---")
    played_cards = []

    # Each player plays a card
    for i, player in enumerate(players):
        print(f"\n{player.name}'s Turn:")
        player.display_hand()
        
        while True:
            try:
                choice = int(input(f"Select a card to play (1-{len(player.hand)}): ")) - 1
                if 0 <= choice < len(player.hand):
                    played_card = player.hand.pop(choice)
                    played_cards.append((player, played_card))
                    print(f"{player.name} played {played_card}")
                    break
                else:
                    print("Invalid choice, select a valid card number.")
            except ValueError:
                print("Please enter a valid number.")

    # Determine trick winner
    lead_suit = played_cards[0][1].suit
    highest_card = played_cards[0]
    
    for player, card in played_cards[1:]:
        if card.suit == lead_suit and card.point_value > highest_card[1].point_value:
            highest_card = (player, card)
        elif trump_card and card.suit == trump_card.suit and highest_card[1].suit != trump_card.suit:
            highest_card = (player, card)

    winner = highest_card[0]
    tricks_won[winner.name] += 1
    print(f"\n{winner.name} wins Trick {trick + 1} with {highest_card[1]}!")

# Display results
print("\n--- Trick-Taking Phase Complete! ---")
for player in players:
    print(f"{player.name} won {tricks_won[player.name]} tricks.")

# Final Scoring Phase
print("\n--- Final Scoring Phase ---")
differences = {}

# Calculate differences between bid and tricks won
for player in players:
    bid = player.bid
    tricks = tricks_won[player.name] * 10  # Each trick is worth 10 card-points
    difference = abs(bid - tricks)
    differences[player.name] = difference  # Store difference for scoring
    print(f"{player.name} bid {bid}, won {tricks} card-points. Difference: {difference}")

# Calculate final scores
for player in players:
    print(f"\nCalculating score for {player.name}:")
    opponent_diffs = [differences[opponent.name] for opponent in players if opponent != player]
    base_score = sum(opponent_diffs)
    print(f"Sum of opponents' differences: {' + '.join(map(str, opponent_diffs))} = {base_score}")

    # Apply bonuses
    bonus = 0
    if differences[player.name] == 0:
        bonus = 30
        print(f"Bonus: Exact bid made (+30)")
    elif differences[player.name] <= 2:
        bonus = 20
        print(f"Bonus: Within 2 card-points (+20)")
    elif differences[player.name] <= 5:
        bonus = 10
        print(f"Bonus: Within 5 card-points (+10)")
    
    total_score = base_score + bonus
    player.score += total_score
    print(f"Final score for {player.name}: {base_score} + {bonus} = {total_score}")

# Determine Winner
winner = max(players, key=lambda p: p.score)
print(f"\n🏆 {winner.name} is the winner with {winner.score} points! 🏆")

# Dealer Rotation
players.append(players.pop(0))  # Move dealer to the end of the list
print(f"\nNext round dealer: {players[0].name}")

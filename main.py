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
        self.round_score = 0  # Track score per round

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

    # Get Winning Condition from Player
    print("\nChoose the winning condition:")
    print("1. First player to reach a target score")
    print("2. Play a set number of rounds")
    while True:
        try:
            win_condition = int(input("Enter 1 or 2: "))
            if win_condition in [1, 2]:
                break
            print("Invalid choice. Enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

    # If score-based win, get target score
    if win_condition == 1:
        while True:
            try:
                target_score = int(input("Enter target score to win: "))
                if target_score > 0:
                    break
                print("Target score must be a positive number.")
            except ValueError:
                print("Please enter a valid number.")

    # If round-based win, get number of rounds (must be 1 or a multiple of 3)
    elif win_condition == 2:
        while True:
            try:
                max_rounds = int(input("Enter number of rounds to play (1 or multiple of 3): "))
                if max_rounds == 1 or (max_rounds > 0 and max_rounds % 3 == 0):
                    break
                print("Number of rounds must be 1 or a positive number divisible by 3.")
            except ValueError:
                print("Please enter a valid number.")

    # Initialize game variables
    current_round = 1
    game_over = False

    while not game_over:
        # Reset round scores for each player
        for player in players:
            player.round_score = 0
            
        print(f"\n=== Round {current_round} Begins! ===")
        
        # Reset deck and hands for new round
        deck = Deck()
        deck.shuffle()
        hands = deck.deal(num_players=len(players), cards_per_player=12)
        for i, player in enumerate(players):
            player.receive_cards(hands[i])
            player.display_hand()
        
        # Reveal new trump card
        trump_card = deck.reveal_trump()
        print(f"\nTrump Card: {trump_card if trump_card else 'No Trump (Joker or Nine)'}")
        print("\nSetup complete. Ready for bidding phase!")

        # Bidding Phase
        print("\nBidding Phase: Each player must discard 3 cards to set their bid.")
        bids = {}

        for player in players:
            print(f"\n{player.name}'s Turn to Bid:")
            player.display_hand()

            # Keep track of card positions with a dictionary mapping position to card
            card_positions = {i+1: card for i, card in enumerate(player.hand)}
            discarded_positions = []  # Track which positions have been discarded
            discarded_cards = []

            for i in range(3):
                while True:
                    try:
                        choice = int(input(f"Select a card to discard (1-12): "))
                        if choice in card_positions and choice not in discarded_positions:
                            discarded_cards.append(card_positions[choice])
                            discarded_positions.append(choice)
                            break
                        elif choice in discarded_positions:
                            print(f"You have already discarded card {choice}. Please choose another card.")
                        else:
                            print("Invalid choice, select a valid card number (1-12).")
                    except ValueError:
                        print("Please enter a valid number.")

            # Remove discarded cards from player's hand
            player.hand = [card for position, card in card_positions.items() 
                          if position not in discarded_positions]

            # Calculate bid based on discarded cards' suits
            bid_value = sum(10 if card.suit == "Spades" else 20 if card.suit == "Hearts"
                            else 30 if card.suit == "Clubs" else 0 for card in discarded_cards)

            bids[player.name] = bid_value
            player.bid = bid_value

            print(f"{player.name} bid {bid_value} points.")
            print("=" * 25)

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
                
                # Create a mapping of positions to cards for this trick
                card_positions = {i+1: card for i, card in enumerate(player.hand)}
                
                while True:
                    try:
                        choice = int(input(f"Select a card to play (1-{len(player.hand)}): "))
                        if 1 <= choice <= len(player.hand):
                            played_card = card_positions[choice]
                            player.hand.remove(played_card)  # Remove by card object, not by index
                            played_cards.append((player, played_card))
                            print(f"{player.name} played {played_card}")
                            break
                        else:
                            print(f"Invalid choice, select a valid card number (1-{len(player.hand)}).")
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
            
            round_score = base_score + bonus
            player.round_score = round_score
            player.score += round_score
            print(f"Round score for {player.name}: {base_score} + {bonus} = {round_score}")

        # Round winner (based on round_score, not total score)
        round_winner = max(players, key=lambda p: p.round_score)
        print(f"\n🏆 Round winner: {round_winner.name} with {round_winner.round_score} points this round! 🏆")

        # Display all player scores
        print("\nCurrent Total Scores:")
        for player in players:
            print(f"{player.name}: {player.score} points")

        # Check Winning Condition
        if win_condition == 1:  # Score-based win
            players_over_target = [player for player in players if player.score >= target_score]
            if players_over_target:
                # If multiple players reached the target, find the one with highest score
                if len(players_over_target) > 1:
                    # Sort by score (highest first)
                    players_over_target.sort(key=lambda p: p.score, reverse=True)
                    # Check if there's a tie for highest score
                    if players_over_target[0].score == players_over_target[1].score:
                        tied_players = [p.name for p in players_over_target 
                                       if p.score == players_over_target[0].score]
                        print(f"\n🏆 Game ended in a draw between {', '.join(tied_players)} " 
                              f"with the score of: {players_over_target[0].score} 🏆")
                    else:
                        # One clear winner with highest score
                        winner = players_over_target[0]
                        print(f"\n🏆 {winner.name} has reached {target_score} points with a total of "
                              f"{winner.score} and wins the game! 🏆")
                else:
                    # Just one player reached the target
                    winner = players_over_target[0]
                    print(f"\n🏆 {winner.name} has reached {target_score} points with a total of "
                          f"{winner.score} and wins the game! 🏆")
                game_over = True
        elif win_condition == 2 and current_round >= max_rounds:  # Round-based win
            # Find players with the highest score
            max_score = max(player.score for player in players)
            winners = [player for player in players if player.score == max_score]
            
            if len(winners) > 1:
                # Multiple players tied for highest score
                tied_players = [p.name for p in winners]
                print(f"\n🏆 After {max_rounds} rounds, game ended in a draw between "
                      f"{', '.join(tied_players)} with the score of: {max_score} 🏆")
            else:
                # One clear winner
                final_winner = winners[0]
                print(f"\n🏆 After {max_rounds} rounds, {final_winner.name} wins with {final_winner.score} points! 🏆")
            game_over = True

        if not game_over:
            # Rotate dealer
            players.append(players.pop(0))
            print(f"\nNext round dealer: {players[0].name}")
            current_round += 1
            
            # Add pause between rounds
            print("\n" + "="*50)
            input("Press Enter when you're ready to start the next round... ")
            print("="*50)
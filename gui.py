import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os
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
        self.cards.append(Card("Joker", "Joker", 0))

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
        self.round_score = 0

    def receive_cards(self, cards):
        """Assign dealt cards to the player."""
        self.hand = cards


class CounterPointGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CounterPoint")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.card_images = []
        self.player_names = ["Player 1", "Player 2", "Player 3"]
        self.players = []
        self.trump_card = None
        self.deck = None
        self.current_round = 1
        self.game_over = False
        self.current_player_index = 0
        self.tricks_won = {}
        self.bids = {}
        self.current_trick = []
        self.current_phase = "welcome"
        self.target_score = None
        self.max_rounds = None
        self.win_condition = None
        self.discarded_cards = []
        self.discard_count = 0
        self.current_trick_number = 1
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.current_phase = "welcome"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        welcome_frame = tk.Frame(self.root)
        welcome_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(welcome_frame, text="CounterPoint", font=("Arial", 24, "bold")).pack(pady=20)
        
        tk.Button(welcome_frame, text="Start Game", font=("Arial", 14),
                  command=self.get_game_settings, width=15, height=2).pack(pady=10)
        
        tk.Button(welcome_frame, text="Game Rules", font=("Arial", 14),
                  command=self.show_help, width=15, height=2).pack(pady=10)
        
        tk.Button(welcome_frame, text="Exit", font=("Arial", 14),
                  command=self.root.destroy, width=15, height=2).pack(pady=10)

    def get_game_settings(self):
        for i in range(3):
            name = simpledialog.askstring("Player Names", f"Enter name for Player {i+1}:", parent=self.root)
            if name:
                self.player_names[i] = name
            else:
                self.player_names[i] = f"Player {i+1}"

        win_dialog = tk.Toplevel(self.root)
        win_dialog.title("Winning Condition")
        win_dialog.geometry("300x200")
        win_dialog.transient(self.root)
        win_dialog.grab_set()

        tk.Label(win_dialog, text="Choose the winning condition:", font=("Arial", 12)).pack(pady=10)
        tk.Button(win_dialog, text="Target Score", command=lambda: self.set_win_condition(1, win_dialog)).pack(pady=5)
        tk.Button(win_dialog, text="Set Rounds", command=lambda: self.set_win_condition(2, win_dialog)).pack(pady=5)

    def set_win_condition(self, condition, dialog):
        self.win_condition = condition
        dialog.destroy()
        
        if condition == 1:
            while True:
                score = simpledialog.askinteger("Target Score", "Enter target score to win:", parent=self.root)
                if score and score > 0:
                    self.target_score = score
                    break
                messagebox.showerror("Error", "Target score must be a positive number.")
        elif condition == 2:
            while True:
                rounds = simpledialog.askinteger("Number of Rounds", "Enter number of rounds (1 or multiple of 3):", parent=self.root)
                if rounds and (rounds == 1 or (rounds > 0 and rounds % 3 == 0)):
                    self.max_rounds = rounds
                    break
                messagebox.showerror("Error", "Number of rounds must be 1 or a positive number divisible by 3.")
        
        self.initialize_game()

    def initialize_game(self):
        self.players = [Player(name) for name in self.player_names]
        self.start_round()

    def start_round(self):
        self.current_phase = "setup"
        for player in self.players:
            player.round_score = 0
        self.deck = Deck()
        self.deck.shuffle()
        hands = self.deck.deal(num_players=3, cards_per_player=12)
        for i, player in enumerate(self.players):
            player.receive_cards(hands[i])
        self.trump_card = self.deck.reveal_trump()
        self.tricks_won = {player.name: 0 for player in self.players}
        self.bids = {}
        self.current_trick = []
        self.current_trick_number = 1
        self.current_player_index = 0
        self.select_trump_card()

    def select_trump_card(self):
        self.current_phase = "trump"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        trump_frame = tk.Frame(self.root)
        trump_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(trump_frame, text=f"Round {self.current_round} - Trump Card", font=("Arial", 20, "bold")).pack(pady=20)
        
        rank = self.trump_card.rank
        suit = self.trump_card.suit if self.trump_card.suit != "Joker" else None
        
        card_frame = tk.Frame(trump_frame)
        card_frame.pack(pady=20)
        
        img = self.load_card_image(rank, suit, size=(100, 150))
        if img:
            self.card_images.append(img)
            tk.Label(card_frame, image=img).pack()
        else:
            tk.Label(card_frame, text=str(self.trump_card), width=10, height=15, relief="raised", bg="white", font=("Arial", 12)).pack()
        
        info_text = "No trump suit this round!" if (rank == "Nine" or rank == "Joker") else f"The trump suit is: {suit.upper()}"
        tk.Label(trump_frame, text=info_text, font=("Arial", 16)).pack(pady=20)
        
        tk.Button(trump_frame, text="Start Bidding", font=("Arial", 14),
                  command=self.setup_bidding_phase, width=15, height=2).pack(pady=20)

    def setup_bidding_phase(self):
        self.current_phase = "bidding"
        self.current_player_index = 0
        self.discarded_cards = []
        self.discard_count = 0
        self.setup_game_ui()

    def setup_game_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        self.root.grid_rowconfigure(2, weight=2)
            
        menu_bar = tk.Menu(self.root)
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.get_game_settings)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Rules", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

        self.top_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=5)
        self.top_frame.grid(row=0, column=0, sticky="ew")
        
        self.center_frame = tk.Frame(self.root, bg="#f8f8f8", padx=10, pady=10)
        self.center_frame.grid(row=1, column=0, sticky="nsew")
        
        self.bottom_frame = tk.Frame(self.root, bg="#e8e8e8", padx=10, pady=10)
        self.bottom_frame.grid(row=2, column=0, sticky="ew")

        tk.Label(self.bottom_frame, text=f"{self.player_names[self.current_player_index]}'s Hand", 
                 font=("Arial", 12, "bold"), bg="#e8e8e8").pack(pady=5)

        self.update_scores()
        
        trump_frame = tk.Frame(self.center_frame, bg="#f8f8f8", padx=5, pady=5)
        trump_frame.pack(pady=10)
        
        rank = self.trump_card.rank
        suit = self.trump_card.suit if self.trump_card.suit != "Joker" else None
        tk.Label(trump_frame, text="Trump Card:", font=("Arial", 14), bg="#f8f8f8").pack(side="left", padx=5)
        
        img = self.load_card_image(rank, suit, size=(60, 90))
        if img:
            self.card_images.append(img)
            tk.Label(trump_frame, image=img, bg="#f8f8f8").pack(side="left")
        else:
            tk.Label(trump_frame, text=str(self.trump_card), width=5, height=7, relief="raised", bg="white").pack(side="left")
        
        info_text = "No Trump Suit" if (rank == "Nine" or rank == "Joker") else f"The trump suit is: {suit.upper()}"
        tk.Label(self.center_frame, text=info_text, font=("Arial", 14), bg="#f8f8f8").pack(pady=5)
        
        self.turn_label = tk.Label(self.center_frame, text=f"Turn: {self.player_names[self.current_player_index]}", 
                                  font=("Arial", 16, "bold"), fg="blue", bg="#f8f8f8")
        self.turn_label.pack(pady=10)
        
        self.trick_frame = tk.Frame(self.center_frame, bg="#e0f0e0", width=300, height=200, relief=tk.GROOVE, bd=2)
        self.trick_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        self.trick_frame.pack_propagate(False)
        
        tk.Label(self.trick_frame, text=f"Trick {self.current_trick_number}", font=("Arial", 12), bg="#e0f0e0").pack(pady=10)
        
        self.played_cards_frame = tk.Frame(self.trick_frame, bg="#e0f0e0")
        self.played_cards_frame.pack(pady=10, expand=True)

        self.update_player_hand()
        if self.current_phase == "bidding":
            self.handle_bidding()
        elif self.current_phase == "trick":
            self.handle_trick()

    def update_scores(self):
        scores_text = f"Scores — {self.player_names[0]}: {self.players[0].score} | " \
                      f"{self.player_names[1]}: {self.players[1].score} | " \
                      f"{self.player_names[2]}: {self.players[2].score}"
        for widget in self.top_frame.winfo_children():
            widget.destroy()
        tk.Label(self.top_frame, text=scores_text, font=("Arial", 14, "bold"), bg="#e0e0e0").pack(pady=10)

    def update_player_hand(self):
        for widget in self.bottom_frame.winfo_children():
            if widget != self.bottom_frame.winfo_children()[0]:
                widget.destroy()
        
        player = self.players[self.current_player_index]
        hand = [(card.rank, card.suit if card.suit != "Joker" else None, card) for card in player.hand]
        self.create_scrollable_cards(self.bottom_frame, hand, vertical=False, interactive=True)

    def create_scrollable_cards(self, parent, cards, vertical=False, interactive=False):
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame)
        
        if vertical:
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            canvas.configure(yscrollcommand=scrollbar.set)
        else:
            scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
            scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas.configure(xscrollcommand=scrollbar.set)
            
        cards_frame = tk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=cards_frame, anchor="nw")
        
        def on_card_click(card_btn, card_obj):
            if self.current_phase == "bidding":
                self.handle_bid_card(card_btn, card_obj)
            elif self.current_phase == "trick":
                self.handle_trick_card(card_btn, card_obj)
        
        for rank, suit, card_obj in cards:
            img = self.load_card_image(rank, suit, size=(60, 90))
            if img:
                self.card_images.append(img)
                if interactive:
                    card_btn = tk.Button(cards_frame, image=img, relief="raised")
                    card_btn.config(command=lambda b=card_btn, c=card_obj: on_card_click(b, c))
                    if vertical:
                        card_btn.pack(pady=2)
                    else:
                        card_btn.pack(side=tk.LEFT, padx=2)
                else:
                    lbl = tk.Label(cards_frame, image=img)
                    if vertical:
                        lbl.pack(pady=2)
                    else:
                        lbl.pack(side=tk.LEFT, padx=2)
            else:
                placeholder = tk.Label(cards_frame, text=f"{rank} {suit if suit else 'Joker'}", 
                                     width=5, height=7, relief="raised", bg="white")
                if interactive:
                    placeholder.bind("<Button-1>", lambda e, c=card_obj: on_card_click(placeholder, c))
                if vertical:
                    placeholder.pack(pady=2)
                else:
                    placeholder.pack(side=tk.LEFT, padx=2)
        
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if vertical:
                canvas.configure(width=cards_frame.winfo_reqwidth())
            else:
                canvas.configure(height=cards_frame.winfo_reqheight())
        
        cards_frame.bind("<Configure>", configure_canvas)
        
        if vertical:
            cards_frame.config(width=100)
        else:
            cards_frame.config(height=110)

    def load_card_image(self, rank, suit, size=(60, 90)):
        try:
            if rank == "Joker":
                filename = "Joker.png"
            else:
                # Ensure exact naming: [rank]of[suit].png (e.g., KingofHearts.png)
                rank_map = {
                    "Ace": "ace", "King": "king", "Queen": "queen", "Jack": "jack",
                    "Ten": "10", "Nine": "9", "Eight": "8", "Seven": "7", "Six": "6"
                }
                suit_map = {
                   "Hearts": "hearts", "Diamonds": "diamonds", "Clubs": "clubs", "Spades": "spades"
                }
                filename = f"{rank_map[rank]}_of_{suit_map[suit]}.png"
                
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
            path = os.path.join(folder_path, filename)
            
            if not os.path.exists(folder_path):
                print(f"Images folder not found: {folder_path}")
                return None
            if not os.path.exists(path):
                print(f"Image file not found: {path}")
                return None
                
            img = Image.open(path).resize(size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading {rank} of {suit if suit else 'Joker'}: {e}")
            return None

    def handle_bidding(self):
        player = self.players[self.current_player_index]
        self.turn_label.config(text=f"Turn: {player.name} - Select 3 cards to discard for bidding")
        self.discarded_cards = []
        self.discard_count = 0

    def handle_bid_card(self, card_btn, card_obj):
        if self.discard_count < 3 and card_obj in self.players[self.current_player_index].hand:
            self.discarded_cards.append(card_obj)
            self.discard_count += 1
            card_btn.config(state="disabled", relief="sunken")
            if self.discard_count == 3:
                player = self.players[self.current_player_index]
                bid_value = sum(10 if card.suit == "Spades" else 20 if card.suit == "Hearts"
                               else 30 if card.suit == "Clubs" else 0 for card in self.discarded_cards)
                player.hand = [card for card in player.hand if card not in self.discarded_cards]
                self.bids[player.name] = bid_value
                player.bid = bid_value
                messagebox.showinfo("Bid", f"{player.name} bid {bid_value} points.")
                self.current_player_index += 1
                if self.current_player_index < 3:
                    self.prompt_next_player()
                else:
                    self.start_trick_phase()

    def prompt_next_player(self):
        next_player = self.players[self.current_player_index]
        messagebox.showinfo("Next Player", f"Please pass to {next_player.name} to bid.")
        self.setup_game_ui()

    def start_trick_phase(self):
        self.current_phase = "trick"
        self.current_trick_number = 1
        self.current_player_index = 0
        self.current_trick = []
        for widget in self.played_cards_frame.winfo_children():
            widget.destroy()
        tk.Label(self.trick_frame, text=f"Trick {self.current_trick_number}", font=("Arial", 12), bg="#e0f0e0").pack(pady=10)
        self.handle_trick()

    def handle_trick(self):
        player = self.players[self.current_player_index]
        self.turn_label.config(text=f"Turn: {player.name} - Play a card for Trick {self.current_trick_number}")
        self.update_player_hand()

    def handle_trick_card(self, card_btn, card_obj):
        if card_obj in self.players[self.current_player_index].hand:
            player = self.players[self.current_player_index]
            player.hand.remove(card_obj)
            self.current_trick.append((player, card_obj))
            self.display_played_card(card_obj)
            card_btn.config(state="disabled", relief="sunken")
            self.current_player_index = (self.current_player_index + 1) % 3
            if len(self.current_trick) < 3:
                self.prompt_next_player_trick()
            else:
                self.resolve_trick()

    def prompt_next_player_trick(self):
        next_player = self.players[self.current_player_index]
        messagebox.showinfo("Next Player", f"Please pass to {next_player.name} to play a card.")
        self.setup_game_ui()

    def display_played_card(self, card):
        rank = card.rank
        suit = card.suit if card.suit != "Joker" else None
        img = self.load_card_image(rank, suit, size=(60, 90))
        if img:
            self.card_images.append(img)
            tk.Label(self.played_cards_frame, image=img, bg="#e0f0e0").pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(self.played_cards_frame, text=str(card), bg="#e0f0e0").pack(side=tk.LEFT, padx=5)

    def resolve_trick(self):
        lead_suit = self.current_trick[0][1].suit
        highest_card = self.current_trick[0]
        
        for player, card in self.current_trick[1:]:
            if card.suit == lead_suit and card.point_value > highest_card[1].point_value:
                highest_card = (player, card)
            elif self.trump_card and card.suit == self.trump_card.suit and highest_card[1].suit != self.trump_card.suit:
                highest_card = (player, card)
        
        winner = highest_card[0]
        self.tricks_won[winner.name] += 1
        messagebox.showinfo("Trick Result", f"{winner.name} wins Trick {self.current_trick_number} with {highest_card[1]}!")
        
        self.current_trick_number += 1
        self.current_trick = []
        self.current_player_index = self.players.index(winner)  # Start next trick with winner
        
        for widget in self.played_cards_frame.winfo_children():
            widget.destroy()
        
        if self.current_trick_number <= 9:
            for widget in self.trick_frame.winfo_children():
                widget.destroy()
            tk.Label(self.trick_frame, text=f"Trick {self.current_trick_number}", font=("Arial", 12), bg="#e0f0e0").pack(pady=10)
            self.played_cards_frame = tk.Frame(self.trick_frame, bg="#e0f0e0")
            self.played_cards_frame.pack(pady=10, expand=True)
            self.prompt_next_player_trick()
        else:
            self.score_round()

    def score_round(self):
        self.current_phase = "scoring"
        differences = {}
        for player in self.players:
            bid = player.bid
            tricks = self.tricks_won[player.name] * 10
            differences[player.name] = abs(bid - tricks)
        
        for player in self.players:
            opponent_diffs = [differences[opponent.name] for opponent in self.players if opponent != player]
            base_score = sum(opponent_diffs)
            bonus = 0
            if differences[player.name] == 0:
                bonus = 30
            elif differences[player.name] <= 2:
                bonus = 20
            elif differences[player.name] <= 5:
                bonus = 10
            player.round_score = base_score + bonus
            player.score += player.round_score
        
        self.update_scores()
        
        round_winner = max(self.players, key=lambda p: p.round_score)
        messagebox.showinfo("Round Result", f"Round {self.current_round} Complete!\n"
                            f"Round Winner: {round_winner.name} with {round_winner.round_score} points")
        
        self.check_game_over()

    def check_game_over(self):
        if self.win_condition == 1:
            players_over_target = [player for player in self.players if player.score >= self.target_score]
            if players_over_target:
                players_over_target.sort(key=lambda p: p.score, reverse=True)
                if len(players_over_target) > 1 and players_over_target[0].score == players_over_target[1].score:
                    tied_players = [p.name for p in players_over_target if p.score == players_over_target[0].score]
                    messagebox.showinfo("Game Over", f"Game ended in a draw between {', '.join(tied_players)} "
                                        f"with {players_over_target[0].score} points!")
                else:
                    winner = players_over_target[0]
                    messagebox.showinfo("Game Over", f"{winner.name} wins with {winner.score} points!")
                self.game_over = True
        elif self.win_condition == 2 and self.current_round >= self.max_rounds:
            max_score = max(player.score for player in self.players)
            winners = [player for player in self.players if player.score == max_score]
            if len(winners) > 1:
                tied_players = [p.name for p in winners]
                messagebox.showinfo("Game Over", f"After {self.max_rounds} rounds, game ended in a draw between "
                                    f"{', '.join(tied_players)} with {max_score} points!")
            else:
                winner = winners[0]
                messagebox.showinfo("Game Over", f"After {self.max_rounds} rounds, {winner.name} wins with {winner.score} points!")
            self.game_over = True
        
        if not self.game_over:
            self.players.append(self.players.pop(0))
            self.current_round += 1
            messagebox.showinfo("Next Round", f"Next round dealer: {self.players[0].name}\nClick OK to start Round {self.current_round}")
            self.start_round()
        else:
            self.show_welcome_screen()

    def show_help(self):
        rules = (
            "CounterPoint Game Rules:\n\n"
            "- 3 players, 37 cards (including Joker)\n"
            "- Each player discards 3 cards to place a bid\n"
            "- Card suits represent bid value:\n"
            "    ♦ = 0, ♠ = 10, ♥ = 20, ♣ = 30\n"
            "- Players take 9 tricks\n"
            "- Win tricks and get points based on your bid accuracy\n"
            "- Game ends when a player reaches target score or max rounds\n"
        )
        messagebox.showinfo("Game Rules", rules)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CounterPointGame()
    game.run()
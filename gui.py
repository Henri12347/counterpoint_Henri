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
        self.bid_cards = {}  # Store bid cards for each player
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
            
        # Create a frame to hold the background and buttons
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(bg="White")  # Use system default for pseudo-transparency
        
        # Create a label for the background image
        bg_label = tk.Label(main_frame)
        bg_label.place(relx=0.5, rely=0.5, anchor="center")
        bg_label.configure(bg="White")
        
        def resize_background(event=None):
            try:
                folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
                img_path = os.path.join(folder_path, "background.png")
                img = Image.open(img_path)
                # Resize image to fit current window size while maintaining aspect ratio
                window_width = max(self.root.winfo_width(), 1)
                window_height = max(self.root.winfo_height(), 1)
                img_width, img_height = img.size
                scale = min(window_width/img_width, window_height/img_height)
                new_size = (int(img_width * scale), int(img_height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                if bg_label.winfo_exists():
                    bg_label.configure(image=self.bg_image)
            except Exception as e:
                print(f"Error loading background.png: {e}")
            if main_frame.winfo_exists():
                main_frame.configure(bg="#f8f8f8")
            if bg_label.winfo_exists():
                bg_label.configure(bg="#f8f8f8")
        
        # Configure buttons with custom color
        button_style = {"font": ("Arial", 14), "bg": "#f5e1bf", "width": 15, "height": 2}

        tk.Button(main_frame, text="Start Game", command=self.get_game_settings, **button_style).place(relx=0.5, rely=0.4, anchor="center")
        tk.Button(main_frame, text="Game Rules", command=self.show_help, **button_style).place(relx=0.5, rely=0.5, anchor="center")
        tk.Button(main_frame, text="Exit", command=self.root.destroy, **button_style).place(relx=0.5, rely=0.6, anchor="center")
        
        # Load initial background
        self.root.after(100, resize_background)

    def get_game_settings(self):
        self.current_phase = "player_names"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        names_frame = tk.Frame(self.root)
        names_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(names_frame, text="Enter Player Names", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Player 1
        tk.Label(names_frame, text="Choose a name for Player 1:", font=("Arial", 14)).pack(pady=5)
        player1_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player1_entry.pack(pady=5)
        player1_entry.focus_set()
        
        # Player 2
        tk.Label(names_frame, text="Choose a name for Player 2:", font=("Arial", 14)).pack(pady=5)
        player2_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player2_entry.pack(pady=5)
        
        # Player 3
        tk.Label(names_frame, text="Choose a name for Player 3:", font=("Arial", 14)).pack(pady=5)
        player3_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player3_entry.pack(pady=5)
        
        def submit_names():
            # Get names from entries, default to "Player X" if empty
            self.player_names[0] = player1_entry.get().strip() or "Player 1"
            self.player_names[1] = player2_entry.get().strip() or "Player 2"
            self.player_names[2] = player3_entry.get().strip() or "Player 3"
            self.show_win_condition_screen()
        
        tk.Button(names_frame, text="Continue", font=("Arial", 14),
                  command=submit_names, width=15, height=2).pack(pady=20)

    def show_win_condition_screen(self):
        self.current_phase = "win_condition"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        win_frame = tk.Frame(self.root)
        win_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(win_frame, text="Choose Winning Condition", font=("Arial", 20, "bold")).pack(pady=20)
        
        tk.Button(win_frame, text="Target Score", font=("Arial", 14),
                  command=lambda: self.set_win_condition(1), width=15, height=2).pack(pady=10)
        
        tk.Button(win_frame, text="Set Rounds", font=("Arial", 14),
                  command=lambda: self.set_win_condition(2), width=15, height=2).pack(pady=10)

    def set_win_condition(self, condition):
        self.win_condition = condition
        self.current_phase = "input_condition"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        input_frame = tk.Frame(self.root)
        input_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        if condition == 1:
            tk.Label(input_frame, text="Enter Target Score", font=("Arial", 20, "bold")).pack(pady=20)
            tk.Label(input_frame, text="Enter a positive number", font=("Arial", 14)).pack(pady=5)
            
            score_entry = tk.Entry(input_frame, font=("Arial", 14), width=10)
            score_entry.pack(pady=10)
            score_entry.focus_set()
            
            def submit_score():
                try:
                    score = int(score_entry.get())
                    if score > 0:
                        self.target_score = score
                        self.initialize_game()
                    else:
                        messagebox.showerror("Error", "Target score must be a positive number.")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number.")
            
            tk.Button(input_frame, text="Submit", font=("Arial", 14),
                      command=submit_score, width=15, height=2).pack(pady=10)
            
            tk.Button(input_frame, text="Back", font=("Arial", 14),
                      command=self.show_win_condition_screen, width=15, height=2).pack(pady=10)
            
        elif condition == 2:
            tk.Label(input_frame, text="Enter Number of Rounds", font=("Arial", 20, "bold")).pack(pady=20)
            tk.Label(input_frame, text="Enter 1 or a number divisible by 3", font=("Arial", 14)).pack(pady=5)
            
            rounds_entry = tk.Entry(input_frame, font=("Arial", 14), width=10)
            rounds_entry.pack(pady=10)
            rounds_entry.focus_set()
            
            def submit_rounds():
                try:
                    rounds = int(rounds_entry.get())
                    if rounds == 1 or (rounds > 0 and rounds % 3 == 0):
                        self.max_rounds = rounds
                        self.initialize_game()
                    else:
                        messagebox.showerror("Error", "Number of rounds must be 1 or a positive number divisible by 3.")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number.")
            
            tk.Button(input_frame, text="Submit", font=("Arial", 14),
                      command=submit_rounds, width=15, height=2).pack(pady=10)
            
            tk.Button(input_frame, text="Back", font=("Arial", 14),
                      command=self.show_win_condition_screen, width=15, height=2).pack(pady=10)

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
        
        info_text = "No Trump Suit" if (rank == "Nine" or rank == "Joker") else f"Trump Suit: {suit.upper()}"
        tk.Label(self.center_frame, text=info_text, font=("Arial", 14), bg="#f8f8f8").pack(pady=5)
        
        self.turn_label = tk.Label(self.center_frame, text=f"Turn: {self.player_names[self.current_player_index]}", 
                                  font=("Arial", 16, "bold"), fg="blue", bg="#f8f8f8")
        self.turn_label.pack(pady=10)
        
        self.trick_frame = tk.Frame(self.center_frame, bg="#e0f0e0", width=300, height=200, relief=tk.GROOVE, bd=2)
        self.trick_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        self.trick_frame.pack_propagate(False)
        
        trick_label_text = "Selected Cards" if self.current_phase == "bidding" else f"Trick {self.current_trick_number}"
        tk.Label(self.trick_frame, text=trick_label_text, font=("Arial", 12), bg="#e0f0e0").pack(pady=5)
        
        self.played_cards_frame = tk.Frame(self.trick_frame, bg="#e0f0e0")
        self.played_cards_frame.pack(fill=tk.BOTH, expand=True)
        self.played_cards_frame.grid_columnconfigure(0, weight=1)
        self.played_cards_frame.grid_columnconfigure(1, weight=1)
        self.played_cards_frame.grid_columnconfigure(2, weight=1)
        self.played_cards_frame.grid_rowconfigure(0, weight=1)

        # Create sub-frames for left, center, and right
        self.left_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
        self.left_frame.grid(row=0, column=0, sticky="n")
        
        self.current_cards_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
        self.current_cards_frame.grid(row=0, column=1, sticky="n")
        
        self.right_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
        self.right_frame.grid(row=0, column=2, sticky="n")

        # Display previous players' bid or trick cards
        if self.current_phase == "bidding":
            for i in range(self.current_player_index):
                player_name = self.player_names[i]
                if player_name in self.bid_cards:
                    target_frame = self.left_frame if i == 0 else self.right_frame
                    frame = tk.Frame(target_frame, bg="#e0f0e0")
                    frame.pack(pady=5)
                    tk.Label(frame, text=f"{player_name}'s Bid", font=("Arial", 10), bg="#e0f0e0").pack()
                    cards_frame = tk.Frame(frame, bg="#e0f0e0")
                    cards_frame.pack()
                    for card in self.bid_cards[player_name]:
                        rank = card.rank
                        suit = card.suit if card.suit != "Joker" else None
                        img = self.load_card_image(rank, suit, size=(60, 90))
                        if img:
                            self.card_images.append(img)
                            tk.Label(cards_frame, image=img, bg="#e0f0e0").pack(side=tk.LEFT, padx=2)
                        else:
                            tk.Label(cards_frame, text=str(card), bg="#e0f0e0").pack(side=tk.LEFT, padx=2)
        elif self.current_phase == "trick":
            for i, (player, card) in enumerate(self.current_trick):
                player_name = player.name
                target_frame = self.left_frame if i == 0 else self.right_frame
                frame = tk.Frame(target_frame, bg="#e0f0e0")
                frame.pack(pady=5)
                tk.Label(frame, text=f"{player_name}'s Card", font=("Arial", 10), bg="#e0f0e0").pack()
                rank = card.rank
                suit = card.suit if card.suit != "Joker" else None
                img = self.load_card_image(rank, suit, size=(60, 90))
                if img:
                    self.card_images.append(img)
                    tk.Label(frame, image=img, bg="#e0f0e0").pack(pady=2)
                else:
                    tk.Label(frame, text=str(card), bg="#e0f0e0").pack(pady=2)

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
        self.card_buttons = []  # Store card buttons for enabling/disabling
        self.create_scrollable_cards(self.bottom_frame, hand, vertical=False, interactive=True)
        
        if self.current_phase == "bidding":
            # Add Submit Bid button to the right of the cards
            self.submit_bid_button = tk.Button(self.bottom_frame, text="Submit Bid", font=("Arial", 12),
                                               command=self.submit_bid, width=15, height=2, state="disabled")
            self.submit_bid_button.pack(side=tk.RIGHT, padx=10)
        elif self.current_phase == "trick":
            # Add Play Card button to the right of the cards
            self.play_card_button = tk.Button(self.bottom_frame, text="Play Card", font=("Arial", 12),
                                              command=self.submit_trick_card, width=15, height=2, state="disabled")
            self.play_card_button.pack(side=tk.RIGHT, padx=10)

    def create_scrollable_cards(self, parent, cards, vertical=False, interactive=False):
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
                    card_btn._card_obj = card_obj  # Store card_obj for identification
                    self.card_buttons.append(card_btn)  # Store button for enabling/disabling
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
        self.turn_label.config(text=f"Turn: {player.name} - Select 3 cards to bid")
        self.discarded_cards = []
        self.discard_count = 0
        # Clear only the current player's selection area
        for widget in self.current_cards_frame.winfo_children():
            widget.destroy()

    def handle_bid_card(self, card_btn, card_obj):
        if self.current_phase != "bidding" or card_obj not in self.players[self.current_player_index].hand:
            return
        
        if card_obj in self.discarded_cards:
            # Deselect the card
            self.discarded_cards.remove(card_obj)
            self.discard_count -= 1
            card_btn.config(relief="raised", bg="SystemButtonFace")
            # Remove the card from the current_cards_frame
            for widget in self.current_cards_frame.winfo_children():
                if hasattr(widget, "_card_obj") and widget._card_obj == card_obj:
                    widget.destroy()
        else:
            # Select the card if less than 3 are selected
            if self.discard_count < 3:
                self.discarded_cards.append(card_obj)
                self.discard_count += 1
                card_btn.config(relief="sunken", bg="#d0d0d0")
                # Display the card in the current_cards_frame horizontally
                rank = card_obj.rank
                suit = card_obj.suit if card_obj.suit != "Joker" else None
                img = self.load_card_image(rank, suit, size=(60, 90))
                if img:
                    self.card_images.append(img)
                    card_label = tk.Label(self.current_cards_frame, image=img, bg="#e0f0e0")
                    card_label._card_obj = card_obj  # Store card_obj for identification
                    card_label.pack(side=tk.LEFT, padx=5)
                else:
                    card_label = tk.Label(self.current_cards_frame, text=str(card_obj), bg="#e0f0e0")
                    card_label._card_obj = card_obj
                    card_label.pack(side=tk.LEFT, padx=5)
        
        # Enable/disable Submit Bid button based on discard_count
        if hasattr(self, 'submit_bid_button'):
            self.submit_bid_button.config(state="normal" if self.discard_count == 3 else "disabled")

    def submit_bid(self):
        if self.discard_count != 3:
            return
        
        player = self.players[self.current_player_index]
        bid_value = sum(10 if card.suit == "Spades" else 20 if card.suit == "Hearts"
                        else 30 if card.suit == "Clubs" else 0 for card in self.discarded_cards)
        player.hand = [card for card in player.hand if card not in self.discarded_cards]
        self.bids[player.name] = bid_value
        player.bid = bid_value
        self.bid_cards[player.name] = self.discarded_cards[:]  # Store bid cards
        
        # Clear the current player's selection area
        for widget in self.played_cards_frame.winfo_children():
            if not widget.winfo_children():
                widget.destroy()
        
        self.current_player_index += 1
        if self.current_player_index < 3:
            next_player = self.players[self.current_player_index]
            message = f"{player.name} bid {bid_value} points.\nPlease pass to {next_player.name} to bid."
            self.show_custom_dialog("Bid Result", message, lambda: self.prompt_next_player())
        else:
            message = f"{player.name} bid {bid_value} points."
            self.show_custom_dialog("Bid Result", message, lambda: self.start_trick_phase())

    def prompt_next_player(self):
        self.setup_game_ui()

    def show_custom_dialog(self, title, message, on_close):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog relative to the root window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text=message, font=("Arial", 12), wraplength=250).pack(pady=20)
        
        tk.Button(dialog, text="Continue", font=("Arial", 12),
                  command=lambda: [dialog.destroy(), on_close()]).pack(pady=10)
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: [dialog.destroy(), on_close()])

    def start_trick_phase(self):
        self.current_phase = "trick"
        self.current_trick_number = 1
        self.current_player_index = 0
        self.current_trick = []
        self.setup_game_ui()  # This will call handle_trick() too

    def handle_trick(self):
        player = self.players[self.current_player_index]
        self.turn_label.config(text=f"Turn: {player.name} - Select a card for Trick {self.current_trick_number}")
        self.selected_trick_card = None
        # Clear only the current player's selection area
        for widget in self.current_cards_frame.winfo_children():
            widget.destroy()
        self.update_player_hand()
        
        # Enforce follow suit rule
        lead_suit = None
        if self.current_trick:  # If not the first player in the trick
            lead_suit = self.current_trick[0][1].suit if self.current_trick[0][1].suit != "Joker" else None
        
        if lead_suit:
            # Check if player has cards of the lead suit
            has_lead_suit = any(card.suit == lead_suit for card in player.hand)
            if has_lead_suit:
                # Disable cards that don't match the lead suit
                for btn in self.card_buttons:
                    card_obj = btn._card_obj
                    if card_obj.suit != lead_suit:
                        btn.config(state="disabled")
                    else:
                        btn.config(state="normal")
            else:
                # Enable all cards if player has no lead suit
                for btn in self.card_buttons:
                    btn.config(state="normal")
        else:
            # First player can play any card
            for btn in self.card_buttons:
                btn.config(state="normal")

    def handle_trick_card(self, card_btn, card_obj):
        if self.current_phase != "trick" or card_obj not in self.players[self.current_player_index].hand:
            return
        
        # Check if the card follows suit
        lead_suit = None
        if self.current_trick:  # If not the first player in the trick
            lead_suit = self.current_trick[0][1].suit if self.current_trick[0][1].suit != "Joker" else None
        
        if lead_suit:
            has_lead_suit = any(card.suit == lead_suit for card in self.players[self.current_player_index].hand)
            if has_lead_suit and card_obj.suit != lead_suit:
                return  # Prevent selecting a card that doesn't follow suit
        
        if card_obj == self.selected_trick_card:
            # Deselect the card
            self.selected_trick_card = None
            card_btn.config(relief="raised", bg="SystemButtonFace", state="normal")
            # Remove the card from the current_cards_frame
            for widget in self.current_cards_frame.winfo_children():
                if hasattr(widget, "_card_obj") and widget._card_obj == card_obj:
                    widget.destroy()
            # Re-enable valid cards based on lead suit
            if lead_suit:
                has_lead_suit = any(card.suit == lead_suit for card in self.players[self.current_player_index].hand)
                if has_lead_suit:
                    for btn in self.card_buttons:
                        if btn._card_obj.suit == lead_suit:
                            btn.config(state="normal")
                        else:
                            btn.config(state="disabled")
                else:
                    for btn in self.card_buttons:
                        btn.config(state="normal")
            else:
                for btn in self.card_buttons:
                    btn.config(state="normal")
        else:
            # Select the card, deselecting any previously selected card
            if self.selected_trick_card:
                # Reset the previously selected card's button
                for btn in self.card_buttons:
                    if hasattr(btn, "_card_obj") and btn._card_obj == self.selected_trick_card:
                        btn.config(relief="raised", bg="SystemButtonFace", state="normal")
                # Clear the current_cards_frame
                for widget in self.current_cards_frame.winfo_children():
                    if hasattr(widget, "_card_obj") and widget._card_obj == self.selected_trick_card:
                        widget.destroy()
            
            self.selected_trick_card = card_obj
            card_btn.config(relief="sunken", bg="#d0d0d0", state="normal")  # Keep selected card clickable
            card_btn._card_obj = card_obj  # Store card_obj for identification
            # Disable all other card buttons
            for btn in self.card_buttons:
                if btn != card_btn:
                    btn.config(state="disabled")
            # Display the card in the current_cards_frame
            rank = card_obj.rank
            suit = card_obj.suit if card_obj.suit != "Joker" else None
            img = self.load_card_image(rank, suit, size=(60, 90))
            if img:
                self.card_images.append(img)
                card_label = tk.Label(self.current_cards_frame, image=img, bg="#e0f0e0")
                card_label._card_obj = card_obj  # Store card_obj for identification
                card_label.pack(side=tk.LEFT, padx=5)
            else:
                card_label = tk.Label(self.current_cards_frame, text=str(card_obj), bg="#e0f0e0")
                card_label._card_obj = card_obj
                card_label.pack(side=tk.LEFT, padx=5)
        
        # Enable/disable Play Card button based on whether a card is selected
        if hasattr(self, 'play_card_button'):
            self.play_card_button.config(state="normal" if self.selected_trick_card else "disabled")

    def submit_trick_card(self):
        if not self.selected_trick_card:
            return
        
        player = self.players[self.current_player_index]
        if self.selected_trick_card in player.hand:
            player.hand.remove(self.selected_trick_card)
            self.current_trick.append((player, self.selected_trick_card))
            self.selected_trick_card = None
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
            self.played_cards_frame.grid_columnconfigure(0, weight=1)
            self.played_cards_frame.grid_columnconfigure(1, weight=1)
            self.played_cards_frame.grid_columnconfigure(2, weight=1)
            self.played_cards_frame.grid_rowconfigure(0, weight=1)
            
            self.left_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
            self.left_frame.grid(row=0, column=0, sticky="n")
            
            self.current_cards_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
            self.current_cards_frame.grid(row=0, column=1, sticky="n")
            
            self.right_frame = tk.Frame(self.played_cards_frame, bg="#e0f0e0")
            self.right_frame.grid(row=0, column=2, sticky="n")
            
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
            "- You must follow the suit of the first card played if you have it\n"
            "- Win tricks and get points based on your bid accuracy\n"
            "- Game ends when a player reaches target score or max rounds\n"
        )
        messagebox.showinfo("Game Rules", rules)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CounterPointGame()
    game.run()
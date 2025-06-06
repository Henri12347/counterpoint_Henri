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
    RANK_ORDER = ["Six", "Seven", "Eight", "Nine", "Jack", "Queen", "King", "Ten", "Ace"]
    
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
        self.scoring_details = {}
        self.cumulative_stats = {
            'total_tricks_won': 0,
            'total_points_won': 0,
            'total_cards_won': 0,
            'total_bonus': 0,
            'bids': [],  # List of (bid, points_won) tuples per round
            'round_scores': [],  # List of round scores
            'differences': [],  # List of differences per round
            'bonuses': []  # List of bonuses per round
        }

    def receive_cards(self, cards):
        """Assign dealt cards to the player."""
        self.hand = cards


class CounterPointGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CounterPoint")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#194c22")  # Set main background color
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
        self.cards_won = {}  # Initialize here to ensure it's available
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.current_phase = "welcome"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create a frame to hold the background and buttons
        main_frame = tk.Frame(self.root, bg="#194c22")  # Match main background
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a label for the background image
        bg_label = tk.Label(main_frame, bg="#194c22")
        bg_label.place(relx=0.5, rely=0.5, anchor="center")
        
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
                main_frame.configure(bg="#194c22")
            if bg_label.winfo_exists():
                bg_label.configure(bg="#194c22")
        
        # Configure buttons with custom color
        button_style = {"font": ("Arial", 14), "bg": "#f5e1bf", "width": 15, "height": 2}

        tk.Button(main_frame, text="Start Game", command=self.get_game_settings, **button_style).place(relx=0.5, rely=0.4, anchor="center")
        tk.Button(main_frame, text="Game Rules", command=self.show_help, **button_style).place(relx=0.5, rely=0.5, anchor="center")
        tk.Button(main_frame, text="Exit", command=self.root.destroy, **button_style).place(relx=0.5, rely=0.6, anchor="center")
        
        # Load initial background
        self.root.after(30, resize_background)

    def get_game_settings(self):
        self.current_phase = "player_names"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        names_frame = tk.Frame(self.root, bg="#194c22")
        names_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(names_frame, text="Enter Player Names", font=("Arial", 20, "bold"), bg="#194c22", fg="white").pack(pady=20)
        
        # Player 1
        tk.Label(names_frame, text="Choose a name for Player 1:", font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)
        player1_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player1_entry.pack(pady=5)
        player1_entry.focus_set()
        
        # Player 2
        tk.Label(names_frame, text="Choose a name for Player 2:", font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)
        player2_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player2_entry.pack(pady=5)
        
        # Player 3
        tk.Label(names_frame, text="Choose a name for Player 3:", font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)
        player3_entry = tk.Entry(names_frame, font=("Arial", 14), width=20)
        player3_entry.pack(pady=5)
        
        def submit_names():
            # Get names from entries, default to "Player X" if empty
            self.player_names[0] = player1_entry.get().strip() or "Player 1"
            self.player_names[1] = player2_entry.get().strip() or "Player 2"
            self.player_names[2] = player3_entry.get().strip() or "Player 3"
            self.show_win_condition_screen()
        
        tk.Button(names_frame, text="Continue", font=("Arial", 14),
                  command=submit_names, bg="#f5e1bf", width=15, height=2).pack(pady=20)

    def show_win_condition_screen(self):
        self.current_phase = "win_condition"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        win_frame = tk.Frame(self.root, bg="#194c22")
        win_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(win_frame, text="Choose Winning Condition", font=("Arial", 20, "bold"), bg="#194c22", fg="white").pack(pady=20)
        
        tk.Button(win_frame, text="Target Score", font=("Arial", 14),
                  command=lambda: self.set_win_condition(1), bg="#f5e1bf", width=15, height=2).pack(pady=10)
        
        tk.Button(win_frame, text="Set Deals", font=("Arial", 14),
                  command=lambda: self.set_win_condition(2), bg="#f5e1bf", width=15, height=2).pack(pady=10)

    def set_win_condition(self, condition):
        self.win_condition = condition
        self.current_phase = "input_condition"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        input_frame = tk.Frame(self.root, bg="#194c22")
        input_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        if condition == 1:
            tk.Label(input_frame, text="Enter Target Score", font=("Arial", 20, "bold"), bg="#194c22", fg="white").pack(pady=20)
            tk.Label(input_frame, text="Enter a positive number", font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)
            
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
                      command=submit_score, bg="#f5e1bf", width=15, height=2).pack(pady=10)
            
            tk.Button(input_frame, text="Back", font=("Arial", 14),
                      command=self.show_win_condition_screen, bg="#f5e1bf", width=15, height=2).pack(pady=10)
            
        elif condition == 2:
            tk.Label(input_frame, text="Enter Number of deals", font=("Arial", 20, "bold"), bg="#194c22", fg="white").pack(pady=20)
            tk.Label(input_frame, text="Enter 1 or a number divisible by 3", font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)
            
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
                        messagebox.showerror("Error", "Number of deals must be 1 or a positive number divisible by 3.")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number.")
            
            tk.Button(input_frame, text="Submit", font=("Arial", 14),
                      command=submit_rounds, bg="#f5e1bf", width=15, height=2).pack(pady=10)
            
            tk.Button(input_frame, text="Back", font=("Arial", 14),
                      command=self.show_win_condition_screen, bg="#f5e1bf", width=15, height=2).pack(pady=10)

    def initialize_game(self):
        self.players = [Player(name) for name in self.player_names]
        self.current_round = 1  # Reset round count
        self.start_round()

    def start_round(self):
        self.current_phase = "setup"
        for player in self.players:
            player.round_score = 0
            player.hand = []
            player.bid = None
        self.deck = Deck()
        self.deck.shuffle()
        hands = self.deck.deal(num_players=3, cards_per_player=12)
        for i, player in enumerate(self.players):
            player.receive_cards(hands[i])
        self.trump_card = self.deck.reveal_trump()
        self.tricks_won = {player.name: 0 for player in self.players}
        self.cards_won = {player.name: [] for player in self.players}  # Reset cards won per round
        self.bids = {}
        self.current_trick = []
        self.current_trick_number = 1
        self.current_player_index = 0
        self.select_trump_card()

    def select_trump_card(self):
        self.current_phase = "trump"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        trump_frame = tk.Frame(self.root, bg="#194c22")
        trump_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(trump_frame, text=f"Round {self.current_round} - Trump Card", font=("Arial", 20, "bold"), bg="#194c22", fg="white").pack(pady=20)
        
        rank = self.trump_card.rank
        suit = self.trump_card.suit if self.trump_card.suit != "Joker" else None
        
        card_frame = tk.Frame(trump_frame, bg="#194c22")
        card_frame.pack(pady=20)
        
        img = self.load_card_image(rank, suit, size=(100, 150))
        if img:
            self.card_images.append(img)
            tk.Label(card_frame, image=img, bg="#194c22").pack()
        else:
            tk.Label(card_frame, text=str(self.trump_card), width=10, height=15, relief="raised", bg="white", font=("Arial", 12)).pack()
        
        info_text = "No trump suit this round!" if (rank == "Nine" or rank == "Joker") else f"The trump suit is: {suit.upper()}"
        tk.Label(trump_frame, text=info_text, font=("Arial", 16), bg="#194c22", fg="white").pack(pady=20)
        
        tk.Button(trump_frame, text="Start Bidding", font=("Arial", 14),
                  command=self.setup_bidding_phase, bg="#f5e1bf", width=15, height=2).pack(pady=20)

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

        self.top_frame = tk.Frame(self.root, bg="#ab3a11", padx=10, pady=5)  # Scores tab color
        self.top_frame.grid(row=0, column=0, sticky="ew")

        self.center_frame = tk.Frame(self.root, bg="#194c22", padx=10, pady=10)  # Main background color
        self.center_frame.grid(row=1, column=0, sticky="nsew")

        self.bottom_frame = tk.Frame(self.root, bg="#ab3a11", padx=10, pady=10)  # Player's hand bar color
        self.bottom_frame.grid(row=2, column=0, sticky="ew")

        tk.Label(self.bottom_frame, text=f"{self.players[self.current_player_index].name}'s Hand",
                 font=("Arial", 12, "bold"), bg="#ab3a11", fg="white").pack(pady=5)

        self.update_scores()

        trump_frame = tk.Frame(self.center_frame, bg="#194c22", padx=5, pady=5)
        trump_frame.pack(pady=10)

        rank = self.trump_card.rank
        suit = self.trump_card.suit if self.trump_card.suit != "Joker" else None
        tk.Label(trump_frame, text="Trump Card:", font=("Arial", 14), bg="#194c22", fg="white").pack(side="left", padx=5)

        img = self.load_card_image(rank, suit, size=(60, 90))
        if img:
            self.card_images.append(img)
            tk.Label(trump_frame, image=img, bg="#194c22").pack(side="left")
        else:
            tk.Label(trump_frame, text=str(self.trump_card), width=5, height=7, relief="raised", bg="white").pack(side="left")

        info_text = "No Trump Suit" if (rank == "Nine" or rank == "Joker") else f"Trump Suit: {suit.upper()}"
        tk.Label(self.center_frame, text=info_text, font=("Arial", 14), bg="#194c22", fg="white").pack(pady=5)

        self.turn_label = tk.Label(self.center_frame, text=f"Turn: {self.players[self.current_player_index].name}",
                                 font=("Arial", 16, "bold"), fg="white", bg="#194c22")
        self.turn_label.pack(pady=10)

        self.trick_frame = tk.Frame(self.center_frame, bg="#194c22", width=300, height=200, relief=tk.FLAT, bd=0)
        self.trick_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        self.trick_frame.pack_propagate(False)

        self.played_cards_frame = tk.Frame(self.trick_frame, bg="#194c22")
        self.played_cards_frame.pack(fill=tk.BOTH, expand=True)

        # Load and apply wood texture to played_cards_frame
        try:
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
            texture_path = os.path.join(folder_path, "wood_texture.jpg")
            if os.path.exists(texture_path):
                texture_img = Image.open(texture_path)
                # Resize to fit played_cards_frame (initially use trick_frame size as approximation)
                texture_img = texture_img.resize((300, 180), Image.Resampling.LANCZOS)
                self.trick_texture = ImageTk.PhotoImage(texture_img)
                self.card_images.append(self.trick_texture)  # Store to prevent garbage collection
                self.texture_label = tk.Label(self.played_cards_frame, image=self.trick_texture)
                self.texture_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover entire frame
                self.texture_label.lower()  # Ensure texture is behind other widgets
            else:
                print(f"Wood texture not found at {texture_path}, using default background")
                self.played_cards_frame.configure(bg="#194c22")
        except Exception as e:
            print(f"Error loading wood texture: {e}")
            self.played_cards_frame.configure(bg="#194c22")

        # Place the trick label directly on the wood texture
        trick_label_text = "Selected Cards" if self.current_phase == "bidding" else f"Trick {self.current_trick_number}"
        self.trick_label = tk.Label(self.played_cards_frame, text=trick_label_text, font=("Arial", 12), bg="#57311a", fg="white")
        self.trick_label.place(relx=0.5, rely=0, anchor="n", y=5)

        # Dynamic resizing of texture
        def resize_trick_texture(event):
            try:
                folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
                texture_path = os.path.join(folder_path, "wood_texture.jpg")
                if os.path.exists(texture_path):
                    texture_img = Image.open(texture_path)
                    # Resize to current played_cards_frame size
                    frame_width = max(event.width, 1)
                    frame_height = max(event.height, 1)
                    texture_img = texture_img.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
                    self.trick_texture = ImageTk.PhotoImage(texture_img)
                    self.card_images.append(self.trick_texture)  # Store to prevent garbage collection
                    if self.texture_label and self.texture_label.winfo_exists():
                        self.texture_label.configure(image=self.trick_texture)
            except Exception as e:
                print(f"Error resizing wood texture: {e}")

        self.played_cards_frame.bind("<Configure>", resize_trick_texture)

        self.played_cards_frame.grid_columnconfigure(0, weight=1)
        self.played_cards_frame.grid_columnconfigure(2, weight=1)
        self.played_cards_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
        self.left_frame.grid(row=0, column=0, sticky="n")

        self.right_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
        self.right_frame.grid(row=0, column=2, sticky="n")

        self.current_cards_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
        self.current_cards_frame.place(relx=0.5, rely=0, anchor="n", y=30)

        if self.current_phase == "bidding":
            for i in range(self.current_player_index):
                player_name = self.player_names[i]
                if player_name in self.bid_cards:
                    target_frame = self.left_frame if i == 0 else self.right_frame
                    frame = tk.Frame(target_frame, bg="#57311a")
                    frame.pack(pady=5)
                    tk.Label(frame, text=f"{player_name}'s Bid", font=("Arial", 10), bg="#57311a", fg="white").pack()
                    cards_frame = tk.Frame(frame, bg="#57311a")
                    cards_frame.pack()
                    for card in self.bid_cards[player_name]:
                        rank = card.rank
                        suit = card.suit if card.suit != "Joker" else None
                        img = self.load_card_image(rank, suit, size=(60, 90))
                        if img:
                            self.card_images.append(img)
                            tk.Label(cards_frame, image=img, bg="#57311a").pack(side=tk.LEFT, padx=2)
                        else:
                            tk.Label(cards_frame, text=str(card), bg="#57311a", fg="white").pack(side=tk.LEFT, padx=2)
        elif self.current_phase == "trick":
            for i, (player, card) in enumerate(self.current_trick):
                player_name = player.name
                target_frame = self.left_frame if i == 0 else self.right_frame
                frame = tk.Frame(target_frame, bg="#57311a")
                frame.pack(pady=5)
                tk.Label(frame, text=f"{player_name}'s Card", font=("Arial", 10), bg="#57311a", fg="white").pack()
                rank = card.rank
                suit = card.suit if card.suit != "Joker" else None
                img = self.load_card_image(rank, suit, size=(60, 90))
                if img:
                    self.card_images.append(img)
                    tk.Label(frame, image=img, bg="#57311a").pack(pady=2)
                else:
                    tk.Label(frame, text=str(card), bg="#57311a", fg="white").pack(pady=2)

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
        tk.Label(self.top_frame, text=scores_text, font=("Arial", 14, "bold"), bg="#ab3a11", fg="white").pack(pady=10)

    def update_player_hand(self):
        # Clear all widgets in bottom_frame
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()
        
        # Update the label to show the current player's hand
        player = self.players[self.current_player_index]
        tk.Label(self.bottom_frame, text=f"{player.name}'s Hand",
                 font=("Arial", 12, "bold"), bg="#ab3a11", fg="white").pack(pady=5)
        
        # Display the player's cards
        hand = [(card.rank, card.suit if card.suit != "Joker" else None, card) for card in player.hand]
        self.card_buttons = []  # Store card buttons for enabling/disabling
        self.create_scrollable_cards(self.bottom_frame, hand, vertical=False, interactive=True)
        
        if self.current_phase == "bidding":
            # Add Submit Bid button to the right of the cards
            self.submit_bid_button = tk.Button(self.bottom_frame, text="Submit Bid", font=("Arial", 12),
                                               command=self.submit_bid, bg="#f5e1bf", width=15, height=2, state="disabled")
            self.submit_bid_button.pack(side=tk.RIGHT, padx=10)
        elif self.current_phase == "trick":
            # Add Play Card button to the right of the cards
            self.play_card_button = tk.Button(self.bottom_frame, text="Play Card", font=("Arial", 12),
                                              command=self.submit_trick_card, bg="#f5e1bf", width=15, height=2, state="disabled")
            self.play_card_button.pack(side=tk.RIGHT, padx=10)

    def create_scrollable_cards(self, parent, cards, vertical=False, interactive=False):
        if parent == self.bottom_frame:
            # For the player's hand, use a simple frame without canvas or scrollbar
            cards_frame = tk.Frame(parent, bg="#ab3a11")
            cards_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            # For other cases, use the original canvas and scrollbar (though not used in current code)
            canvas_frame = tk.Frame(parent, bg="#194c22")
            canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            canvas = tk.Canvas(canvas_frame, bg="#194c22")
            
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
                
            cards_frame = tk.Frame(canvas, bg="#194c22")
            canvas.create_window((0, 0), window=cards_frame, anchor="nw")
            
            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                if vertical:
                    canvas.configure(width=cards_frame.winfo_reqwidth())
                else:
                    canvas.configure(height=cards_frame.winfo_reqheight())
            
            cards_frame.bind("<Configure>", configure_canvas)
        
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
                    card_btn = tk.Button(cards_frame, image=img, relief="raised", bg="#f5e1bf")
                    card_btn.config(command=lambda b=card_btn, c=card_obj: on_card_click(b, c))
                    card_btn._card_obj = card_obj  # Store card_obj for identification
                    self.card_buttons.append(card_btn)  # Store button for enabling/disabling
                    if vertical:
                        card_btn.pack(pady=2)
                    else:
                        card_btn.pack(side=tk.LEFT, padx=2)
                else:
                    lbl = tk.Label(cards_frame, image=img, bg="#ab3a11" if parent == self.bottom_frame else "#194c22")
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
        
        if parent != self.bottom_frame:
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
            card_btn.config(relief="raised", bg="#f5e1bf")
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
                    card_label = tk.Label(self.current_cards_frame, image=img, bg="#57311a")
                    card_label._card_obj = card_obj  # Store card_obj for identification
                    card_label.pack(side=tk.LEFT, padx=5)
                else:
                    card_label = tk.Label(self.current_cards_frame, text=str(card_obj), bg="#57311a", fg="white")
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
            message = f"{player.name} bid {bid_value} points."
            pass_message = f"Please pass to {next_player.name} to bid."
            self.show_bid_result_prompt(message, pass_message, self.prompt_next_player)
        else:
            message = f"{player.name} bid {bid_value} points."
            pass_message = "Bidding complete. Starting trick phase."
            self.show_bid_result_prompt(message, pass_message, self.start_trick_phase)

    def show_bid_result_prompt(self, bid_message, pass_message, on_continue):
        self.current_phase = "bid_result_prompt"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        prompt_frame = tk.Frame(self.root, bg="#194c22")
        prompt_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(prompt_frame, text="Bid Result", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
        tk.Label(prompt_frame, text=bid_message, font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=10)
        tk.Label(prompt_frame, text=pass_message, font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=20)
        
        tk.Button(prompt_frame, text="Continue", font=("Arial", 14),
                  command=on_continue, bg="#f5e1bf", width=15, height=2).pack(pady=30)

    def prompt_next_player(self):
        self.current_phase = "bidding"  # Ensure the phase is set to bidding for the next player
        self.setup_game_ui()

    def start_trick_phase(self):
        self.current_phase = "trick"
        self.current_trick_number = 1
        self.current_player_index = 0
        self.current_trick = []
        self.setup_game_ui()

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
            card_btn.config(relief="raised", bg="#f5e1bf", state="normal")
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
                        btn.config(relief="raised", bg="#f5e1bf", state="normal")
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
                card_label = tk.Label(self.current_cards_frame, image=img, bg="#57311a")
                card_label._card_obj = card_obj  # Store card_obj for identification
                card_label.pack(side=tk.LEFT, padx=5)
            else:
                card_label = tk.Label(self.current_cards_frame, text=str(card_obj), bg="#57311a", fg="white")
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
                self.show_next_player_prompt()
            else:
                self.resolve_trick()

    def show_next_player_prompt(self, trick_result=None):
        self.current_phase = "next_player_prompt"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        prompt_frame = tk.Frame(self.root, bg="#194c22")
        prompt_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        next_player = self.players[self.current_player_index]
        
        # Display the trick result if provided
        if trick_result:
            tk.Label(prompt_frame, text="Trick Result", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
            tk.Label(prompt_frame, text=trick_result, font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=10)
        
        # Display the pass to next player instruction
        tk.Label(prompt_frame, text=f"Pass to {next_player.name}", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
        tk.Label(prompt_frame, text="Please pass the device to the next player to play their card.",
                 font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=10)
        
        def on_continue():
            self.current_phase = "trick"  # Ensure the phase is set to trick for the next player
            self.setup_game_ui()
        
        tk.Button(prompt_frame, text="Continue", font=("Arial", 14),
                  command=on_continue, bg="#f5e1bf", width=15, height=2).pack(pady=30)

    def display_played_card(self, card):
        rank = card.rank
        suit = card.suit if card.suit != "Joker" else None
        img = self.load_card_image(rank, suit, size=(60, 90))
        if img:
            self.card_images.append(img)
            tk.Label(self.played_cards_frame, image=img, bg="#194c22").pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(self.played_cards_frame, text=str(card), bg="#194c22", fg="white").pack(side=tk.LEFT, padx=5)

    def card_strength(self, card, lead_suit, trump_suit):
        """Returns a tuple (priority, rank_index) to determine card strength."""
        priority = 0
        rank_index = Deck.RANK_ORDER.index(card.rank) if card.rank in Deck.RANK_ORDER else -1  # Joker has lowest rank

        if trump_suit and card.suit == trump_suit:
            priority = 2  # Trump cards have highest priority
        elif card.suit == lead_suit:
            priority = 1  # Lead suit cards have next priority

        return (priority, rank_index)

    def resolve_trick(self):
        lead_suit = self.current_trick[0][1].suit if self.current_trick[0][1].suit != "Joker" else None
        trump_suit = self.trump_card.suit if self.trump_card and self.trump_card.rank not in ["Nine", "Joker"] else None

        # Evaluate each card's strength
        strengths = [(player, card, self.card_strength(card, lead_suit, trump_suit)) for player, card in self.current_trick]
        # Find the highest strength card
        winner_entry = max(strengths, key=lambda x: x[2])  # Compare by strength tuple (priority, rank_index)
        winner, winning_card = winner_entry[0], winner_entry[1]

        # Update tricks won and cards won
        self.tricks_won[winner.name] += 1
        # Collect all cards in the trick for the winner
        for _, card in self.current_trick:
            self.cards_won[winner.name].append(card)

        # Prepare the trick result message
        trick_result = f"{winner.name} wins Trick {self.current_trick_number} with {winning_card}!"

        self.current_trick_number += 1
        self.current_trick = []
        self.current_player_index = self.players.index(winner)  # Start next trick with winner
        
        for widget in self.played_cards_frame.winfo_children():
            widget.destroy()
        
        if self.current_trick_number <= 9:
            for widget in self.trick_frame.winfo_children():
                widget.destroy()
            self.played_cards_frame = tk.Frame(self.trick_frame, bg="#194c22")
            self.played_cards_frame.pack(pady=10, expand=True)

            # Reapply wood texture to played_cards_frame
            try:
                folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
                texture_path = os.path.join(folder_path, "wood_texture.jpg")
                if os.path.exists(texture_path):
                    texture_img = Image.open(texture_path)
                    texture_img = texture_img.resize((300, 180), Image.Resampling.LANCZOS)
                    self.trick_texture = ImageTk.PhotoImage(texture_img)
                    self.card_images.append(self.trick_texture)  # Store to prevent garbage collection
                    self.texture_label = tk.Label(self.played_cards_frame, image=self.trick_texture)
                    self.texture_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.texture_label.lower()
                else:
                    print(f"Wood texture not found at {texture_path}, using default background")
                    self.played_cards_frame.configure(bg="#194c22")
            except Exception as e:
                print(f"Error loading wood texture: {e}")
                self.played_cards_frame.configure(bg="#194c22")

            # Place the trick label directly on the wood texture
            tk.Label(self.played_cards_frame, text=f"Trick {self.current_trick_number}", font=("Arial", 12), bg="#57311a", fg="white").place(relx=0.5, rely=0, anchor="n", y=5)

            # Rebind resize handler
            def resize_trick_texture(event):
                try:
                    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
                    texture_path = os.path.join(folder_path, "wood_texture.jpg")
                    if os.path.exists(texture_path):
                        texture_img = Image.open(texture_path)
                        frame_width = max(event.width, 1)
                        frame_height = max(event.height, 1)
                        texture_img = texture_img.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
                        self.trick_texture = ImageTk.PhotoImage(texture_img)
                        self.card_images.append(self.trick_texture)  # Store to prevent garbage collection
                        if self.texture_label and self.texture_label.winfo_exists():
                            self.texture_label.configure(image=self.trick_texture)
                except Exception as e:
                    print(f"Error resizing wood texture: {e}")

            self.played_cards_frame.bind("<Configure>", resize_trick_texture)

            self.played_cards_frame.grid_columnconfigure(0, weight=1)
            self.played_cards_frame.grid_columnconfigure(1, weight=1)
            self.played_cards_frame.grid_columnconfigure(2, weight=1)
            self.played_cards_frame.grid_rowconfigure(0, weight=1)
            
            self.left_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
            self.left_frame.grid(row=0, column=0, sticky="n")
            
            self.current_cards_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
            self.current_cards_frame.place(relx=0.5, rely=0, anchor="n", y=30)
            
            self.right_frame = tk.Frame(self.played_cards_frame, bg="#57311a")
            self.right_frame.grid(row=0, column=2, sticky="n")
            
            # Show the combined prompt with the trick result
            self.show_next_player_prompt(trick_result=trick_result)
        else:
            # For the last trick, show the result before proceeding to scoring
            for widget in self.root.winfo_children():
                widget.destroy()
                
            prompt_frame = tk.Frame(self.root, bg="#194c22")
            prompt_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(prompt_frame, text="Trick Result", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
            tk.Label(prompt_frame, text=trick_result, font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=10)
            tk.Label(prompt_frame, text="This was the last trick. Proceeding to scoring...",
                     font=("Arial", 16), bg="#194c22", fg="white", wraplength=400).pack(pady=20)
            
            tk.Button(prompt_frame, text="Continue", font=("Arial", 14),
                      command=self._score_round_without_ui_update, bg="#f5e1bf", width=15, height=2).pack(pady=30)

    def _score_round_without_ui_update(self):
        """Helper method to score the round without updating the UI, since the UI is cleared."""
        self.current_phase = "scoring"
        self.differences = {}  # Store differences for score breakdown
        for player in self.players:
            # Calculate points from cards won
            points_won = sum(card.point_value for card in self.cards_won[player.name])
            bid = player.bid
            self.differences[player.name] = abs(bid - points_won)
        
        for player in self.players:
            opponent_diffs = [self.differences[opponent.name] for opponent in self.players if opponent != player]
            base_score = sum(opponent_diffs)
            bonus = 0
            player_points_won = sum(card.point_value for card in self.cards_won[player.name])
            difference = self.differences[player.name]
            if difference == 0:
                bonus = 30
            elif difference <= 2:
                bonus = 20
            elif difference <= 5:
                bonus = 10
            player.round_score = base_score + bonus
            player.score += player.round_score
            # Store scoring details for the current round
            player.scoring_details = {
                'base_score': base_score,
                'bonus': bonus,
                'points_won': player_points_won,
                'difference': difference,
                'num_cards_won': len(self.cards_won[player.name])
            }
            # Update cumulative stats
            player.cumulative_stats['total_tricks_won'] += self.tricks_won[player.name]
            player.cumulative_stats['total_points_won'] += player_points_won
            player.cumulative_stats['total_cards_won'] += len(self.cards_won[player.name])
            player.cumulative_stats['total_bonus'] += bonus
            player.cumulative_stats['bids'].append((player.bid, player_points_won))  # Use player.bid directly
            player.cumulative_stats['round_scores'].append(player.round_score)
            player.cumulative_stats['differences'].append(difference)
            player.cumulative_stats['bonuses'].append(bonus)
        
        # Only show the "Round Result" message if the game will continue (i.e., not the last round)
        if not (self.win_condition == 2 and self.current_round >= self.max_rounds):
            round_winner = max(self.players, key=lambda p: p.round_score)
            messagebox.showinfo("Round Result", f"Round {self.current_round} Complete!\n"
                                f"Round Winner: {round_winner.name} with {round_winner.round_score} points")
        
        self.check_game_over()

    def score_round(self):
        self.current_phase = "scoring"
        self.differences = {}  # Store differences for score breakdown
        for player in self.players:
            # Calculate points from cards won
            points_won = sum(card.point_value for card in self.cards_won[player.name])
            bid = player.bid
            self.differences[player.name] = abs(bid - points_won)
        
        for player in self.players:
            opponent_diffs = [self.differences[opponent.name] for opponent in self.players if opponent != player]
            base_score = sum(opponent_diffs)
            bonus = 0
            player_points_won = sum(card.point_value for card in self.cards_won[player.name])
            difference = self.differences[player.name]
            if difference == 0:
                bonus = 30
            elif difference <= 2:
                bonus = 20
            elif difference <= 5:
                bonus = 10
            player.round_score = base_score + bonus
            player.score += player.round_score
            # Store scoring details for the current round
            player.scoring_details = {
                'base_score': base_score,
                'bonus': bonus,
                'points_won': player_points_won,
                'difference': difference,
                'num_cards_won': len(self.cards_won[player.name])
            }
            # Update cumulative stats
            player.cumulative_stats['total_tricks_won'] += self.tricks_won[player.name]
            player.cumulative_stats['total_points_won'] += player_points_won
            player.cumulative_stats['total_cards_won'] += len(self.cards_won[player.name])
            player.cumulative_stats['total_bonus'] += bonus
            player.cumulative_stats['bids'].append((player.bid, player_points_won))  # Use player.bid directly
            player.cumulative_stats['round_scores'].append(player.round_score)
            player.cumulative_stats['differences'].append(difference)
            player.cumulative_stats['bonuses'].append(bonus)
        
        self.update_scores()
        
        round_winner = max(self.players, key=lambda p: p.round_score)
        messagebox.showinfo("Round Result", f"Round {self.current_round} Complete!\n"
                            f"Round Winner: {round_winner.name} with {round_winner.round_score} points")
        
        self.check_game_over()

    def check_game_over(self):
        # Always sort players by score to determine winners
        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        max_score = sorted_players[0].score
        winners = [player for player in sorted_players if player.score == max_score]

        # Check win conditions
        if self.win_condition == 1:
            # Target Score: Game ends when at least one player reaches or exceeds the target
            if max_score >= self.target_score:
                self.game_over = True
                self.show_game_over_screen()
        elif self.win_condition == 2 and self.current_round >= self.max_rounds:
            # Set Deals: Game ends after the specified number of deals
            self.game_over = True
            self.show_game_over_screen()
        
        if not self.game_over:
            self.players.append(self.players.pop(0))
            self.current_round += 1
            messagebox.showinfo("Next Round", f"Next round dealer: {self.players[0].name}\nClick OK to start Round {self.current_round}")
            self.start_round()

    def show_game_over_screen(self):
        self.current_phase = "game_over"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        game_over_frame = tk.Frame(self.root, bg="#194c22")
        game_over_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(game_over_frame, text="Game Over!", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
        
        # Sort all players by score in descending order
        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        max_score = sorted_players[0].score
        winners = [player for player in sorted_players if player.score == max_score]
        
        # Display results based on the number of winners
        if len(winners) == 1:
            # One winner
            winner = winners[0]
            second = sorted_players[1]
            third = sorted_players[2]
            tk.Label(game_over_frame, text=f"🥇 {winner.name} won with {winner.score} points! 🥇",
                     font=("Arial", 18), bg="#194c22", fg="white").pack(pady=10)
            tk.Label(game_over_frame, text=f"🥈 {second.name} was second with {second.score} points. 🥈",
                     font=("Arial", 16), bg="#194c22", fg="white").pack(pady=10)
            tk.Label(game_over_frame, text=f"🥉 {third.name} was third with {third.score} points. 🥉",
                     font=("Arial", 16), bg="#194c22", fg="white").pack(pady=10)
        elif len(winners) == 2:
            # Two-way draw for first place
            tied_names = " and ".join(winner.name for winner in winners)
            last_player = sorted_players[-1]  # The player who came last
            tk.Label(game_over_frame, text=f"🎖️ {tied_names} tied for first with {winners[0].score} points! 🎖️",
                     font=("Arial", 18), bg="#194c22", fg="white").pack(pady=10)
            tk.Label(game_over_frame, text=f"🥉 {last_player.name} was third with {last_player.score} points. 🥉",
                     font=("Arial", 16), bg="#194c22", fg="white").pack(pady=10)
        else:
            # Three-way draw
            tied_names = ", ".join(winner.name for winner in winners)
            tk.Label(game_over_frame, text=f"🎖️ {tied_names} tied with {winners[0].score} points! 🎖️",
                     font=("Arial", 18), bg="#194c22", fg="white").pack(pady=10)

        tk.Button(game_over_frame, text="Show Score Breakdown", font=("Arial", 14),
                  command=self.show_score_breakdown, bg="#f5e1bf", width=20, height=2).pack(pady=20)
        
        tk.Button(game_over_frame, text="New Game", font=("Arial", 14),
                  command=self.get_game_settings, bg="#f5e1bf", width=15, height=2).pack(pady=10)
        
        tk.Button(game_over_frame, text="Exit", font=("Arial", 14),
                  command=self.root.destroy, bg="#f5e1bf", width=15, height=2).pack(pady=10)

    def show_score_breakdown(self):
        self.current_phase = "score_breakdown"
        for widget in self.root.winfo_children():
            widget.destroy()
            
        breakdown_frame = tk.Frame(self.root, bg="#194c22")
        breakdown_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(breakdown_frame, text="Score Breakdown", font=("Arial", 24, "bold"), bg="#194c22", fg="white").pack(pady=20)
        
        # Create a Treeview to display the score breakdown
        columns = ("Metric", self.players[0].name, self.players[1].name, self.players[2].name)
        tree = ttk.Treeview(breakdown_frame, columns=columns, show="headings", height=10)
        
        # Set column headings
        tree.heading("Metric", text="Metric")
        for player in self.players:
            tree.heading(player.name, text=player.name)
            tree.column(player.name, width=200, anchor=tk.CENTER)
        tree.column("Metric", width=150, anchor=tk.W)
        
        # Populate the table
        # Total Score
        total_scores = [str(player.score) for player in self.players]
        tree.insert("", "end", values=("Total Score", total_scores[0], total_scores[1], total_scores[2]))
        
        # Bidding Results (Bid vs Points Won per round)
        bidding_results = []
        for player in self.players:
            bids_summary = "; ".join(f"R{idx+1}: Bid {bid}, Won {won}" for idx, (bid, won) in enumerate(player.cumulative_stats['bids']))
            bidding_results.append(bids_summary if bids_summary else "None")
        tree.insert("", "end", values=("Bidding Results", bidding_results[0], bidding_results[1], bidding_results[2]))
        
        # Differences per round
        differences = []
        for player in self.players:
            diff_summary = "; ".join(f"R{idx+1}: {diff}" for idx, diff in enumerate(player.cumulative_stats['differences']))
            differences.append(diff_summary if diff_summary else "None")
        tree.insert("", "end", values=("Differences", differences[0], differences[1], differences[2]))
        
        # Bonuses per round
        bonuses = []
        for player in self.players:
            bonus_summary = "; ".join(f"R{idx+1}: {bonus}" for idx, bonus in enumerate(player.cumulative_stats['bonuses']))
            bonuses.append(bonus_summary if bonus_summary else "None")
        tree.insert("", "end", values=("Bonuses", bonuses[0], bonuses[1], bonuses[2]))
        
        # Round Scores
        round_scores = []
        for player in self.players:
            scores_summary = "; ".join(f"R{idx+1}: {score}" for idx, score in enumerate(player.cumulative_stats['round_scores']))
            round_scores.append(scores_summary if scores_summary else "None")
        tree.insert("", "end", values=("Round Scores", round_scores[0], round_scores[1], round_scores[2]))
        
        # Total Tricks Won
        tricks_won = [str(player.cumulative_stats['total_tricks_won']) for player in self.players]
        tree.insert("", "end", values=("Total Tricks Won", tricks_won[0], tricks_won[1], tricks_won[2]))
        
        # Total Points from Cards
        points_won = [str(player.cumulative_stats['total_points_won']) for player in self.players]
        tree.insert("", "end", values=("Total Points from Cards", points_won[0], points_won[1], points_won[2]))
        
        # Total Cards Won
        cards_won = [str(player.cumulative_stats['total_cards_won']) for player in self.players]
        tree.insert("", "end", values=("Total Cards Won", cards_won[0], cards_won[1], cards_won[2]))
        
        # Total Bonus Points
        total_bonus = [str(player.cumulative_stats['total_bonus']) for player in self.players]
        tree.insert("", "end", values=("Total Bonus Points", total_bonus[0], total_bonus[1], total_bonus[2]))
        
        # Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(breakdown_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Button(breakdown_frame, text="Back to results", font=("Arial", 14),
                  command=self.show_game_over_screen, bg="#f5e1bf", width=20, height=2).pack(pady=20)

    def show_help(self):
        messagebox.showinfo("Game Rules", "CounterPoint Rules:\n\n"
                            "1. The game is played with a deck of 37 cards (standard deck + Joker).\n"
                            "2. Each player is dealt 12 cards, and the last card is revealed as the trump card.\n"
                            "3. If the trump card is a Nine or Joker, there is no trump suit for that round.\n"
                            "4. Bidding Phase: Each player selects 3 cards to discard. The bid is calculated as:\n"
                            "   - Spades: 10 points each\n"
                            "   - Hearts: 20 points each\n"
                            "   - Clubs: 30 points each\n"
                            "   - Diamonds/Joker: 0 points\n"
                            "5. Trick Phase: Play 9 tricks. Players must follow suit if possible. The highest card of the lead suit wins, unless a trump card is played.\n"
                            "6. Scoring:\n"
                            "   - Points from cards: Ace (11), Ten (10), King (4), Queen (3), Jack (2), others (0).\n"
                            "   - Base Score: Sum of the differences of the other two players.\n"
                            "   - Difference: Bid - Points won on tricks (each trick winner gets the 3 cards played during that trick) .\n"
                            "   - Round Score: Base score + bonus.\n"
                            "   - Bonus: +30 if difference = 0, +20 if difference ≤ 2, +10 if difference ≤ 5.\n"
                            "7. Win Conditions:\n"
                            "   - Target Score: First to reach the target wins.\n"
                            "   - Set Deals: Player with the highest score after set deals wins.\n"
                            "8. After each round, the dealer rotates to the player on the left.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CounterPointGame()
    game.run()
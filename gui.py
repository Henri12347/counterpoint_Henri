import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk  # Requires 'pillow' library
import os
import random

class CounterPointGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CounterPoint")
        # Set a minimum size for the window
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.card_images = []  # Cache images to avoid garbage collection
        self.player_names = ["Player 1", "Player 2", "Player 3"]
        self.trump_card = None
        self.show_welcome_screen()
        
    def show_welcome_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create welcome frame
        welcome_frame = tk.Frame(self.root)
        welcome_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(welcome_frame, text="CounterPoint", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Buttons
        start_button = tk.Button(welcome_frame, text="Start Game", font=("Arial", 14),
                                 command=self.get_player_names, width=15, height=2)
        start_button.pack(pady=10)
        
        rules_button = tk.Button(welcome_frame, text="Game Rules", font=("Arial", 14),
                                command=self.show_help, width=15, height=2)
        rules_button.pack(pady=10)
        
        exit_button = tk.Button(welcome_frame, text="Exit", font=("Arial", 14),
                               command=self.root.destroy, width=15, height=2)
        exit_button.pack(pady=10)
    
    def get_player_names(self):
        # Ask for all 3 player names
        for i in range(3):
            name = simpledialog.askstring("Player Names", f"Enter name for Player {i+1}:", parent=self.root)
            if name:
                self.player_names[i] = name
            
        # Show trump card screen
        self.select_trump_card()
    
    def select_trump_card(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create trump card frame
        trump_frame = tk.Frame(self.root)
        trump_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(trump_frame, text="Trump Card Selection", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        # Select a random card for trump
        suits = ['hearts', 'spades', 'clubs', 'diamonds']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        # Add Joker as a possibility
        all_cards = [(rank, suit) for rank in ranks for suit in suits]
        all_cards.append(("Joker", None))
        
        self.trump_card = random.choice(all_cards)
        rank, suit = self.trump_card
        
        # Display the trump card
        card_frame = tk.Frame(trump_frame)
        card_frame.pack(pady=20)
        
        img = self.load_card_image(rank, suit, size=(100, 150))  # Larger card for better visibility
        if img:
            self.card_images.append(img)
            card_label = tk.Label(card_frame, image=img)
            card_label.pack()
        else:
            # Fallback if image doesn't load
            placeholder = tk.Label(card_frame, text=f"{rank} of {suit if suit else ''}", 
                                  width=10, height=15, relief="raised", bg="white", font=("Arial", 12))
            placeholder.pack()
        
        # Trump info text
        if rank == '9' or rank == 'Joker':
            info_text = "There is no trump suit for this round!"
        else:
            info_text = f"The trump suit is: {suit.upper()}"
        
        trump_info = tk.Label(trump_frame, text=info_text, font=("Arial", 16))
        trump_info.pack(pady=20)
        
        # Continue button
        continue_btn = tk.Button(trump_frame, text="Continue to Game", font=("Arial", 14),
                               command=self.setup_game_ui, width=15, height=2)
        continue_btn.pack(pady=20)
    
    def setup_game_ui(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Setup the main container with grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_rowconfigure(2, weight=2)
            
        # ===== Menu Bar =====
        menu_bar = tk.Menu(self.root)
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.get_player_names)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Rules", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

        # ===== Game Area Frames =====
        # Top frame for scores and status
        top_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=5)
        top_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        
        # Left player frame
        left_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=5)
        left_frame.grid(row=1, column=0, sticky="ns")
        
        # Center game area
        center_frame = tk.Frame(self.root, bg="#f8f8f8", padx=10, pady=10)
        center_frame.grid(row=1, column=1, sticky="nsew")
        
        # Right player frame
        right_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=5)
        right_frame.grid(row=1, column=2, sticky="ns")
        
        # Bottom player frame
        bottom_frame = tk.Frame(self.root, bg="#e8e8e8", padx=10, pady=10)
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky="ew")

        # ===== Player Labels =====
        left_label = tk.Label(left_frame, text=f"{self.player_names[0]}", 
                             font=("Arial", 12, "bold"), bg="#f0f0f0")
        left_label.pack(pady=5)
        
        right_label = tk.Label(right_frame, text=f"{self.player_names[1]}", 
                              font=("Arial", 12, "bold"), bg="#f0f0f0")
        right_label.pack(pady=5)
        
        bottom_label = tk.Label(bottom_frame, text=f"{self.player_names[2]}", 
                               font=("Arial", 12, "bold"), bg="#e8e8e8")
        bottom_label.pack(pady=5)

        # ===== Test Cards =====
        test_hand = [
            ("2", "clubs"), ("3", "hearts"), ("4", "spades"),
            ("5", "diamonds"), ("6", "clubs"), ("7", "hearts"),
            ("8", "spades"), ("9", "diamonds"), ("10", "clubs"),
            ("2", "hearts"), ("3", "spades"), ("4", "diamonds"), 
        ]

        # Create scrollable card frames
        self.create_scrollable_cards(left_frame, test_hand, vertical=True)
        self.create_scrollable_cards(right_frame, test_hand, vertical=True)
        self.create_scrollable_cards(bottom_frame, test_hand, interactive=True)

        # ===== Top Info Area =====
        # Scores at the top
        scores_text = f"Scores — {self.player_names[0]}: 0 | {self.player_names[1]}: 0 | {self.player_names[2]}: 0"
        score_label = tk.Label(top_frame, text=scores_text, font=("Arial", 14, "bold"), bg="#e0e0e0")
        score_label.pack(pady=10)
        
        # ===== Center Game Area =====
        # Trump card display
        trump_frame = tk.Frame(center_frame, bg="#f8f8f8", padx=5, pady=5)
        trump_frame.pack(pady=10)
        
        rank, suit = self.trump_card
        trump_label = tk.Label(trump_frame, text="Trump Card:", font=("Arial", 14), bg="#f8f8f8")
        trump_label.pack(side="left", padx=5)
        
        img = self.load_card_image(rank, suit, size=(60, 90))
        if img:
            self.card_images.append(img)
            trump_img = tk.Label(trump_frame, image=img, bg="#f8f8f8")
            trump_img.pack(side="left")
        
        # Trump suit text
        if rank == '9' or rank == 'Joker':
            trump_text = "No Trump Suit"
        else:
            trump_text = f"Trump Suit: {suit.upper()}"
        
        tk.Label(center_frame, text=trump_text, font=("Arial", 14), bg="#f8f8f8").pack(pady=5)
        
        # Current turn indicator
        turn_label = tk.Label(center_frame, text=f"Turn: {self.player_names[0]}", 
                            font=("Arial", 16, "bold"), fg="blue", bg="#f8f8f8")
        turn_label.pack(pady=10)
        
        # Current trick area
        trick_frame = tk.Frame(center_frame, bg="#e0f0e0", width=300, height=200, 
                              relief=tk.GROOVE, bd=2)
        trick_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        trick_frame.pack_propagate(False)  # Prevent the frame from shrinking
        
        tk.Label(trick_frame, text="Current Trick", font=("Arial", 12), bg="#e0f0e0").pack(pady=10)
        
        # Area for played cards in the trick
        played_cards_frame = tk.Frame(trick_frame, bg="#e0f0e0")
        played_cards_frame.pack(pady=10, expand=True)
    
    def create_scrollable_cards(self, parent, cards, vertical=False, interactive=False):
        # Create a canvas with scrollbar for cards
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a canvas
        canvas = tk.Canvas(canvas_frame)
        
        # Add scrollbar
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
            
        # Create a frame inside the canvas to hold cards
        cards_frame = tk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=cards_frame, anchor="nw")
        
        def on_card_click(card_btn, rank, suit):
            print(f"Card clicked: {rank} of {suit}")
            card_btn.config(state="disabled", relief="sunken")
           
          
        
        # Add cards to the frame
        for rank, suit in cards:
            img = self.load_card_image(rank, suit, size=(60, 90))
            if img:
                self.card_images.append(img)  # Keep reference to prevent garbage collection
                if interactive:
                    card_btn = tk.Button(cards_frame, image=img)
                    card_btn.config(command=lambda b=card_btn, r=rank, s=suit: on_card_click(b, r, s))
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
                # Fallback if image doesn't load
                placeholder = tk.Label(cards_frame, text=f"{rank} {suit}", width=5, height=7, 
                                     relief="raised", bg="white")
                if vertical:
                    placeholder.pack(pady=2)
                else:
                    placeholder.pack(side=tk.LEFT, padx=2)
        
        # Update scroll region when the frame changes size
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if vertical:
                canvas.configure(width=cards_frame.winfo_reqwidth())
            else:
                canvas.configure(height=cards_frame.winfo_reqheight())
        
        cards_frame.bind("<Configure>", configure_canvas)
        
        # Make sure the cards frame is wide/tall enough
        if vertical:
            cards_frame.config(width=100)  # Set minimum width
        else:
            cards_frame.config(height=110)  # Set minimum height
    
    def load_card_image(self, rank, suit, size=(60, 90)):
        try:
            if rank == "Joker":
                filename = "Joker.png"
            else:
                filename = f"{rank}_of_{suit}.png"
                
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
            path = os.path.join(folder_path, filename)
            
            # Debug printing
            if not os.path.exists(path):
                print(f"File not found: {path}")
                if not os.path.exists(folder_path):
                    print(f"Images directory not found: {folder_path}")
                    print(f"Current directory: {os.path.dirname(os.path.abspath(__file__))}")
                
            img = Image.open(path).resize(size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading {rank} of {suit if suit else ''}: {e}")
            return None

    def connect_game_logic(self, game_logic):
        self.game_logic = game_logic
        # Here you would implement the connection between GUI and game logic
        
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
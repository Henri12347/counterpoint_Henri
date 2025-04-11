import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Requires 'pillow' library
import os

def start_gui():
    def on_start():
        messagebox.showinfo("Start Game", "Card images loaded — game logic still to be implemented.")

    def on_exit():
        root.destroy()

    def show_help():
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

    def load_card_image(rank, suit):
     filename = f"{rank}_of_{suit}.png" if suit else "Joker.png"
     folder_path = os.path.join(os.path.dirname(__file__), "images")
     path = os.path.join(folder_path, filename)
    
     try:
        img = Image.open(path).resize((50, 75))
        return ImageTk.PhotoImage(img)
     except Exception as e:
        print(f"Error loading {path}: {e}")
        return None


    root = tk.Tk()
    root.title("CounterPoint")
    root.geometry("1000x700")

    # ===== Menu Bar =====
    menu_bar = tk.Menu(root)
    game_menu = tk.Menu(menu_bar, tearoff=0)
    game_menu.add_command(label="New Game", command=on_start)
    game_menu.add_separator()
    game_menu.add_command(label="Exit", command=on_exit)
    menu_bar.add_cascade(label="Game", menu=game_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Rules", command=show_help)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menu_bar)

    # ===== Layout Frames =====
    top_frame = tk.Frame(root, height=100)
    top_frame.pack(side="top", fill="x")

    middle_frame = tk.Frame(root)
    middle_frame.pack(expand=True, fill="both")

    left_frame = tk.Frame(middle_frame, width=150)
    left_frame.pack(side="left", fill="y")

    right_frame = tk.Frame(middle_frame, width=150)
    right_frame.pack(side="right", fill="y")

    center_frame = tk.Frame(middle_frame)
    center_frame.pack(expand=True)

    bottom_frame = tk.Frame(root, height=150)
    bottom_frame.pack(side="bottom", fill="x")

    # ===== Player Labels =====
    tk.Label(top_frame, text="Player 1 (Top)", font=("Arial", 12)).pack()
    tk.Label(left_frame, text="Player 2 (Left)", font=("Arial", 12)).pack()
    tk.Label(right_frame, text="Player 3 (Right)", font=("Arial", 12)).pack()
    tk.Label(bottom_frame, text="You (Bottom)", font=("Arial", 12)).pack()

    # ===== Load Cards =====
    suits = ['hearts', 'spades', 'clubs', 'diamonds']
    ranks = ['A', '10', 'K', 'Q', 'J', '9', '8', '7', '6']
    test_hand  = [
    ("2", "clubs"), ("3", "hearts"), ("4", "spades"),
    ("5", "diamonds"), ("6", "clubs"), ("7", "hearts"),
    ("8", "spades"), ("9", "diamonds"), ("10", "clubs"),
    ("2", "hearts"), ("3", "spades"), ("4", "diamonds"), 
]


    # Cache images to avoid garbage collection
    card_images = []

    def display_cards(frame, is_horizontal=True):
        inner = tk.Frame(frame)
        inner.pack()
        for rank, suit in test_hand:
            img = load_card_image(rank, suit)
            if img:
                lbl = tk.Label(inner, image=img)
                lbl.pack(side="left" if is_horizontal else "top", padx=2, pady=2)
                card_images.append(img)

    display_cards(top_frame)
    display_cards(left_frame, is_horizontal=False)
    display_cards(right_frame, is_horizontal=False)
    display_cards(bottom_frame)

    # ===== Center Info =====
    tk.Label(center_frame, text="Turn: Player 1", font=("Arial", 16), fg="blue").pack(pady=10)
    tk.Label(center_frame, text="Trump Suit: ♠", font=("Arial", 14)).pack()
    tk.Label(center_frame, text="Scores — P1: 0 | P2: 0 | P3: 0", font=("Arial", 12)).pack(pady=10)

    root.mainloop()

start_gui()

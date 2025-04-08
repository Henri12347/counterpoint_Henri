import tkinter as tk
from tkinter import messagebox

def start_gui():
    def on_start():
        messagebox.showinfo("Start Game", "Game will start (GUI logic to be implemented).")

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

    root = tk.Tk()
    root.title("CounterPoint")
    root.geometry("400x300")

    # Menu Bar
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

    # Title and Start Button
    title_label = tk.Label(root, text="CounterPoint", font=("Arial", 24))
    title_label.pack(pady=40)

    start_button = tk.Button(root, text="Start Game", command=on_start, font=("Arial", 14), width=15)
    start_button.pack(pady=20)

    root.mainloop()

start_gui()

import tkinter as tk
from tkinter import messagebox

def start_gui():
    def on_start():
        messagebox.showinfo("Start Game", "Game will start (GUI logic to be implemented).")

    root = tk.Tk()
    root.title("CounterPoint")
    root.geometry("400x300")

    title_label = tk.Label(root, text="CounterPoint", font=("Arial", 24))
    title_label.pack(pady=40)

    start_button = tk.Button(root, text="Start Game", command=on_start, font=("Arial", 14), width=15)
    start_button.pack(pady=20)

    root.mainloop()


start_gui()

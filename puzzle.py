import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import heapq
MAX_BOARD_SIZE = 500


class Application(tk.Frame):
    def __init__(self, image, board_grid=4):
        super().__init__()
        self.grid()
        self.board_grid = max(board_grid, 3)
        self.load_image(image)
        self.steps = 0
        self.create_widgets()
        self.create_events()
        self.create_board()
        self.show()

    def load_image(self, image):
        try:
            image = Image.open(image)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file '{image}' not found.")

        board_size = min(image.size)
        if image.size[0] != image.size[1]:
            image = image.crop((0, 0, board_size, board_size))
        if board_size > MAX_BOARD_SIZE:
            board_size = MAX_BOARD_SIZE
            image = image.resize((board_size, board_size), Image.AFFINE)
        self.image = image
        self.board_size = board_size
        self.piece_size = self.board_size / self.board_grid

    def create_widgets(self):
        args = dict(width=self.board_size, height=self.board_size)
        self.canvas = tk.Canvas(self, **args)
        self.canvas.grid()

    def create_events(self):
        self.canvas.bind_all("<KeyPress-Up>", self.slide)
        self.canvas.bind_all("<KeyPress-Down>", self.slide)
        self.canvas.bind_all("<KeyPress-Left>", self.slide)
        self.canvas.bind_all("<KeyPress-Right>", self.slide)
        self.canvas.bind_all("<KeyPress-h>", self.slide)
        self.canvas.bind_all("<KeyPress-j>", self.slide)
        self.canvas.bind_all("<KeyPress-k>", self.slide)
        self.canvas.bind_all("<KeyPress-l>", self.slide)
        self.canvas.bind_all("<KeyPress-H>", self.help)

    def help(self, event):
        if getattr(self, "_img_help_id", None) is None:
            self._img_help = ImageTk.PhotoImage(self.image)
            self._img_help_id = self.canvas.create_image(
                0, 0, image=self._img_help, anchor=tk.NW
            )
        else:
            state = self.canvas.itemconfig(self._img_help_id, "state")[-1]
            state = "hidden" if state == "normal" else "normal"
            self.canvas.itemconfig(self._img_help_id, state=state)

    def slide(self, event):
        pieces = self.get_pieces_around()
        if event.keysym in ("Up", "k") and pieces["bottom"]:
            self._slide(pieces["bottom"], pieces["center"], (0, -self.piece_size))
        if event.keysym in ("Down", "j") and pieces["top"]:
            self._slide(pieces["top"], pieces["center"], (0, self.piece_size))
        if event.keysym in ("Left", "h") and pieces["right"]:
            self._slide(pieces["right"], pieces["center"], (-self.piece_size, 0))
        if event.keysym in ("Right", "l") and pieces["left"]:
            self._slide(pieces["left"], pieces["center"], (self.piece_size, 0))
        self.check_status()

    def _slide(self, from_, to, coord):
        self.canvas.move(from_["id"], *coord)
        to["pos_a"], from_["pos_a"] = from_["pos_a"], to["pos_a"]
        self.steps += 1

    def get_pieces_around(self):
        pieces = {
            "center": None,
            "right": None,
            "left": None,
            "top": None,
            "bottom": None,
        }
        for piece in self.board:
            if not piece["visible"]:
                pieces["center"] = piece
                break
        x0, y0 = pieces["center"]["pos_a"]
        for piece in self.board:
            x1, y1 = piece["pos_a"]
            if y0 == y1 and x1 == x0 + 1:
                pieces["right"] = piece
            if y0 == y1 and x1 == x0 - 1:
                pieces["left"] = piece
            if x0 == x1 and y1 == y0 - 1:
                pieces["top"] = piece
            if x0 == x1 and y1 == y0 + 1:
                pieces["bottom"] = piece
        return pieces

    def create_board(self):
        self.board = []
        for x in range(self.board_grid):
            for y in range(self.board_grid):
                x0 = x * self.piece_size
                y0 = y * self.piece_size
                x1 = x0 + self.piece_size
                y1 = y0 + self.piece_size
                image = ImageTk.PhotoImage(self.image.crop((x0, y0, x1, y1)))
                piece = {
                    "id": None,
                    "image": image,
                    "pos_o": (x, y),
                    "pos_a": None,
                    "visible": True,
                }
                self.board.append(piece)
        self.board[-1]["visible"] = False

    def check_status(self):
        for piece in self.board:
            if piece["pos_a"] != piece["pos_o"]:
                return
        title = "Ganaste!"
        message = f"Lo resolviste en {self.steps} movidas!"
        messagebox.showinfo(title, message)

    def show(self):
        random.shuffle(self.board)
        index = 0
        for x in range(self.board_grid):
            for y in range(self.board_grid):
                self.board[index]["pos_a"] = (x, y)
                if self.board[index]["visible"]:
                    x1 = x * self.piece_size
                    y1 = y * self.piece_size
                    image = self.board[index]["image"]
                    id = self.canvas.create_image(x1, y1, image=image, anchor=tk.NW)
                    self.board[index]["id"] = id
                index += 1

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Sliding puzzle")
    parser.add_argument(
        "-g", "--board-grid", type=int, default=4, help="(the minimum value is 3)"
    )
    parser.add_argument(
        "-i", "--image", type=str, default="spider.jpg", help="path to image"
    )
    args = parser.parse_args()

    if args.board_grid < 3:
        args.board_grid = 3
        print("Warning: using 3 for board-grid")

    app = Application('spider.jpg', 4)
    app.master.title("Sliding puzzle")
    app.mainloop()


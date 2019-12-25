from tkinter import *
import csv
from math import sqrt

WIDTH = 400
HEIGHT = 400
grid = []
train_entry = []
train_output = []


class Block:
    def __init__(self, canvas, x1, y1, x2, y2):
        self.square = canvas.create_rectangle(x1, y1, x2, y2)
        self.canvas = canvas
        self.pos = x1, y1
        self.x_size = x2 - x1
        self.y_size = y2 - y1
        self.filled = 0

    def in_square(self, touch):
        if self.pos[0] < touch[0] < self.pos[0] + self.x_size:
            if self.pos[1] < touch[1] < self.pos[1] + self.y_size:
                return True
        return False

    def fill(self):
        self.filled = 1
        self.canvas.itemconfig(self.square, fill='black')

    def clear(self):
        self.filled = 0
        self.canvas.itemconfig(self.square, fill='white')


class Neighbour:
    def __init__(self, csv_row):
        self.number = int(csv_row[0])
        self.pixels = list(map(int, csv_row[1:]))
        self.distance = 99999999

    def neighbour_distance(self, drawing_grid):
        distance = 0
        for i in range(len(drawing_grid)):
            if drawing_grid[i].filled != self.pixels[i]:
                distance += 100

        self.distance = distance
        return distance


def main():
    root = Tk()
    canvas = create_canvas(root)
    create_grid(50, 25, 28, 28, 10, canvas)
    create_ui(canvas)
    canvas.pack()
    root.mainloop()


def create_canvas(root):
    canvas = Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.bind("<Button-1>", click)
    canvas.bind("<B1-Motion>", click)
    return canvas


def create_grid(x, y, width, height, size, canvas):
    for h in range(1, height + 1):
        for w in range(1, width + 1):
            block = Block(canvas, x + w * size, y + h * size, x + (w + 1) * size, y + (h + 1) * size)
            grid.append(block)


def create_ui(canvas):
    textbox = Entry(canvas)
    canvas.create_window(265, 335, window=textbox, height=20, width=20)
    submit = Button(canvas, text="Submit", command=save_data)
    canvas.create_window(315, 335, window=submit, height=20, width=50)
    guess = Button(canvas, text="Guess", command=get_guess)
    canvas.create_window(175, 335, window=guess, height=20)
    clear = Button(canvas, text="Clear", command=clear_grid)
    canvas.create_window(85, 335, window=clear, height=20)
    output_guess = Label(canvas, text="Guess")
    canvas.create_window(175, 360, window=output_guess, height=20)
    output_certainty = Label(canvas, text="Certainty")
    canvas.create_window(175, 380, window=output_certainty, height=20)
    train_entry.append(textbox)
    train_output.append(output_guess)
    train_output.append(output_certainty)


def clear_grid():
    for block in grid:
        block.clear()


# SUBMIT COMMAND SHOULD BE SAVE WINDOW IN ORDER TO PREVENT TAMPERING OF TRAINING DATA
# IN ADDITION THIS DOESN'T YET CHECK FOR A PASSWORD
def save_window():
    window = Tk()
    canvas = Canvas(window)
    label = Label(canvas, text="Enter password")
    label.pack()
    textbox = Entry(canvas)
    textbox.pack()
    submit = Button(canvas, text="Save", command=save_data)
    submit.pack()
    canvas.pack()
    window.title("Save Data")
    window.mainloop()


def save_data():
    record = [train_entry[0].get()]
    for block in grid:
        record.append(str(block.filled))
        block.clear()

    with open('training.csv', mode='a') as train_file:
        train_writer = csv.writer(train_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        train_writer.writerow(record)


def get_guess():
    training_data = []
    with open('training.csv', 'r') as csvfile:
        train_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in train_reader:
            if row:
                training_data.append(row)

    guess, certainty = knn(15, training_data)
    train_output[0].config(text=str(guess))
    train_output[1].config(text=str(certainty))


def knn(k, rows):
    closest_k = []
    for row in rows:
        # index 0 is the classification of the record (the number it represents)
        neighbour = Neighbour(row)
        neighbour.neighbour_distance(grid)
        insert(closest_k, neighbour, 0)
    closest_k = closest_k[:k]
    return count_nn(closest_k)


def count_nn(neighbours):
    numbers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for neighbour in neighbours:
        numbers[neighbour.number] += 1
    print(numbers)
    guess = numbers.index(max(numbers))
    cert = round(max(numbers)/sum(numbers) * 100, 2)
    certainty = str(cert) + "% certainty"
    return [guess, certainty]


def insert(neighbours, neighbour, start_index):
    if len(neighbours) == 0:
        neighbours.append(neighbour)
    if start_index == len(neighbours) - 1:
        neighbours.append(neighbour)
    else:
        if neighbour.distance < neighbours[start_index].distance:
            neighbours.insert(start_index, neighbour)
        else:
            insert(neighbours, neighbour, start_index + 1)


def click(e):
    if True:
        draw((e.x, e.y))


def draw(pos):
    for block in grid:
        if block.in_square(pos):
            block.fill()


main()

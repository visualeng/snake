# -*- coding: utf-8 -*-
# змейка на python, натыкался инструкцию с turtle и решил попробовать
# запуск: python snake.py
# управление: WASD или стрелочки, выход - Esc

import os
import random
import time
import turtle

# куда пишем рекорд, рядом со скриптом
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best.txt")

# настройки, можно крутить
CELL = 20               # размер клетки
SPEED_START = 150       # скорость в мс (меньше = быстрее)
SPEED_STEP = 5          # насколько ускоряемся за каждое яблоко
SPEED_MIN = 60          # предел скорости, дальше некуда

W = 600
H = 600

# цвета
BG = "#1a1a2e"
SNAKE_COLOR = "#00d4aa"
FOOD_COLOR = "#e94560"
TEXT_COLOR = "#ffffff"

score = 0


def load_best():
    """читаем рекорд из файла, если файл первый раз - значит 0"""
    try:
        with open(SAVE_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_best():
    """сохраняем рекорд, чтобы не потеряться"""
    try:
        with open(SAVE_FILE, "w") as f:
            f.write(str(best))
    except OSError:
        pass  # не смог записать - не страхо, просто рекорд не сохранится


best = load_best()  # рекорд, правда честный


def setup():
    """готово к экран, возвращает окно"""
    global screen, pen

    screen = turtle.Screen()
    screen.title("Змейка")
    screen.bgcolor(BG)
    screen.setup(W, H)
    screen.tracer(0)  # без этого тормозит жёстко

    pen = turtle.Turtle()
    pen.speed(0)
    pen.hideturtle()
    pen.penup()

    return screen


def make_square(x, y, color, size=CELL - 2):
    t = turtle.Turtle()
    t.speed(0)
    t.penup()
    t.goto(x, y)
    t.color(color)
    t.shape("square")
    t.shapesize(size / 20)
    return t


def write(text, y, size=20, color=TEXT_COLOR):
    pen.clear()
    pen.goto(0, y)
    pen.color(color)
    pen.write(text, align="center", font=("Segoe UI", size, "bold"))


def make_food():
    t = turtle.Turtle()
    t.speed(0)
    t.penup()
    t.shape("circle")
    t.color(FOOD_COLOR)
    t.shapesize(1.2)
    place_food(t)
    return t


def place_food(t):
    # немного не по центру, чтобы не попадало ровно под змейкой
    x = random.randint(-(W // 2 - CELL), W // 2 - CELL)
    y = random.randint(-(H // 2 - CELL), H // 2 - CELL)
    # округляем до клеток, иначе выглядит криво
    x = (x // CELL) * CELL
    y = (y // CELL) * CELL
    t.goto(x, y)


def main():
    global score, best

    screen = setup()

    # змейка начинается в центре, длина 3
    x = 0
    parts = []
    for _ in range(3):
        t = make_square(x, 0, SNAKE_COLOR)
        parts.append(t)
        x -= CELL

    head = parts[0]
    food = make_food()

    dx, dy = CELL, 0  # летим вправо
    delay = SPEED_START

    def up():
        nonlocal dx, dy
        if dy == 0:  # нельзя развернуться на 180, проверяем
            dx, dy = 0, CELL

    def down():
        nonlocal dx, dy
        if dy == 0:
            dx, dy = 0, -CELL

    def left():
        nonlocal dx, dy
        if dx == 0:
            dx, dy = -CELL, 0

    def right():
        nonlocal dx, dy
        if dx == 0:
            dx, dy = CELL, 0

    screen.listen()
    # стрелки
    screen.onkeypress(up, "Up")
    screen.onkeypress(down, "Down")
    screen.onkeypress(left, "Left")
    screen.onkeypress(right, "Right")
    # и wasd тоже, кому так удобнее
    screen.onkeypress(up, "w")
    screen.onkeypress(down, "s")
    screen.onkeypress(left, "a")
    screen.onkeypress(right, "d")
    screen.onkeypress(screen.bye, "Escape")

    write(f"Очки: 0   Рекорд: {best}", H // 2 - 40)

    while True:
        screen.update()
        time.sleep(delay / 1000)

        # хвост едет по цепочке (сначала тело, потом голова,
        # иначе всё схлопнется в одну точку - было у меня так)
        for i in range(len(parts) - 1, 0, -1):
            parts[i].goto(parts[i - 1].xcor(), parts[i - 1].ycor())

        # теперь двигаем голову
        head.goto(head.xcor() + dx, head.ycor() + dy)

        # врезались в стену?
        if abs(head.xcor()) > W // 2 - CELL // 2 or abs(head.ycor()) > H // 2 - CELL // 2:
            game_over(screen)
            return

        # врезались в себя? (по голове не считаем)
        for p in parts[1:]:
            if p.distance(head) < CELL - 4:
                game_over(screen)
                return

        # съели яблоко?
        if head.distance(food) < CELL:
            # тело растёт - просто добавляем копию хвоста
            tail = parts[-1]
            new = make_square(tail.xcor(), tail.ycor(), SNAKE_COLOR)
            parts.append(new)

            score += 1
            if score > best:
                best = score
                save_best()  # сразу пишем в файл, чтобы не потерять
            place_food(food)

            # ускоряемся понемногу
            delay = max(SPEED_MIN, delay - SPEED_STEP)

            write(f"Очки: {score}   Рекорд: {best}", H // 2 - 40)

    screen.mainloop()


def game_over(screen):
    screen.clear()
    screen.bgcolor(BG)
    save_best()  # на всякий случай пишем ещё раз
    screen.update()  # tracer выключен, без этого ничего не покажет
    t = turtle.Turtle()
    t.hideturtle()
    t.penup()
    t.goto(0, 30)
    t.color(FOOD_COLOR)
    t.write("ИГРА ОКОНЧЕНА", align="center", font=("Segoe UI", 36, "bold"))
    t.goto(0, -30)
    t.color(TEXT_COLOR)
    t.write(f"Твой счёт: {score}    Рекорд: {best}", align="center",
            font=("Segoe UI", 20, "normal"))
    t.goto(0, -80)
    t.color("#888888")
    t.write("нажми Esc чтобы выйти", align="center", font=("Segoe UI", 14, "normal"))
    screen.update()
    screen.listen()
    screen.onkeypress(screen.bye, "Escape")
    screen.mainloop()


if __name__ == "__main__":
    main()

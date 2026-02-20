import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AlgoVision 🔥")

font = pygame.font.SysFont("Segoe UI", 22)

dark_mode = False

def get_colors():
    if dark_mode:
        return {
            "BG": (18, 18, 18),
            "PANEL": (30, 30, 30),
            "BORDER": (70, 70, 70),
            "TEXT": (230, 230, 230),
            "BAR": (100, 149, 237),
            "COMPARE": (255, 99, 71),
            "SORTED": (60, 179, 113),
            "ACTIVE": (186, 85, 211),
            "KEY": (255, 215, 0)
        }
    else:
        return {
            "BG": (255, 255, 255),
            "PANEL": (245, 245, 245),
            "BORDER": (220, 220, 220),
            "TEXT": (40, 40, 40),
            "BAR": (100, 149, 237),
            "COMPARE": (255, 99, 71),
            "SORTED": (60, 179, 113),
            "ACTIVE": (186, 85, 211),
            "KEY": (255, 215, 0)
        }

NUM_BARS = 40
array = []
bar_area_x = 270
bar_width = (WIDTH - bar_area_x) // NUM_BARS

speed = 50
sorting = False
paused = False
algorithm = "Bubble"

comparisons = 0
swaps = 0

i = 0
j = 0
min_index = 0

merge_generator = None
quick_generator = None
insertion_generator = None

def generate_array():
    global array, comparisons, swaps, sorting, paused
    global i, j, merge_generator, quick_generator, insertion_generator

    array = [random.randint(50, 450) for _ in range(NUM_BARS)]
    comparisons = 0
    swaps = 0
    sorting = False
    paused = False
    i = 0
    j = 0

    merge_generator = None
    quick_generator = None
    insertion_generator = None

generate_array()

def draw_bars(highlight1=None, highlight2=None, pivot=None, key_idx=None, sorted_boundary=None, active_range=None):
    colors = get_colors()

    for idx, value in enumerate(array):
        x = idx * bar_width + bar_area_x
        y = HEIGHT - value - 40

        color = colors["BAR"]

        if active_range and active_range[0] <= idx <= active_range[1]:
            color = colors["ACTIVE"]

        if idx == highlight1 or idx == highlight2:
            color = colors["COMPARE"]

        if idx == pivot or idx == key_idx:
            color = colors["KEY"]

        if sorted_boundary is not None and idx < sorted_boundary:
            color = colors["SORTED"]

        pygame.draw.rect(screen, color, (x, y, bar_width - 2, value))

def draw_info():
    colors = get_colors()

    pygame.draw.rect(screen, colors["PANEL"], (0, 0, bar_area_x, HEIGHT))
    pygame.draw.line(screen, colors["BORDER"], (bar_area_x, 0), (bar_area_x, HEIGHT), 2)

    status = "Paused" if paused else "Sorting" if sorting else "Ready"

    info = [
        f"Algorithm: {algorithm}",
        f"Status: {status}",
        f"Speed: {speed} ms",
        f"Comparisons: {comparisons}",
        f"Swaps/Shifts: {swaps}",
        "",
        "Controls:",
        "SPACE → Start / Pause",
        "R → Regenerate Array",
        "↑ ↓ → Adjust Speed",
        "",
        "B → Bubble Sort",
        "S → Selection Sort",
        "I → Insertion Sort",
        "M → Merge Sort",
        "Q → Quick Sort",
        "",
        "D → Toggle Dark Mode 🌙"
    ]

    for idx, text in enumerate(info):
        label = font.render(text, True, colors["TEXT"])
        screen.blit(label, (10, 15 + idx * 26))

# -------- Bubble Sort --------
def bubble_sort_step():
    global i, j, comparisons, swaps, sorting

    if i < len(array):
        if j < len(array) - i - 1:
            comparisons += 1

            screen.fill(get_colors()["BG"])
            draw_info()
            draw_bars(j, j+1)

            pygame.display.update()
            pygame.time.delay(speed)

            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]
                swaps += 1

            j += 1
        else:
            j = 0
            i += 1
    else:
        sorting = False

# -------- Selection Sort --------
def selection_sort_step():
    global i, j, min_index, comparisons, swaps, sorting

    if i < len(array):

        if j == 0:
            min_index = i
            j = i + 1

        if j < len(array):
            comparisons += 1

            screen.fill(get_colors()["BG"])
            draw_info()
            draw_bars(i, j)

            pygame.display.update()
            pygame.time.delay(speed)

            if array[j] < array[min_index]:
                min_index = j

            j += 1
        else:
            if min_index != i:
                array[i], array[min_index] = array[min_index], array[i]
                swaps += 1

            i += 1
            j = 0
    else:
        sorting = False

# -------- Insertion Sort --------
def insertion_sort_generator(arr):
    global comparisons, swaps

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            comparisons += 1
            yield (j, j+1, i)

            arr[j+1] = arr[j]
            swaps += 1
            yield (j, j+1, i)

            j -= 1

        arr[j+1] = key
        swaps += 1
        yield (j+1, None, i)

def insertion_sort_step():
    global insertion_generator, sorting

    try:
        h = next(insertion_generator)

        screen.fill(get_colors()["BG"])
        draw_info()
        draw_bars(h[0], h[1], key_idx=h[2], sorted_boundary=h[2])

        pygame.display.update()
        pygame.time.delay(speed)

    except StopIteration:
        sorting = False

# -------- Merge Sort --------
def merge_sort_generator(arr, left, right):
    global comparisons, swaps

    if left >= right:
        return

    mid = (left + right) // 2

    yield from merge_sort_generator(arr, left, mid)
    yield from merge_sort_generator(arr, mid + 1, right)

    merged = []
    i = left
    j = mid + 1

    while i <= mid and j <= right:
        comparisons += 1
        yield (i, j, left, right)

        if arr[i] < arr[j]:
            merged.append(arr[i])
            i += 1
        else:
            merged.append(arr[j])
            j += 1

    while i <= mid:
        merged.append(arr[i])
        i += 1

    while j <= right:
        merged.append(arr[j])
        j += 1

    for idx, val in enumerate(merged):
        arr[left + idx] = val
        swaps += 1
        yield (left + idx, None, left, right)

def merge_sort_step():
    global merge_generator, sorting

    try:
        h = next(merge_generator)

        screen.fill(get_colors()["BG"])
        draw_info()
        draw_bars(h[0], h[1], active_range=(h[2], h[3]))

        pygame.display.update()
        pygame.time.delay(speed)

    except StopIteration:
        sorting = False

# -------- Quick Sort --------
def quick_sort_generator(arr, low, high):
    global comparisons, swaps

    if low >= high:
        return

    pivot = arr[high]
    i = low

    for j in range(low, high):
        comparisons += 1
        yield (j, high, high)

        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            swaps += 1
            yield (i, j, high)
            i += 1

    arr[i], arr[high] = arr[high], arr[i]
    swaps += 1
    yield (i, high, high)

    yield from quick_sort_generator(arr, low, i-1)
    yield from quick_sort_generator(arr, i+1, high)

def quick_sort_step():
    global quick_generator, sorting

    try:
        h = next(quick_generator)

        screen.fill(get_colors()["BG"])
        draw_info()
        draw_bars(h[0], h[1], pivot=h[2])

        pygame.display.update()
        pygame.time.delay(speed)

    except StopIteration:
        sorting = False

# -------- Main Loop --------
clock = pygame.time.Clock()

while True:
    clock.tick(60)

    screen.fill(get_colors()["BG"])
    draw_info()
    draw_bars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                if not sorting:
                    sorting = True
                    paused = False
                    i = 0
                    j = 0

                    if algorithm == "Merge":
                        merge_generator = merge_sort_generator(array, 0, len(array)-1)
                    if algorithm == "Quick":
                        quick_generator = quick_sort_generator(array, 0, len(array)-1)
                    if algorithm == "Insertion":
                        insertion_generator = insertion_sort_generator(array)
                else:
                    paused = not paused

            if event.key == pygame.K_r:
                generate_array()

            if event.key == pygame.K_UP:
                speed = max(5, speed - 5)

            if event.key == pygame.K_DOWN:
                speed += 5

            if event.key == pygame.K_b:
                algorithm = "Bubble"
                generate_array()

            if event.key == pygame.K_s:
                algorithm = "Selection"
                generate_array()

            if event.key == pygame.K_i:
                algorithm = "Insertion"
                generate_array()

            if event.key == pygame.K_m:
                algorithm = "Merge"
                generate_array()

            if event.key == pygame.K_q:
                algorithm = "Quick"
                generate_array()

            if event.key == pygame.K_d:
                dark_mode = not dark_mode

    if sorting and not paused:
        if algorithm == "Bubble":
            bubble_sort_step()
        elif algorithm == "Selection":
            selection_sort_step()
        elif algorithm == "Insertion":
            insertion_sort_step()
        elif algorithm == "Merge":
            merge_sort_step()
        elif algorithm == "Quick":
            quick_sort_step()

    pygame.display.update()

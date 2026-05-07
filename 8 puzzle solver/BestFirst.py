import flet as ft
import random
import time
import heapq

def is_solvable(state):
    flat = [n for n in state if n != 0]
    inv = sum(flat[i] > flat[j] for i in range(len(flat)) for j in range(i+1, len(flat)))
    return inv % 2 == 0

def generate_solvable():
    while True:
        s = list(range(9))
        random.shuffle(s)
        if is_solvable(s):
            return tuple(s)

class PuzzleState:
    def __init__(self, board, parent=None, move="", depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.h = 0

    def __lt__(self, other):
        return self.h < other.h  # Greedy Best First

    def neighbors(self):
        res = []
        idx = self.board.index(0)
        r, c = divmod(idx, 3)

        moves = {
            "Up": (-1,0),
            "Down": (1,0),
            "Left": (0,-1),
            "Right": (0,1)
        }

        for name, (dr, dc) in moves.items():
            nr, nc = r+dr, c+dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                ni = nr*3 + nc
                b = list(self.board)
                b[idx], b[ni] = b[ni], b[idx]
                res.append(PuzzleState(tuple(b), self, name, self.depth+1))
        return res

def manhattan(board, goal):
    dist = 0
    for i in range(1, 9):
        curr = board.index(i)
        goal_pos = goal.index(i)
        dist += abs(curr//3 - goal_pos//3) + abs(curr%3 - goal_pos%3)
    return dist

def best_first(start, goal):
    pq = []
    start_node = PuzzleState(start)
    start_node.h = manhattan(start, goal)

    heapq.heappush(pq, start_node)

    visited = set()
    visited_states = []

    while pq:
        curr = heapq.heappop(pq)
        visited_states.append(curr.board)

        if curr.board == goal:
            return curr, visited_states

        visited.add(curr.board)

        for n in curr.neighbors():
            if n.board not in visited:
                n.h = manhattan(n.board, goal)
                heapq.heappush(pq, n)

    return None, visited_states

def main(page: ft.Page):
    page.title = "8-Puzzle Best First Search"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 700
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    board = list(generate_solvable())
    goal = (1,2,3,4,5,6,7,8,0)

    grid = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    result = ft.Text(weight="bold", color="white")
    
    visited_logs = ft.Text(size=11,color="white")
    solution_path = ft.Text(size=11,color="white")

    def draw():
        grid.controls.clear()
        for i in range(0, 9, 3):
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for j in range(3):
                val = board[i+j]
                row.controls.append(
                    ft.Container(
                        content=ft.Text(
                            str(val) if val != 0 else "", 
                            size=24, 
                            weight="bold", 
                            color="white" if val != 0 else "grey"
                        ),
                        width=70,
                        height=70,
                        alignment=ft.alignment.center,
                        bgcolor="blue" if val != 0 else "grey",
                        border_radius=8,
                        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                    )
                )
            grid.controls.append(row)
        page.update()

    def randomize(e):
        nonlocal board
        board = list(generate_solvable())
        draw()
        result.value = "New State Generated"
        visited_logs.value = ""
        solution_path.value = ""
        page.update()

    def solve(e):
        nonlocal board
        start = tuple(board)

        t0 = time.time()
        goal_node, visited_states = best_first(start, goal)
        t1 = time.time()

        if goal_node:
            path = []
            moves = []
            curr = goal_node

            while curr:
                path.append(curr.board)
                moves.append(curr.move)
                curr = curr.parent

            path.reverse()
            moves.reverse()

            for state in path:
                for i in range(9):
                    board[i] = state[i]
                draw()
                time.sleep(0.15)

            visited_logs.value = "\n".join(str(v) for v in visited_states)
            solution_path.value = "\n".join(str(p) for p in path)

            result.value = f"Steps: {len(path)-1} | Nodes: {len(visited_states)} | Time: {t1-t0:.2f}s"

        else:
            result.value = "No solution found"

        page.update()

    page.add(
        ft.Text("8-Puzzle Best First Search", size=32, weight="bold"),
        grid,
        ft.Row(
            [
                ft.ElevatedButton("Shuffle", on_click=randomize,bgcolor="green",color= "white"),
                ft.ElevatedButton("Solve", on_click=solve, bgcolor="green", color="white"),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        result,
        ft.Divider(height=20),

        ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Visited States", weight="bold", color="white"),
                        visited_logs
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=10,
                    border=ft.border.all(1, "grey"),
                    border_radius=10,
                    expand=True,
                    height=300,
                    bgcolor="black"
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Solution Path", weight="bold", color="white"),
                        solution_path
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=10,
                    border=ft.border.all(1, "grey"),
                    border_radius=10,
                    expand=True,
                    height=300,
                    bgcolor="black"
                ),
            ],
            spacing=20
        )
    )

    draw()

ft.app(target=main)

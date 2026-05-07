import flet as ft
import random
import time

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
    def __init__(self, board, parent=None, depth=0):
        self.board = board
        self.parent = parent
        self.depth = depth

    def neighbors(self):
        res = []
        idx = self.board.index(0)
        r, c = divmod(idx, 3)

        moves = [(-1,0),(1,0),(0,-1),(0,1)]
        for dr, dc in moves:
            nr, nc = r+dr, c+dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                ni = nr*3 + nc
                b = list(self.board)
                b[idx], b[ni] = b[ni], b[idx]
                res.append(PuzzleState(tuple(b), self, self.depth + 1))
        return res

def solve_dfs(start, goal, limit=30):
    stack = [PuzzleState(start)]
    visited = {start: 0}
    visited_states = []

    while stack:
        curr = stack.pop()
        visited_states.append(curr.board)

        if curr.board == goal:
            return curr, visited_states

        if curr.depth < limit:
            for n in curr.neighbors():
                if n.board not in visited or visited[n.board] > n.depth:
                    visited[n.board] = n.depth
                    stack.append(n)

    return None, visited_states

def main(page: ft.Page):
    page.title = "8 Puzzle DFS Solver"
    page.theme_mode = ft.ThemeMode.DARK
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
        goal_node, visited_states = solve_dfs(start, goal, limit=40)
        t1 = time.time()

        if goal_node:
            path = []
            curr = goal_node
            while curr:
                path.append(curr.board)
                curr = curr.parent
            path.reverse()

            for state in path:
                for i in range(9):
                    board[i] = state[i]
                draw()
                time.sleep(0.15)

            visited_logs.value = "\n".join(str(v) for v in visited_states[:20])
            solution_path.value = "\n".join(str(p) for p in path)

            result.value = f"DFS | Steps: {len(path)-1} | Nodes: {len(visited_states)} | Time: {t1-t0:.2f}s"
        else:
            result.value = "No solution (Depth limit reached)"

        page.update()

    page.add(
        ft.Text("8-Puzzle DFS Solver", size=32, weight="bold"),
        grid,
        ft.Row(
            [
                ft.ElevatedButton("Shuffle", on_click=randomize,bgcolor="green",color="white"),
                ft.ElevatedButton("Solve ", on_click=solve, bgcolor="green", color="white"),
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
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

    draw()

ft.app(target=main)
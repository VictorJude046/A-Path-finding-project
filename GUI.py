import tkinter as tk
import heapq
import random

# Constants
GRID_SIZE = 50  # Size of each cell in the grid
CANVAS_WIDTH, CANVAS_HEIGHT = 1200, 700


class FieldObject:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x, self.y = x, y

        # Randomize size and shape
        self.width = random.randint(20, GRID_SIZE)  # Width of the object
        self.height = random.randint(20, GRID_SIZE)  # Height of the object
        self.shape = random.choice(["oval", "rectangle", "triangle"])  # Random shape
        self.color = random.choice(["blue", "green", "yellow", "red", "purple"])  # Random color

        # Draw the shape based on type
        if self.shape == "oval":
            self.object_id = self.canvas.create_oval(
                x * GRID_SIZE, y * GRID_SIZE,
                x * GRID_SIZE + self.width, y * GRID_SIZE + self.height,
                fill=self.color, tags="object"
            )
        elif self.shape == "rectangle":
            self.object_id = self.canvas.create_rectangle(
                x * GRID_SIZE, y * GRID_SIZE,
                x * GRID_SIZE + self.width, y * GRID_SIZE + self.height,
                fill=self.color, tags="object"
            )
        elif self.shape == "triangle":
            self.object_id = self.canvas.create_polygon(
                x * GRID_SIZE, y * GRID_SIZE + self.height,  # Bottom-left
                x * GRID_SIZE + self.width, y * GRID_SIZE + self.height,  # Bottom-right
                x * GRID_SIZE + self.width // 2, y * GRID_SIZE,  # Top
                fill=self.color, tags="object"
            )

    def move_to(self, x, y):
        self.canvas.coords(
            self.object_id,
            x * GRID_SIZE, y * GRID_SIZE,
            (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE
        )
        self.x, self.y = x, y


class Robot:
    def __init__(self, canvas, x, y, color="red"):
        self.canvas = canvas
        self.color = color
        self.x, self.y = x, y
        self.object_id = self.canvas.create_rectangle(
            x * GRID_SIZE, y * GRID_SIZE,
            (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
            fill=color, tags="robot"
        )

    def move_to(self, x, y):
        self.canvas.coords(
            self.object_id,
            x * GRID_SIZE, y * GRID_SIZE,
            (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE
        )
        self.x, self.y = x, y


class ObjectFieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Object Field with A* Pathfinding")

        # Set up canvas and grid
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack()

        self.objects = []
        self.selected_object = None

        # Create a frame for the buttons at the bottom
        self.button_frame = tk.Frame(root, bg="gray")
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        self.place_robot_button = tk.Button(self.button_frame, text="Spawn Robot", command=self.enable_robot_placement)
        self.place_robot_button.pack(side="left", padx=10)

        self.set_destination_button = tk.Button(self.button_frame, text="Pick Destination", command=self.enable_destination_setting)
        self.set_destination_button.pack(side="left", padx=10)

        self.add_object_button = tk.Button(self.button_frame, text="Add Object", command=self.add_object)
        self.add_object_button.pack(side="left", padx=10)

        self.show_path_button = tk.Button(self.button_frame, text="Path", command=self.calculate_and_show_path)
        self.show_path_button.pack(side="left", padx=10)

        # Create a logical grid
        self.rows = CANVAS_HEIGHT // GRID_SIZE
        self.cols = CANVAS_WIDTH // GRID_SIZE
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Initialize robot, destination, and objects
        self.robot = None
        self.destination = None
        self.path = None
        self.placing_robot = False
        self.setting_destination = False

        # Bind click events
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.drag_object)
        self.canvas.bind("<ButtonRelease-1>", self.release_object)
        self.canvas.bind("<Button-3>", self.add_obstacle)

    def enable_robot_placement(self):
        self.placing_robot = True
        self.setting_destination = False

    def enable_destination_setting(self):
        self.setting_destination = True
        self.placing_robot = False

    def handle_click(self, event):
        x, y = event.x // GRID_SIZE, event.y // GRID_SIZE

        if self.placing_robot:
            if self.robot is None:
                self.robot = Robot(self.canvas, x, y)
            else:
                self.robot.move_to(x, y)
            self.placing_robot = False
            return

        if self.setting_destination:
            if self.robot and (x, y) != (self.robot.x, self.robot.y):
                self.destination = (x, y)
                self.draw_destination()
            self.setting_destination = False
            return

    def drag_object(self, event):
        if self.selected_object:
            x, y = event.x // GRID_SIZE, event.y // GRID_SIZE
            if 0 <= x < self.cols and 0 <= y < self.rows:
                self.selected_object.move_to(x, y)

    def release_object(self, event):
        self.selected_object = None

    def add_object(self):
        x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
        while any((x == obj.x and y == obj.y) for obj in self.objects):
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)

        new_object = FieldObject(self.canvas, x, y)
        self.objects.append(new_object)
        self.canvas.itemconfig(new_object.object_id, tags=("object",))
        self.grid[y][x] = 1

    def add_obstacle(self, event):
        x, y = event.x // GRID_SIZE, event.y // GRID_SIZE
        if self.grid[y][x] == 0:
            self.grid[y][x] = 1
            self.canvas.create_rectangle(
                x * GRID_SIZE, y * GRID_SIZE,
                (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                fill="gray", tags="obstacle"
            )

    def draw_destination(self):
        if self.destination:
            x, y = self.destination
            self.canvas.create_rectangle(
                x * GRID_SIZE, y * GRID_SIZE,
                (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                fill="green", tags="destination"
            )

    def calculate_and_show_path(self):
        if not self.robot or not self.destination:
            return
        start = (self.robot.x, self.robot.y)
        goal = self.destination
        self.path = self.a_star(start, goal)
        self.show_path()

    def show_path(self):
        if self.path:
            for (x, y) in self.path:
                self.canvas.create_rectangle(
                    x * GRID_SIZE + GRID_SIZE // 4, y * GRID_SIZE + GRID_SIZE // 4,
                    (x + 1) * GRID_SIZE - GRID_SIZE // 4, (y + 1) * GRID_SIZE - GRID_SIZE // 4,
                    fill="lightblue", tags="path"
                )
            self.move_robot_along_path()

    def move_robot_along_path(self):
        """Move the robot along the calculated path with animation."""
        if self.path:
            for (x, y) in self.path:
                self.robot.move_to(x, y)
                self.root.update()
                self.root.after(200)  # Pause for animation effect

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            x, y = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < self.cols and 0 <= neighbor[1] < self.rows:
                    if self.grid[neighbor[1]][neighbor[0]] == 1:
                        continue

                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

            # Visualize explored nodes
            if current != start and current != goal:
                self.canvas.create_rectangle(
                    x * GRID_SIZE + GRID_SIZE // 4, y * GRID_SIZE + GRID_SIZE // 4,
                    (x + 1) * GRID_SIZE - GRID_SIZE // 4, (y + 1) * GRID_SIZE - GRID_SIZE // 4,
                    fill="yellow", tags="explored"
                )
                self.root.update()

        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path


# Run the app
root = tk.Tk()
root.geometry("1200x1200")
app = ObjectFieldApp(root)
root.mainloop()

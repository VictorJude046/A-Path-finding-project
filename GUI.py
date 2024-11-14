import tkinter as tk
import heapq
import random

# Constants
GRID_SIZE = 20  # Size of each cell in the grid
CANVAS_WIDTH, CANVAS_HEIGHT = 500, 400

class FieldObject:
    def __init__(self, canvas, x, y, color="blue"):
        self.canvas = canvas
        self.color = color
        self.x, self.y = x, y
        self.object_id = self.canvas.create_oval(
            x * GRID_SIZE, y * GRID_SIZE,
            (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
            fill=color, tags="object"
        )

    def move_to(self, x, y):
        # Move the object to a new position
        self.canvas.coords(
            self.object_id,
            x * GRID_SIZE, y * GRID_SIZE,
            (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE
        )
        self.x, self.y = x, y  # Update grid position


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
        # Move the robot to a new position
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

        # Add buttons
        self.place_robot_button = tk.Button(root, text="Place Robot", command=self.enable_robot_placement)
        self.place_robot_button.pack()
        self.set_destination_button = tk.Button(root, text="Set Destination", command=self.enable_destination_setting)
        self.set_destination_button.pack()
        self.add_object_button = tk.Button(root, text="Add Object", command=self.add_object)
        self.add_object_button.pack()
        self.show_path_button = tk.Button(root, text="Show Path", command=self.show_path)
        self.show_path_button.pack()

        # Create a logical grid (invisible)
        self.rows = CANVAS_HEIGHT // GRID_SIZE
        self.cols = CANVAS_WIDTH // GRID_SIZE
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # 0 = empty, 1 = obstacle

        # Initialize robot, destination, and objects
        self.robot = None
        self.destination = None
        self.path = None
        self.objects = []
        self.placing_robot = False
        self.setting_destination = False
        self.selected_object = None

        # Bind click events
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Button-3>", self.add_obstacle)
        self.canvas.bind("<B1-Motion>", self.move_object)

    def enable_robot_placement(self):
        # Enable robot placement mode
        self.placing_robot = True
        self.setting_destination = False

    def enable_destination_setting(self):
        self.setting_destination = True
        self.placing_robot = False

    def add_object(self):
        # Add an object at a random, non-overlapping position
        x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
        
        # Ensure no overlap with existing objects, robot, or destination
        while any((x == obj.x and y == obj.y) for obj in self.objects) or \
              (self.robot and (x == self.robot.x and y == self.robot.y)) or \
              (self.destination and (x, y) == self.destination):
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
        
        new_object = FieldObject(self.canvas, x, y)
        self.objects.append(new_object)

    def handle_click(self, event):
        x, y = event.x // GRID_SIZE, event.y // GRID_SIZE

        # Place robot if in placement mode
        if self.placing_robot:
            if self.robot is None:
                self.robot = Robot(self.canvas, x, y)
            else:
                self.robot.move_to(x, y)
            self.placing_robot = False
            return

        # Set destination if in destination setting mode
        if self.setting_destination:
            if (x, y) != (self.robot.x, self.robot.y):
                self.destination = (x, y)
                self.draw_destination()  # Draw destination as a green square
                self.calculate_path()
            self.setting_destination = False
            return

        # Select an object for movement if clicked
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if clicked_item and self.canvas.gettags(clicked_item) == ("object",):
            for obj in self.objects:
                if obj.object_id == clicked_item[0]:
                    self.selected_object = obj
                    break

    def move_object(self, event):
        if self.selected_object:
            x, y = event.x // GRID_SIZE, event.y // GRID_SIZE
            self.selected_object.move_to(x, y)

    def add_obstacle(self, event):
        x, y = event.x // GRID_SIZE, event.y // GRID_SIZE
        if self.grid[y][x] == 0 and (self.robot is None or (x, y) != (self.robot.x, self.robot.y)):
            self.grid[y][x] = 1  # Mark obstacle in the logical grid
            # Draw obstacle directly as a black square
            self.canvas.create_rectangle(
                x * GRID_SIZE, y * GRID_SIZE,
                (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                fill="black", tags="obstacle"
            )

    def draw_destination(self):
        # Draw the destination as a green square
        if self.destination:
            x, y = self.destination
            self.canvas.create_rectangle(
                x * GRID_SIZE, y * GRID_SIZE,
                (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                fill="green", tags="destination"
            )

    def calculate_path(self):
        # Calculate the path using A* algorithm, avoiding obstacles and objects
        if not self.destination or not self.robot:
            return

        start = (self.robot.x, self.robot.y)
        goal = self.destination
        self.path = self.a_star(start, goal)

    def show_path(self):
        if self.path:
            # Draw path as light blue squares on the canvas
            for (x, y) in self.path:
                self.canvas.create_rectangle(
                    x * GRID_SIZE, y * GRID_SIZE,
                    (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                    fill="lightblue", tags="path"
                )
            # Move the robot along the path
            for (x, y) in self.path:
                self.robot.move_to(x, y)
                self.root.update()

    def a_star(self, start, goal):
        # A* pathfinding algorithm
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
                    # Check if cell is blocked by obstacle or object
                    if self.grid[neighbor[1]][neighbor[0]] == 1 or \
                       any(obj.x == neighbor[0] and obj.y == neighbor[1] for obj in self.objects):
                        continue

                    tentative_g_score = g_score[current] + 1

                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                        if neighbor not in [i[1] for i in open_set]:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def heuristic(self, a, b):
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path


# Run the app
root = tk.Tk()
app = ObjectFieldApp(root)
root.mainloop()

import tkinter as tk
from typing import Dict, List, Any

class Visualizer:
    def __init__(self, graph: Any, turns: List[Dict[str, str]]):
        self.graph = graph
        self.turns = turns
        self.turn_index = 0
        self.radius = 28  # Slightly smaller radius to open up space between nodes

        # Map connections for quick capacity lookup
        self.link_caps = {}
        for c in self.graph.connections:
            key = tuple(sorted((c.from_, c.to)))
            self.link_caps[key] = int(getattr(c, 'max_link_capacity', 1))

        self.root = tk.Tk()
        self.root.title("Fly-in Mission Control")
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_w*0.95)}x{int(screen_h*0.85)}")
        
        self.canvas = tk.Canvas(self.root, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        nav = tk.Frame(self.root, bg="#222222")
        nav.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(nav, text=" ◀ PREV ", command=self.prev_turn, bg="#444", fg="white").pack(side=tk.LEFT, padx=20, pady=10)
        self.lbl = tk.Label(nav, text="", bg="#222222", fg="white", font=("Courier", 14, "bold"))
        self.lbl.pack(side=tk.LEFT, expand=True)
        tk.Button(nav, text=" NEXT ▶ ", command=self.next_turn, bg="#444", fg="white").pack(side=tk.RIGHT, padx=20, pady=10)

        self.root.update()
        self.render()
        self.root.mainloop()

    def get_pos(self, x: int, y: int) -> tuple:
        pad_x = 120  # Added more horizontal breathing room
        pad_y = 100
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        zs = list(self.graph.zones.values())
        min_x, max_x = min(z.x for z in zs), max(z.x for z in zs)
        min_y, max_y = min(z.y for z in zs), max(z.y for z in zs)

        # Map to screen pixels with aggressive scaling
        nx = pad_x + ((x - min_x) / (max_x - min_x or 1)) * (w - 2 * pad_x)
        ny = pad_y + ((y - min_y) / (max_y - min_y or 1)) * (h - 2 * pad_y)
        return nx, ny

    def render(self):
        self.canvas.delete("all")
        curr = self.turns[self.turn_index]
        self.lbl.config(text=f"TURN: {self.turn_index} / {len(self.turns)-1}")

        # 1. Tally Current Occupancy
        zone_counts = {z.name: 0 for z in self.graph.zones.values()}
        conn_counts = {k: 0 for k in self.link_caps.keys()}

        for d_id, pos in curr.items():
            if "-" in pos:
                z1, z2 = pos.split("-")
                key = tuple(sorted((z1, z2)))
                if key in conn_counts:
                    conn_counts[key] += 1
            else:
                if pos in zone_counts:
                    zone_counts[pos] += 1

        # 2. Draw Connections & Transit Data
        for c in self.graph.connections:
            z1, z2 = self.graph.get_zone(c.from_), self.graph.get_zone(c.to)
            x1, y1 = self.get_pos(z1.x, z1.y)
            x2, y2 = self.get_pos(z2.x, z2.y)
            
            # Base connection line
            self.canvas.create_line(x1, y1, x2, y2, fill="#333333", width=2)
            
            # Transit Visualization
            key = tuple(sorted((c.from_, c.to)))
            in_transit = conn_counts.get(key, 0)
            if in_transit > 0:
                max_cap = self.link_caps[key]
                
                # FIX: If nodes are horizontally adjacent and close, nudge transit indicators upward
                # to prevent them from getting swallowed by the hub circle layers
                if abs(z1.x - z2.x) <= 1 and y1 == y2:
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2 - 35
                else:
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                
                # Orange Transit Drone Indicator
                self.canvas.create_oval(mid_x-10, mid_y-10, mid_x+10, mid_y+10, fill="orange", outline="white", width=1.5)
                self.canvas.create_text(mid_x, mid_y, text="✈", fill="black", font=("Arial", 10))
                
                # Transit Capacity Fraction
                color = "#ff4444" if in_transit >= max_cap else "#00ff00"
                self.canvas.create_text(mid_x, mid_y - 18, text=f"{in_transit}/{max_cap}", fill=color, font=("Consolas", 9, "bold"))

        # 3. Draw Hubs & Zone Data
        for i, z in enumerate(self.graph.zones.values()):
            cx, cy = self.get_pos(z.x, z.y)
            color = z.color if z.color not in ["none", "rainbow"] else "#444444"
            
            # Draw Hub Outline
            outline = "white" if z.kind in ["start_hub", "end_hub"] else "gray"
            self.canvas.create_oval(cx-self.radius, cy-self.radius, cx+self.radius, cy+self.radius, 
                                    fill=color, outline=outline, width=1.5)
            
            # FIX: Shrunk text size to 7pt and staggered label offsets aggressively 
            # to prevent neighbor label overlapping (e.g., CONV_RESTRICTED blocks)
            if i % 3 == 0:
                y_off = - (self.radius + 15)
            elif i % 3 == 1:
                y_off = (self.radius + 15)
            else:
                y_off = (self.radius + 28)  # Third tier offset for extreme tight spots
                
            self.canvas.create_text(cx, cy + y_off, text=z.name.upper(), fill="#b45309" if "trap" in z.name else "#aaaaaa", font=("Arial", 7, "bold"))

            # Drone Swarm Visualization inside Hub
            occupants = zone_counts[z.name]
            if occupants > 0:
                max_cap = int(getattr(z, 'max_drones', 1))
                if z.kind in ["start_hub", "end_hub"]:
                     max_cap = self.graph.nb_drones
                
                # Yellow Stationed Drone Indicator
                self.canvas.create_oval(cx-12, cy-12, cx+12, cy+12, fill="#fbbf24", outline="black", width=1.5)
                self.canvas.create_text(cx, cy, text="✈", fill="black", font=("Arial", 11))
                
                # Capacity Fraction (Positioned right at the top rim of the circle)
                fraction_color = "#ff4444" if occupants >= max_cap else "#00ff00"
                self.canvas.create_text(cx, cy - self.radius - 5, text=f"{occupants}/{max_cap}", 
                                        fill=fraction_color, font=("Consolas", 10, "bold"))

    def next_turn(self):
        if self.turn_index < len(self.turns) - 1:
            self.turn_index += 1
            self.render()

    def prev_turn(self):
        if self.turn_index > 0:
            self.turn_index -= 1
            self.render()
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
import sys
from parser import Map_parser
from Graph import Graph
from path_finder import Pathfinder

# 1. Parse and run algorithm
map_file = sys.argv[1] if len(sys.argv) > 1 else "maps/easy/03_basic_capacity.txt"
parsed = Map_parser(map_file)
data = parsed.parser()
graph = Graph(data)
pf = Pathfinder(graph)
pf.loop()

routes = graph.routes
if not routes:
    print("No routes found!")
    sys.exit()

max_time = max(route[-1][1] for route in routes)

# 2. Setup Plot
fig, ax = plt.subplots(figsize=(18, 14))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
ax.set_title(f"Drone Routing Visualization - {data.nb_drones} Drones\n(Auto-playing... Use Left/Right Arrows to take manual control)", color='white', fontsize=16)
ax.set_aspect('equal')
ax.axis('off')

SCALE = 3.0

# 3. Draw Connections
for conn in data.connections:
    x_values = [conn.zone1.x * SCALE, conn.zone2.x * SCALE]
    y_values = [conn.zone1.y * SCALE, conn.zone2.y * SCALE]
    ax.plot(x_values, y_values, color='white', zorder=1, linewidth=2, alpha=0.3)

# Zone base info
zone_list = list(data.zones.values())
zone_xs = [z.x * SCALE for z in zone_list]
zone_ys = [z.y * SCALE for z in zone_list]

def get_zone_color(z):
    if z.color:
        if mcolors.is_color_like(z.color):
            return z.color
        if z.color.lower() == 'rainbow':
            return 'violet'
    if z.is_start: return 'green'
    if z.is_end: return 'red'
    if z.zone_type.value == "blocked": return 'gray'
    if z.zone_type.value == "restricted": return 'blue'
    return 'lightblue'

zone_colors = [get_zone_color(z) for z in zone_list]

zone_scatter = ax.scatter(zone_xs, zone_ys, c=zone_colors, s=150, zorder=2, edgecolors='white')

for z in zone_list:
    ax.text(z.x * SCALE, (z.y * SCALE) - 0.4, z.name, color='white', fontsize=8, ha='center', va='top', zorder=4)

drone_scatter = ax.scatter([], [], c='yellow', s=250, zorder=5, edgecolors='orange')
drone_texts = [ax.text(0, 0, f"{i+1}", ha='center', va='center', color='black', fontsize=9, fontweight='bold', zorder=6) for i in range(len(routes))]

turn_text = ax.text(0.02, 0.98, "Turn: 0", transform=ax.transAxes, color='white', fontsize=16, fontweight='bold', va='top')

current_turn = 0
is_animating = True

def update(current_time):
    drone_positions = []
    zone_drone_counts = {z.name: 0 for z in zone_list}

    for i, route in enumerate(routes):
        if current_time <= route[0][1]:
            pos_x, pos_y = route[0][0].x * SCALE, route[0][0].y * SCALE
            zone_drone_counts[route[0][0].name] += 1
        elif current_time >= route[-1][1]:
            pos_x, pos_y = route[-1][0].x * SCALE, route[-1][0].y * SCALE
            zone_drone_counts[route[-1][0].name] += 1
        else:
            for k in range(len(route) - 1):
                z1, t1 = route[k]
                z2, t2 = route[k+1]
                if t1 <= current_time < t2:
                    if z1 == z2:
                        pos_x, pos_y = z1.x * SCALE, z1.y * SCALE
                        zone_drone_counts[z1.name] += 1
                    else:
                        progress = (current_time - t1) / (t2 - t1)
                        pos_x = (z1.x + (z2.x - z1.x) * progress) * SCALE
                        pos_y = (z1.y + (z2.y - z1.y) * progress) * SCALE
                    break

        drone_positions.append([pos_x, pos_y])
        drone_texts[i].set_position((pos_x, pos_y))

    if drone_positions:
        drone_scatter.set_offsets(drone_positions)

    sizes = [150 + (zone_drone_counts[z.name] * 300) for z in zone_list]
    zone_scatter.set_sizes(sizes)

    turn_text.set_text(f"Turn: {current_time:.1f}")

    if not is_animating:
        fig.canvas.draw_idle()

def anim_update(frame):
    global current_turn
    current_turn = frame
    update(current_turn)
    if current_turn == max_time:
        ax.set_title(f"Drone Routing Visualization - {data.nb_drones} Drones\n(Finished. Use Left/Right Arrows to debug)", color='white', fontsize=16)

def on_key(event):
    global current_turn, is_animating

    if is_animating and ani and ani.event_source:
        ani.event_source.stop()
        is_animating = False
        ax.set_title(f"Drone Routing Visualization - {data.nb_drones} Drones\n(Manual Mode. Use Left/Right Arrows)", color='white', fontsize=16)

    if event.key == 'right':
        current_turn = min(current_turn + 1.0, max_time)
        update(current_turn)
    elif event.key == 'left':
        current_turn = max(current_turn - 1.0, 0)
        update(current_turn)

fig.canvas.mpl_connect('key_press_event', on_key)

ani = animation.FuncAnimation(fig, anim_update, frames=int(max_time) + 1, interval=800, repeat=False)

plt.tight_layout()
plt.show()
from parser import Map_parser
from Errors import MapError
from Graph import Graph
from path_finder import Pathfinder
import sys

if __name__ == "__main__":
    try:
        # Determine the map file to use
        map_file = sys.argv[1] if len(sys.argv) > 1 else "/home/zues/Desktop/fly-in/maps/easy/03_basic_capacity.txt"
        
        # parse the Map
        parsed = Map_parser(map_file)
        # get the parsed data
        data = parsed.parser()
        graph = Graph(data)
        pathfinder = Pathfinder(graph)
        pathfinder.loop()
        
        # Build the visualization
        max_turn = 0
        turns_output = {}

        for drone_idx, path_with_times in enumerate(graph.routes):
            drone_id = drone_idx + 1  # D1, D2, ...
            
            for k in range(1, len(path_with_times)):
                prev_z, prev_t = path_with_times[k-1]
                curr_z, curr_t = path_with_times[k]
                
                # If waiting, drone doesn't move, so omit it
                if prev_z == curr_z:
                    continue
                
                # In flight
                for t in range(prev_t + 1, curr_t):
                    if t not in turns_output:
                        turns_output[t] = []
                    turns_output[t].append(f"D{drone_id}-{prev_z.name}-{curr_z.name}")
                
                # Arrives
                if curr_t not in turns_output:
                    turns_output[curr_t] = []
                turns_output[curr_t].append(f"D{drone_id}-{curr_z.name}")
                
                if curr_t > max_turn:
                    max_turn = curr_t
                    
        # Print step-by-step
        for t in range(1, max_turn + 1):
            if t in turns_output and turns_output[t]:
                print(" ".join(turns_output[t]))

    except MapError as e:
        print(e)
    
import itertools

import pandas as pd
import numpy as np

import random


#liest Daten aus Datei
def get_data(n):
    df = pd.read_csv(f'res/wenigerkrumm{n}.txt', header=None, sep=" ")
    df.columns = ("x", "y")
    return [(x, y) for x, y in df.values]

TO_DEG = 360 / (2 * np.pi)


#Berechnet Winkel zweier Vektoren
def get_angle_of_vectors(current_dir, next_dir):
    if np.linalg.norm(current_dir) == 0:
        return 0
    else:
        return np.arccos(np.dot(current_dir, next_dir) / (np.linalg.norm(current_dir) * np.linalg.norm(next_dir)))


#Berechnet Distanz zweier Punkte
def get_distance_to_node(next_node, current_node):
    return np.sqrt((next_node[0] - current_node[0]) ** 2 + (next_node[1] - current_node[1]) ** 2)


#Bestimmt Folgepunkte ohne Memoization
def get_next_points_old(prev_node, current_node, points):
    choices = []
    current_dir = get_vector_from_points(prev_node, current_node)

    for point in points:


        next_dir = np.array([point[0] - current_node[0], point[1] - current_node[1]])
        angle = get_angle_of_vectors(current_dir, next_dir) * TO_DEG

        if angle <= 90:
            choices.append(point)

    choices.sort(key=lambda x: get_distance_to_node(x, current_node))
    return choices


#Bestimmt Folgepunkte mit Memoization
def get_next_points(prev_node, current_node, points, memoization_table = None):

    choices = []
    current_dir = get_vector_from_points(prev_node, current_node)

    for point in points:

        if (prev_node, current_node, point) in memoization_table:
            angle = memoization_table[(prev_node, current_node, point)][0]
        else:
            next_dir = np.array([point[0] - current_node[0], point[1] - current_node[1]])
            angle = get_angle_of_vectors(current_dir, next_dir) * TO_DEG
            if memoization_table is not None:
                memoization_table[(prev_node, current_node, point)] = (angle, get_distance_to_node(current_node, point))

        if angle <= 90:
            choices.append(point)

    choices.sort(key=lambda x: memoization_table[(prev_node, current_node, x)][1])
    return choices



#Generiert alle Tripel von Puntken
def get_permutations(nodes):

    perms = list(itertools.permutations(nodes, 3))

    last = perms[0][-1]

    idx = 0

    for i, perm in enumerate(perms):
        if perm[0] == last:
            idx = i
            break

    perms = perms[0:idx]

    print(last)

    return perms


#Generiert Vektor aus zwei Punkten
def get_vector_from_points(p1, p2):
    return np.array([p2[0]-p1[0], p2[1]-p1[1]])



#unwichtig
def add_edge_to_graph(G, e1, e2, w):
    G.add_edge(e1, e2, weight=w)


#unwichtig
def get_hyperedges(points):


    perms = list(itertools.permutations(points, 3))
    edges = [(perm[0], perm[2]) for perm in perms if get_angle_of_vectors(get_vector_from_points(perm[0], perm[1]),
                                                                          get_vector_from_points(perm[1], perm[
                                                                              2])) * TO_DEG <= 90]

    for perm in perms:
        if get_angle_of_vectors(get_vector_from_points(perm[0], perm[1]), get_vector_from_points(perm[1], perm[
                                                                              2])) * TO_DEG <= 90:
            print(perm[0], perm[1], perm[2])

    return edges


#Polarkoordinaten nach Kartesisch
def polar_to_cartesian(alpha, r):
    x = np.cos(alpha) * r
    y = np.sin(alpha) * r

    return (x, y)


#Zufälliger Punkt in eienm Kreis
def get_random_point_in_circle(radius = 1):

    alpha = random.uniform(0,2*np.pi)
    r = np.sqrt(random.uniform(0,radius**2))

    return polar_to_cartesian(alpha, r)


#Generiert zufällige Punkt in verschiendene Formen (disk, line, circle)
def get_random_points(n, shape = "circle"):
    if shape == "disk":
        return [get_random_point_in_circle(1) for _ in range(n)]
    if shape == "line":
        return [(x, 0) for x in np.linspace(0, n, n) + np.random.uniform(0.1, 1, size=n)]
    if shape == "circle":
        return [polar_to_cartesian(alpha, 1) for alpha in np.linspace(0,2*np.pi, n, endpoint=True)]
    else:
        print("unknoen shape \”", shape, "\”")
        return False


#Route aus Punkteindizes zu Punkteroute
def idx_to_point_route(route, points):
        proute = [points[x] for x in route]
        return proute


#unwichtig
def flatten(arr):
    flat_list = []
    for sublist in arr:
        for item in sublist:
            flat_list.append(item)
    return flat_list


#berechnet Länge der Route optional mit einem distance_lookup-Table
def get_length_of_route(route, distance_lookup=None):
    total_len = 0


    if distance_lookup is not None:
        for p in range(len(route)-1):
            total_len += distance_lookup[route[p]][route[p+1]]
    else:
        for p in range(len(route) - 1):
            total_len += get_distance_to_node(route[p], route[p+1])


    return total_len


if __name__ == "__main__":
    print(get_random_points(10, shape="line"))


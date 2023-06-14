import numpy as np
from utils import *
from concorde.tsp import TSPSolver
from vis import vis_points

def find_route_1(points: list): #Erste, simpelste Implementierung

    backtracking_list = []

    for start_point in points:

        route = [start_point, start_point]
        points.remove(start_point)
        start_idx = 0

        while True: #Bricht ab, wenn keine Folgepunkte mehr gefunden werden können

            next_points = get_next_points_old(route[-2], route[-1], points)

            if len(next_points) > start_idx: #Es gibt Folgepunkte, die noch nicht ausprobiert wurden
                route.append(next_points[start_idx])
                points.remove(next_points[start_idx])
                backtracking_list.append(start_idx+1)
                start_idx = 0

            elif len(points) == 0: #Alle Punkte wurden verwendet -> Route erfolgreich konstruiert
                return route

            elif len(route) > 2: #Es gibt keine Folgepunkte mehr, obwohl noch Punkte übrig sind -> Backtracking
                points.append(route.pop())
                start_idx = backtracking_list.pop()
            else: break #Es gibt keine Möglichkeit mehr backzutracken -> Algorithmus bricht ab

    return False #


def find_route_2(points: list): #Nutzt Memoization

    backtracking_list = []
    memoization_table = {}

    bts = 0

    for start_point in points:

        route = [start_point, start_point]
        points.remove(start_point)
        start_idx = 0

        while True:

            next_nodes = get_next_points(route[-2], route[-1], points, memoization_table=memoization_table)

            if len(next_nodes) > start_idx:
                route.append(next_nodes[start_idx])
                points.remove(next_nodes[start_idx])
                backtracking_list.append(start_idx+1)
                start_idx = 0

            elif len(points) == 0:
                return route

            elif len(route) > 2:
                points.append(route.pop())
                start_idx = backtracking_list.pop()
                bts += 1

            else:
                while len(route) > 1:
                    points.append(route.pop())
                break


    return False


def find_route_3(points: list): #Implementiert check der minimalen Abbiegewinkel und nimmt beste Lösung aus den ersten 100000 Routen jedes Startpunktes

    #Matrix A wird generiert
    def get_triple_matrix():
        # Matrix creation
        point_list = []

        for point in points:
            predecessor_list = []
            for predecessor in points:
                successor_list = []
                for successor in points:
                    if predecessor == point:
                        successor_list.append(True)
                    elif successor == point:
                        successor_list.append(False)
                    elif predecessor == successor:
                        successor_list.append(False)
                    else:
                        v1 = get_vector_from_points(predecessor, point)
                        v2 = get_vector_from_points(point, successor)

                        angle = get_angle_of_vectors(v1, v2) * TO_DEG

                        successor_list.append(angle <= 90)

                predecessor_list.append(successor_list)
            point_list.append(predecessor_list)

        return point_list

    #Lookup Table für die Distanzen zweier Punkte
    def get_distance_lookup():
        distance_lookup = []
        for i in range(len(points)):
            point_list = []
            for j in range(len(points)):
                point_list.append(get_distance_to_node(points[j], points[i]))
            distance_lookup.append(point_list)

        return distance_lookup

    n = len(points)
    #Da Punkte nicht mehr auf der Punkteliste entfernt werden, um Effizienz zu verbessern wird deren Verfügbarkeit in dieser Liste mit Booleans gespeichert
    points_available = [True for _ in range(n)]

    point_triple_traversable_lookup = get_triple_matrix()


    #Zählen aller Punkte mit minimalem Abbiegewinkel > 90
    counter = 0
    start_point = 0
    for i in range(len(point_triple_traversable_lookup)):
        pairs = point_triple_traversable_lookup[i]
        s = sum([sum(x) for x in pairs])
        if s <= n:
            counter += 1
            start_point = i

    print(counter, "points with minimal angle > 90 deg")
    if counter > 2:
        print("cannot reconstruct route")
        return False

    distance_lookup = get_distance_lookup()

    #Beste Route, die mit allen Startpunkten generiert werden konnte
    best_route_glob = (np.inf, [])

    for start_point in range(len(points)):

        route = [start_point, start_point]
        points_available[start_point] = False
        backtracking_list = []
        start_idx = 0
        best_route = []

        bts = 0 #Zählvariable für das Backtracking, um nach 100000 Backtrackings abzubrechen und nächsten Startpunkt zu wählen

        while True:
            if bts > 100000:
                break

            next_points = []
            for i in range(len(point_triple_traversable_lookup[route[-1]][route[-2]])):
                if point_triple_traversable_lookup[route[-1]][route[-2]][i] == True: next_points.append(i)

            next_points.sort(key=lambda x: distance_lookup[x][route[-1]]) #Sortieren der Punkte nach Distanz für die NN-Heuristik

            for i in range(len(next_points)):
                if i >= start_idx and points_available[next_points[i]] == True: #Wenn noch ein Folgepunkt verfügbar ist, der noch nicht ausprobiert wurde
                    route.append(next_points[i]) #Punkt an Route anfügen
                    points_available[next_points[i]] = False
                    backtracking_list.append(i+1)
                    start_idx = 0
                    if len(route) > len(best_route): best_route = route
                    break
            else:
                if sum(points_available) == 0: #Wenn keine Folgepunkte mehr verfügbar sind
                    route.pop(0)
                    break #Route wurde erfolgreich konstruiert -> nächster Startpunkt
                elif len(route) > 2: #Route noch nicht zusammengesetzt -> Backtracking

                    points_available[route.pop()] = True
                    start_idx = backtracking_list.pop()
                    bts += 1
                else: #Keine backtracking Optionen mehr -> Route kann nicht konstruiert werden
                    print("cannot reconstruct")
                    return False

        #Nach Versuch der Konstruktion der Route; Vor nächstem Startpunkt
        for pointer in range(len(points_available)):
            points_available[pointer] = True #Alle Punkte wieder auf verfügbar setzen

        if len(route) == len(points): #Wenn die Route alle Punkte enthält
            length = get_length_of_route(route, distance_lookup) #Länge errechnen
            print("Start Point:", start_point, "=", points[start_point], "; length =", get_length_of_route(route, distance_lookup))
            if length < best_route_glob[0]:
                best_route_glob = (length, idx_to_point_route(route, points)) #Kürzeste Route speichern

    print("")
    print("")
    print("best route has length", best_route_glob[0], "                     ", best_route_glob[1])
    return best_route_glob[1]


if __name__ == "__main__":
    pass





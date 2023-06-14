import itertools
from scipy.spatial import ConvexHull

from utils import *
import matplotlib.pyplot as plt


#Stellt Punkte mit matplotlib dar; connected verbindet die Punkte; edges stellt Tripel mit Abbiegewinkel <= 90 dar; convex_hull stellt die Konvexe Hülle dar
def vis_points(points, connected=False, edges = False, convex_hull=False):
    # Separate the x and y coordinates into separate lists
    x_coords = [d[0] for d in points]
    y_coords = [d[1] for d in points]

    # Create a scatterplot with the x and y coordinates
    plt.scatter(x_coords, y_coords)
    if connected:
        plt.scatter(x_coords[0], y_coords[0], color="red")

    # Create a line plot with the x and y coordinates
    if connected:
        plt.plot(x_coords, y_coords)

    if edges:
        edges = get_hyperedges(points)
        for edge in edges:
            plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]])

    if convex_hull:
        hull = ConvexHull(points)
        x_hull = [hull.points[vertex][0] for vertex in hull.vertices]
        x_hull.append(x_hull[0])
        y_hull = [hull.points[vertex][1] for vertex in hull.vertices]
        y_hull.append(y_hull[0])

        plt.plot(x_hull, y_hull, 'k-')
        plt.scatter(x_hull, y_hull, color='green')


    plt.axis('equal')
    plt.show()


#stellt nicht fertige route in Menge von Punkten dar
def vis_partial_route(route, points):

    plt.scatter([x[0] for x in points], [x[1] for x in points])
    plt.plot([x[0] for x in route], [x[1] for x in route])
    plt.scatter(route[0][0], route[0][1], color="red")

    plt.axis('equal')
    plt.show()



if __name__ == "__main__":
    pass
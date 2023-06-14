import itertools


from algo import *
from vis import vis_points
from utils import *
import matplotlib.pyplot as plt
from time import time


#öffnet Matplotlib GUI, indem Punktemengen per Mausklick erstellt werden. Nach Schließen des Fensters wird Route berechnet
def create_points():
    fig, ax = plt.subplots()
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    scatter = ax.scatter([], [])

    points = []

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x = event.xdata
            y = event.ydata
            points.append((x, y))
            scatter.set_offsets(points)
            plt.draw()

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    return points


#Startet Algorithmus und visualisiert Ergebnis
def show_sol(points):
    res = find_route_3(points) #Aktuell Algorithmus 3, da das der Beste ist
    if res is False:
        print("Not solvable")
    else:
        vis_points(res, connected=True)

if __name__ == "__main__":

    show_sol(get_data(7)) #Zeile, um Programm zu starten
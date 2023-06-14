from utils import *
from algo import *
from vis import analyse_start_rects

def run(rects):
    start_rects = sorted(get_start_rects(rects), key=lambda x:x[1]) #Alle Startscheiben bekommen und nach dem zweiten
    # Tupelparameter sortieren
    #start_rects = advanced_sorting(get_start_rects(), sort_key= lambda x:x[1]) soll für Aufgabe b verwendet werden
    n = sum(rects.values())-2

    for start_rect in start_rects:

        rects[start_rect] -= 2
        current_cuboid = start_rect + (2,)
        cuboid_list, cuboid = rebuild_cuboid_a(current_cuboid, rects,n)#Algorithmus mit jeder Startscheibe starten

        if not cuboid_list == (False): #Wenn es eine Lösung gibt
            cuboid_list = [start_rect, start_rect] + cuboid_list
            print('rebuilt cuboid!')
            return cuboid_list
        else: #sonst nochmal
            rects[start_rect] += 2
    print("Quader lässt sich nicht zusammensetzen")
    return False


if __name__ == "__main__":
    data = get_data(7) #Laden der Daten
    rects = parse_data(data) #Übersetzen der Scheiben in das korrekte Datenformat

    res = run(rects.copy()) #Algorithmus starten

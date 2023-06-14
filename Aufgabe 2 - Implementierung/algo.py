import time

from utils import *


#Quader mit gegebenem Startquader zusammensetzen
def rebuild_cuboid_a(current_cuboid, remaining_rects, n):
    cuboid_list = []
    current_cuboid = sorted(current_cuboid)

    while True:

        #Folgescheibe aus verbleibenden Scheiben und aktuellem Quader bestimmen
        next_rect = get_next_rect(remaining_rects, current_cuboid)

        #Wenn es eine Folgescheibe gibt
        if next_rect is not None:
            remaining_rects[next_rect] -= 1
            n -= 1
            #Folgescheibe an akutellen Quader anfügen
            current_cuboid = alter_cuboid(current_cuboid, next_rect, 1)
            cuboid_list.append(next_rect)
        else:
            if n == 0: #keine Verbleibenden Scheiben mehr, also wurde der Quader zusammengesetzt
                return cuboid_list, current_cuboid
            else:
                while len(cuboid_list) > 0: #Quader kann nicht zusammengestezt werden und wird wieder auseinandergebaut,
                    # damit remaining_rects wieder in der Ausgangszustand kommt; so können Kopieroperationen vermieden werden
                    last_rect = cuboid_list.pop()
                    current_cuboid = alter_cuboid(current_cuboid, last_rect, -1)
                    remaining_rects[last_rect] += 1
                    n += 1
                return False, False


#Quader mit gegebenem Startquader zusammensetzen; max_additions Scheiben dürfen ergänzt werden
def rebuild_cuboid_b(current_cuboid, remaining_rects, n, max_additions = 0):
    cuboid_list = []
    current_cuboid = sorted(current_cuboid)

    backtracking_list = []
    start_idx = 0
    additions = 0

    while True:

        #Bestimmen der Folgescheibe
        next_rect = get_next_rect(remaining_rects, current_cuboid)

        #Wenn es keine Folgescheibe gibt, oder diese bereits probiert wurde
        if start_idx > 0 or next_rect == None:
            #Wenn noch Scheiben addiert werden dürfen und können
            if additions < max_additions and start_idx < 3:
                new_choices = generate_choices(next_rect, current_cuboid)
                #Wenn die neuen Scheiben auch noch nicht probiert wurden
                if len(new_choices) > start_idx - 1:
                    next_rect = new_choices[start_idx - 1]
                    additions += 1
            else:
                next_rect = None

        #Wenn es eine Folgescheibe gibt
        if next_rect is not None:
            remaining_rects[next_rect] -= 1
            n -= 1
            current_cuboid = alter_cuboid(current_cuboid, next_rect, 1) #Scheibe anfügen
            cuboid_list.append(next_rect)
            backtracking_list.append(start_idx + 1) #Entscheidung für später speicher, um backtracken zu können
            start_idx = 0
        elif n + additions == 0: #Wenn keine Scheiben mehr verbleiben
            return cuboid_list, additions
        elif len(cuboid_list) > 0: #Backtracken
            last_rect = cuboid_list.pop() #Scheibe aus Scheibenliste entfernen
            if remaining_rects[last_rect] < 0: #Prüfen, ob Scheibe generiert war
                additions -= 1
            start_idx = backtracking_list.pop() #Start idx setzen, damit backtracking funktioniert
            current_cuboid = alter_cuboid(current_cuboid, last_rect, -1) #Scheibe wieder vom Quader entfernen
            remaining_rects[last_rect] += 1
            n += 1
        else:
            return False, False
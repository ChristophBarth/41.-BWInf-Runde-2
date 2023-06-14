import itertools
import random

import numpy as np
import pandas as pd
from collections import defaultdict

from numpy import ceil
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import time


#get data
def get_data(n):
    df = pd.read_csv(f'res/kaese{n}.txt', header=None, sep=" ", skiprows=[0])
    df.columns = ["x", "y"]
    return df.values.tolist()


#parse data to defaultdict
def parse_data(data):
    rects = defaultdict(lambda: 0)
    for x, y in data:
        rects[(x, y) if x < y else (y, x)] += 1

    return rects


#parse rects from dict into list
def parse_rects(rects):
    out = []

    for rect, count in rects.items():
        out += [rect for _ in range(count)]

    return out


#cut/combine rects
def alter_cuboid(cuboid, rect, n):
    cuboid = list(cuboid)
    if rect == (cuboid[0], cuboid[1]) or rect == (cuboid[1], cuboid[0]):
        cuboid[2] += n
    elif rect == (cuboid[1], cuboid[2]) or rect == (cuboid[2], cuboid[1]):
        cuboid[0] += n
    elif rect == (cuboid[0], cuboid[2]) or rect == (cuboid[2], cuboid[0]):
        cuboid[1] += n
    else:
        print("bug found:", cuboid, "+", rect)

    return sorted(tuple(cuboid))


#get cuboid faces
def get_cuboid_faces(cuboid):
    return [(rect[1], rect[0]) if rect[1]<rect[0] else rect for rect in list(itertools.combinations(cuboid, 2))]


#get_all_next_rects
def get_next_rects(rects, cuboid):
    out = []
    for rect in get_cuboid_faces(cuboid):
        #rect = (rect[1], rect[0]) if rect[1]<rect[0] else rect
        if rects[rect] >= 1:
            out.append(rect)

    return list(dict.fromkeys(out))


#get_next_face
def get_next_rect(rects, cuboid):

    out = None

    for rect in get_cuboid_faces(cuboid):
        rect = (rect[1], rect[0]) if rect[1]<rect[0] else rect
        if rects[rect] >= 1  and (out == None or rect[0]*rect[1]<out[0]*out[1]):
            out = rect

    return out


#get start rects (unsorted)
def get_start_rects(rects):
    out = []
    for rect, count in rects.items():
        if (count >= 2):
            out.append(rect)

    return out


#generate set of rectangles to rebuild cuboid
def get_sample_data(n=100000, max_start_dim=10000, missing_rects = 0):
    out = []

    start_rect = (random.randint(2,ceil(max_start_dim)), random.randint(2,ceil(max_start_dim)))

    info = {
        "start_rect": start_rect,
        "missing_rects": []
    }

    current_cuboid = start_rect + (2,)

    for _ in range(0,n-2):
        r = random.randint(0,2)
        face = get_cuboid_faces(current_cuboid)[r]
        out.append(face)
        current_cuboid = alter_cuboid(current_cuboid, face, 1)

    for _ in range(missing_rects):
        info['missing_rects'].append(out.pop(random.randrange(len(out))))

    out.append(start_rect)
    out.append(start_rect)

    random.shuffle(out)
    return out, info


#Hilfsmethode für advanced_sorting, um Clusterlisten zu verketten
def concatenate_lists(list):
    list1, list2, list3 = list[0], list[1], list[2]
    out = []
    for i in range(max(len(list1), len(list2), len(list3))):
        if i < len(list1):
            out.append(list1[i])
        if i < len(list2):
            out.append(list2[i])
        if i < len(list3):
            out.append(list3[i])
    return out


#kmeans*key Sortieralgorithmus
def advanced_sorting(start_rects, sort_key = lambda x:1, return_lists=False):
    #Differenz aller Startscheiben bilden
    data = np.array([(b-a) for a, b in start_rects]).reshape(-1,1)

    #KMeans Modell mit 3 Clustern Trainieren
    model = KMeans(n_clusters=3, n_init=10)
    model.fit(data)

    #Punkte den drei Clustern zuordnen
    predicted_labels = model.predict(np.array(data).reshape(-1, 1))

    #Punkte mit den predicted_labels in Cluster sortieren
    out = [[] for i in range(model.n_clusters)]
    for i, label in enumerate(predicted_labels):
        out[label].append(start_rects[i])

    #Sortieren der Cluster
    for i in range(model.n_clusters):
        out[i].sort(key=sort_key)

    if(return_lists):return out
    return concatenate_lists(out) #Ausgabe der verketteten Cluster


#Generiert Scheiben für Aufhabe B
def generate_choices(next_rect, current_cuboid):

    theoretical_choices = get_cuboid_faces(current_cuboid) #Alle Seiten des Quaders werden zunächst betrachtet
    out = []

    #Da die generierten Scheiben kleiner sein müssen, als das bereits generierte, wird zunächst die kleinste Scheibe bestimmt
    if next_rect is not None:
        min_area = next_rect[0]*next_rect[1]
    else: min_area = 0

    #Prüfen, ob Quaderseite kleiner ist als die kleinste bereits bestehende Folgescheibe
    for rect in theoretical_choices:
        if min_area == 0 or rect[0]*rect[1] < min_area:
            out.append(rect)

    return out



if __name__ == "__main__":
    pass


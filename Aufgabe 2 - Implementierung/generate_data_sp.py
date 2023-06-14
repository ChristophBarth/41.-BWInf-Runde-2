import time
from algo import rebuild_cuboid_a
from utils import get_start_rects, get_data, parse_data, get_sample_data, advanced_sorting
import pandas as pd
from tqdm.auto import tqdm


def run(rects):
    start_rects = get_start_rects(rects)

    n = sum(rects.values()) - 2

    for start_rect in start_rects:

        rects[start_rect] -= 2
        current_cuboid = start_rect + (2,)
        out, cuboid = rebuild_cuboid_a(current_cuboid, rects, n)

        if out is not False:
            out = [start_rect, start_rect] + out
            return cuboid
        else:
            rects[start_rect] += 2
    print("Cannot rebuild cuboid")
    return

def get_stats(rects, metrics=[], start_rects_sorting_func = False):

    return_runtime = 'runtime' in metrics
    return_start_rect = 'start_rect' in metrics
    return_start_rect_count = 'start_rect_count' in metrics
    return_start_rect_position = 'start_rect_position' in metrics
    return_start_rects = 'start_rects' in metrics
    return_cuboid = 'return_cuboid' in metrics
    return_solution = 'return_solution' in metrics
    return_sorting_time = 'sorting_time' in metrics

    def get_output(success):
        print(success)
        out = {}
        if return_start_rect_position:
            out['start_rect_position'] = start_rects.index(start_rect) if success else -1
        if return_runtime:
            out['runtime'] = time.time() - start_time
        if return_start_rect:
            out['start_rect'] = start_rect if success else (-1,-1)
        if return_start_rect_count:
            out['start_rect_count'] = len(start_rects)
        if return_start_rects:
            out['start_rects'] = start_rects
        if return_cuboid:
            out['cuboid'] = current_cuboid
        if return_solution:
            out['solution'] = cuboid_list
        if return_sorting_time:
            out['sorting_time'] = sorting_time

        return out

    start_rects = get_start_rects(rects)

    if return_sorting_time:
        sorting_start_time = time.time()

    if(start_rects_sorting_func is not False):
        start_rects = start_rects_sorting_func(start_rects)


    if return_sorting_time:
        sorting_time = time.time() - sorting_start_time



    n = sum(rects.values()) - 2

    if return_runtime: start_time = time.time()

    for s, start_rect in enumerate(start_rects):

        rects[start_rect] -= 2
        current_cuboid = start_rect + (2,)
        cuboid_list, cuboid = rebuild_cuboid_a(current_cuboid, rects, n)

        if cuboid_list is not False:
            cuboid_list = [start_rect, start_rect] + cuboid_list
            return get_output(True)
        else:
            rects[start_rect] += 2
    print("Cannot rebuild cuboid")
    return get_output(False)

def run_stats(params):

    # create an empty list to store the data
    data = []

    # loop through the parameters and run the algorithm
    for input_size in tqdm(range(params['step'], params['max_input_size'], params['step'])):
        for dim_vs_n in params['dim_vs_n_values']:
            for run in range(params['runs']):
                # calculate the rects parameter
                n_rects = input_size
                rects = parse_data(get_sample_data(n_rects, n_rects * dim_vs_n))
                for algo_name, algo in params['algos'].items():
                    # run the algorithm and get the stats for all metrics
                    stats = get_stats(rects.copy(), metrics=params['metrics'], start_rects_sorting_func=algo)

                    data.append((input_size, dim_vs_n, run, algo_name, *[stat_val for stat_val in stats.values()]))


    # create a pandas DataFrame with the MultiIndex
    df = pd.DataFrame(data, columns=['input_size', 'dim_vs_n', 'run', 'algorithm', *stats.keys()])

    # pivot the DataFrame to have the metrics as values
    df = df.set_index(['algorithm', 'input_size', 'dim_vs_n', 'run'])

    return df

if __name__ == "__main__":
    params = {
        'max_input_size': 1000,
        'step': 100,
        'runs': 10,
        'dim_vs_n_values': [.1, .5, 1, 2],
        'algos': {
            'first': lambda start_rects: sorted(start_rects, key = lambda x: x[0]),
            'second': lambda start_rects: sorted(start_rects, key = lambda x: x[1]),
            'area': lambda start_rects: sorted(start_rects, key = lambda x: x[0] * x[1]),
            'kmeans*area': lambda start_rects: advanced_sorting(start_rects, lambda x: x[0] * x[1]),
            'kmeans*first': lambda start_rects: advanced_sorting(start_rects, lambda x: x[0]),
            'kmeans*second': lambda start_rects: advanced_sorting(start_rects, lambda x: x[1]),
        },
        'metrics': ['runtime', 'start_rect_position', 'start_rect_count', 'sorting_time', 'start_rect', 'start_rects'],
    }

    #run_stats(params)
    rects = parse_data([(9,10),(9,10),(2,10),(2,10),(3,11),(3,11),(3,10),(3,10),(3,13), (10,11)])

    print(get_stats(rects, metrics=[]))

    #
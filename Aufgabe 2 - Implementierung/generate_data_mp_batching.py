import time
from multiprocessing import Pool, Manager
from threading import Thread
import pandas as pd
from joblib import Parallel, delayed
from algo import rebuild_cuboid_a, rebuild_cuboid_b
from tqdm import tqdm
from utils import get_start_rects, get_data, parse_data, get_sample_data, advanced_sorting
import dill

dill.settings['recurse'] = True

def get_stats_mp(input):
    input = dill.loads(input)
    n = input[0]
    dim_vs_n = input[1]
    algos = input[2]
    run_number = input[3]
    metrics = input[4]

    return_runtime = 'runtime' in metrics
    return_start_rect = 'start_rect' in metrics
    return_start_rect_count = 'start_rect_count' in metrics
    return_start_rect_position = 'start_rect_position' in metrics
    return_start_rects = 'start_rects' in metrics
    return_cuboid = 'return_cuboid' in metrics
    return_solution = 'return_solution' in metrics
    return_sorting_time = 'sorting_time' in metrics


    def run(rects, start_rects_sorting_func, return_sorting_time, return_runtime):


        def get_output(success):
            output = [input[0], dim_vs_n, name, run_number]
            if return_runtime:
                output.append(time.time() - start_time)
            if return_start_rect_position:
                output.append(start_rects.index(start_rect) if success else -1)
            if return_start_rect_count:
                output.append(len(start_rects))
            if return_sorting_time:
                output.append(sorting_time)
            if return_start_rect:
                output.append(start_rect if success else (-1, -1))
            if return_start_rects:
                output.append(start_rects)
            if return_cuboid:
                output.append(current_cuboid)
            if return_solution:
                output.append(cuboid_list)


            output = tuple(output)
            return output

        start_rects = get_start_rects(rects)

        if return_sorting_time:
            sorting_start_time = time.time()
            if start_rects_sorting_func is not None:
                start_rects = start_rects_sorting_func(start_rects)
            sorting_time = time.time() - sorting_start_time

        n = sum(rects.values()) - 2

        if return_runtime: start_time = time.time()

        for s, start_rect in enumerate(start_rects):

            rects[start_rect] -= 2
            current_cuboid = start_rect + (2,)
            cuboid_list, cuboid = rebuild_cuboid_b(current_cuboid, rects, n)

            if cuboid_list is not False:
                cuboid_list = [start_rect, start_rect] + cuboid_list
                return get_output(True)
            else:
                rects[start_rect] += 2
        print("Cannot rebuild cuboid")
        return get_output(False)

    data, info = get_sample_data(n, n*dim_vs_n)
    rects_init = parse_data(data)
    out = []

    for name, algo in algos.items():

        appendix = run(rects_init.copy(), dill.loads(algo), return_sorting_time, return_runtime)
        out.append(appendix)

    return out


def get_parameters(params, n_batches, describe_batches=False):

    max_input_size = params['max_input_size']
    step = params['step']
    runs = params['runs']
    dim_vs_n_values = params['dim_vs_n_values']
    algos = params['algos']
    metrics = params['metrics']

    out = []


    def batch_input(input):

        batched_input = []
        batch = []

        tmp = 0
        total_weight = sum(w[0] for w in input)
        total_lenth = len(input)
        target_batch_weight = total_weight/n_batches

        def analyse_batches(batched_data):
            print('Generated', len(batched_data), 'Batches with total weight:', total_weight)

            for i, batch in enumerate(batched_data):
                print("---Total weight of batch", i, ':', sum([dill.loads(w)[0] for w in batch]))

            #avg error of batch weight from target_batch_weight
            print('Average error of batch weight from target_batch_weight:', round(sum([abs(sum([dill.loads(w)[0] for w in batch]) - target_batch_weight)/target_batch_weight for batch in batched_data])/len(batched_data), 3), '%')

        for _ in range(n_batches):

            while True:

                if(len(input) > 0):
                    next_el = input.pop()
                    tmp += next_el[0]
                    batch.append(dill.dumps(next_el))

                if(tmp >= target_batch_weight):break
                elif(len(input) == 0):break

            batched_input.append(batch)
            batch = []
            tmp = 0

        if describe_batches:analyse_batches(batched_input)
        return batched_input, total_lenth

    for name, algo in algos.items():
        algos[name] = dill.dumps(algo)

    for dim_vs_n in dim_vs_n_values:
        for run in range(runs):
            for input_size in range(step, max_input_size, step):
                out.append((input_size, dim_vs_n, algos, run, metrics))

    out, total_length = batch_input(out)

    return out, total_length


def progress_bar(totals,queue):
    if isinstance(totals, list):
        splitted = True
        pbars = [
            tqdm(
                desc=f'Worker {pid + 1}',
                total=total,
                position=pid,
            )
            for pid, total in enumerate(totals)
        ]
    else:
        splitted = False
        pbars = [
            tqdm(total=totals)
        ]

    while True:
        try:
            message = queue.get()
            if message.startswith('update'):
                if splitted:
                    pid = int(message[6:])
                    pbars[pid].update(1)
                else:
                    pbars[0].update(1)
            elif message == 'done':
                break
        except:
            pass
    for pbar in pbars:
        pbar.close()


def task_wrapper(pid, function, batch, queue):
    result = []
    for input in batch:
        result.append(function(input))
        queue.put(f'update{pid}')
    return result


def batch_process(params, n_workers=1, sep_progress=False, describe_batches=False):

    # Divide data in batches
    input, total_length = get_parameters(params, n_workers, describe_batches=describe_batches)

    # Check single or multiple progress bars
    if sep_progress:
        totals = [len(batch) for batch in input]
    else:
        totals = total_length

    # Start progress bar in separate thread
    manager = Manager()
    queue = manager.Queue()
    progproc = Thread(target=progress_bar, args=(totals, queue))
    progproc.start()

    # Parallel process the batches
    result = Parallel(n_jobs=n_workers)(
        delayed(task_wrapper)
        (pid, get_stats_mp, batch, queue)
        for pid, batch in enumerate(input)
    )

    # Stop the progress bar thread
    queue.put('done')
    progproc.join()

    # Flatten result
    flattened = [value for batch_list in result for algo_list in batch_list for value in algo_list]

    print("Generated", len(flattened), "rows!")

    df = pd.DataFrame(flattened, columns=['input_size', 'dim_vs_n', 'algorithm', 'run', *params['metrics']])

    return df


if __name__ == '__main__':
    params = {
        'max_input_size': 1000,
        'step': 100,
        'runs': 100,
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
    res = batch_process(params, n_workers=12, sep_progress=False, describe_batches=True)
    res.to_csv('data/results.csv', index=False)
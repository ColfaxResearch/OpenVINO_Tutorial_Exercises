from IPython.core.display import HTML
from IPython.display import display, Image
import ipywidgets as widgets
import time
import matplotlib
import matplotlib.pyplot as plt
import os, glob 
import warnings

def waitForJob(job_name, target, show_stdio=True):
    job_id = job_name[0].split('.')[0]
    output_file = "obj_det.o{}".format(job_id)
    stderr_file = "obj_det.e{}".format(job_id)
    results_file = "results/{}_val.txt".format(target)
    timeout=300
    counter = 0
    while not os.path.exists(output_file):
        if counter > timeout/0.5:
            break
        counter+=1
        time.sleep(0.5)

    if os.path.exists(output_file):
        if show_stdio:
            print("\nstdout:")
            with open(output_file) as f:
                print(f.read())        
        if os.path.exists(stderr_file) and show_stdio:
            print("\nstderr:")
            with open(output_file) as f:
                print(f.read())
        if os.path.exists(results_file):
            print("{} results:".format(target))
            with open(results_file) as f:
                print(f.read())
        else:
            print("\n{} job did not produce a results file.".format(target))
    else:
        print("\n {} job did not complete in {} seconds. Giving up.".format(target, timeout))

def summaryPlot(results_path, x_axis, y_axis, title ):
    ''' Bar plot input:
	results_path: path to result file and label {path_to_result:label}
	x_axis: label of the x axis
	y_axis: label of the y axis
	title: title of the graph
    '''
    warnings.filterwarnings('ignore')
    clr = 'xkcd:blue'

    plt.figure(figsize=(15, 8))
    plt.title(title , fontsize=28, color='black', fontweight='bold')
    plt.ylabel(y_axis, fontsize=16, color=clr)
    plt.xlabel(x_axis, fontsize=16, color=clr)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    val = []
    arch = []
    err = []
    diff = 0
    for file_ in glob.iglob("results/*_val.txt"):
        if os.path.isfile(file_):
            with open(file_, "r") as f:
                dev = f.readline().split(":", maxsplit=1)[1]
                num_requests = float(f.readline().split(":", maxsplit=1)[1])
                infer_stat = f.readline().split(":", maxsplit=1)[1]
                infer_avg = float(infer_stat.split("+-")[0])
                infer_std = float(infer_stat.split("+-")[1])
                arch.append(dev)
                val.append(infer_avg)
                err.append(infer_std)

    offset = max(val)/100
    for v, e in zip(val, err):
        precision = 2 
        if v >= pow(10, precision):
            data = '{:.0f}'.format(round(v/pow(10, precision+1), precision)*pow(10, precision+1))
        else:
            data = '{{:.{:d}g}}'.format(round(precision)).format(v)
        data = data+"+/- {}".format(e)
        y = v + offset   
        plt.text(diff, y, data, fontsize=14, multialignment="center",horizontalalignment="center", verticalalignment="bottom",  color='black')
        diff += 1
    plt.ylim(top=(max(val)+10*offset))
    plt.bar(arch, val, width=0.8, align='center', color=clr)
    plt.show()
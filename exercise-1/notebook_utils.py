import os.path                       
import time
def waitForJob(job_name):
    job_id = job_name[0].split('.')[0]
    output_file = "objdet.o"+job_id
    stderr_file = "objdet.e"+job_id
    timeout=120
    counter = 0
    while not os.path.exists(output_file):
        if counter > timeout/0.5:
            break
        counter+=1
        time.sleep(0.5)
    if os.path.exists(output_file):
        print("\nstdout:")

        with open(output_file) as f:
            print(f.read())
    if os.path.exists(stderr_file):
        print("\nstderr:")
        with open(stderr_file) as f:
            print(f.read())
    else:
        print("job did not complete in {} seconds. Giving up.".format(timeout))
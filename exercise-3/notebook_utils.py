# Utility Quality-of-Life code tyhat automatically waits for the output tp be ready.
import os.path                       
import time
def waitForJob(job_name):
    print("Job submitted. Waiting for output. This make take some time.")
    job_id = job_name[0].split('.')[0]
    output_file = "objdet.o"+job_id
    timeout=600
    counter = 0
    while not os.path.exists(output_file):
        if counter > timeout/0.5:
            break
        counter+=1
        time.sleep(0.5)
    if os.path.exists(output_file):
        with open(output_file) as f:
            print(f.read())
    else:
        print("job did not complete in {} seconds. Giving up.".format(timeout))
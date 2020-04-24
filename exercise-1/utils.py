import requests
import jwt
import sys
import time
import json
import subprocess


def submitToDevCloud(script, node_type, script_args=[], files=[]):
    def getJWT():
        output = subprocess.run(["/usr/local/bin/jwt-generator.py"], capture_output=True)
        return output['stdout']
    
    # Creating AuthBase (see https://2.python-requests.org/en/master/user/authentication/)
    class JWTAuth(requests.auth.AuthBase):
        def __call__(self, r):
            jwt_tok = getJWT()
            r.headers['Authorization'] = "Bearer "+jwt_tok
            return r

    submit_files = {'submission.sh': open(script,'rb')}
    for file in files:
        submit_files[file]=open(file,'rb')

    ov_version='openvino2020.2'
    if node_type == "CPU":
        #node_flag = '-l nodes=1:tank-870:i5-6500te:{}'.format(ov_version)
        node_flag = '-l nodes=s001-n001'
    elif node_type == "GPU":
        node_flag = '-l nodes=1:tank-870:i5-6500te:iei-mustang-f100-a10:{}'.format(ov_version)
    elif node_type == "VPU":
        node_flag = '-l nodes=1:tank-870:i5-6500te:iei-mustang-f100-a10:{}'.format(ov_version)
    elif node_type == "FPGA":
        node_flag = '-l nodes=1:tank-870:i5-6500te:iei-mustang-f100-a10:{}'.format(ov_version)
    else:
        raise Exception("Unkown node_type: {}. Only CPU, GPU, VPU, and FPGA are supported.".format(node_type))
        
    qflags = [node_flag, '-q batch@v-qsvr-2'] 
    if len(script_args) > 0:
        qflags.append("-F '{}'".format(" ".join(script_args)))
    post_data = {'qflags':json.dumps(qflags)}

    r_post = requests.post('https://devapi.edge.devcloud.intel.com/jobapi/jobs', files=submit_files, data=post_data, auth=JWTAuth())
    if(r_post.status_code != 200):
        print("Error during job submittion. Please contact admin.")
        print(r_post.text)
        return
    
    job_id = json.loads(r_post.text)['data']['job_id']
    print("Submitted. Job ID: {}".format(job_id))
    print("Witing for job to complete. This may take a few minutes.", end ="")
    count = 0
    while True:
        r_post = requests.get('https://devapi.edge.devcloud.intel.com/jobapi/jobs/{}'.format(job_id), auth=JWTAuth())
        if(r_post.status_code != 200):
            print("Error getting job status. Trying again. If this message repeats, please contact admin.")
            print(r_post.text)
        else:
            if count%3 == 0:
                print(".", end ="")
            res = json.loads(r_post.text)['data']['status']
            if res == 'C':
                print("")
                break
        count+=1
        time.sleep(1)

    r_res = requests.get('https://devapi.edge.devcloud.intel.com/jobapi/jobs/{}/results'.format(job_id), params={'filename':'stdio.txt'}, auth=JWTAuth())
    if(r_res.status_code == 200):
        print("")
        print(r_res.text)

    else:
        print("Error getting job result. Please contact admin.")
        print(r_res.text)
        

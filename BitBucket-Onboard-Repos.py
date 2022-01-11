import requests
from requests.auth import HTTPBasicAuth
import json

##--------Configuration--------------------------------------------------------------------------------->


# ---- BitBucket authentication credentails ------
username = 'xxxxxx'
password = 'xxxxxx'
scm_repo_url = 'https://api.bitbucket.org/2.0/repositories/xxxxxx'

#---------IQ Server --------------------------------
iq_username = 'admin'
iq_password = 'admin123'
repo_prefix = 'BB_'
#repo prefix is optional and can be used to differentiate scm applications from other applications with the same name scanned in IQ. Set it to '' if not needed

repo_branch = 'master'
stage_id = 'source'
iq_auto_org_name = 'BitBucket'
iq_server__url = 'http://localhost:8070/'


full_repo_list = []
repo_eval_count = 0
repo_exist_count = 0


#--- Get IQ Parent Organizaton id  -----
org_url = iq_server__url+"api/v2/organizations/?organizationName="+iq_auto_org_name

payload = ""
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("GET", org_url, auth=HTTPBasicAuth(iq_username, iq_password), headers=headers, data=payload)
org_json = response.json()

#------Check if organization is valid --------
count = len(org_json['organizations'])
if (count==0):
    print("Organization " + iq_auto_org_name + " does not exists")

else:
    org_id=org_json['organizations'][0]['id']



# Request 100 repositories per page (and only their slugs), and the next page URL

next_page_url = scm_repo_url+'?pagelen=100&fields=next,values.links.html.href,values.slug'
print ("Access SCM URL: ", next_page_url)



# Keep fetching pages while there's a page to fetch
while next_page_url is not None:
  response = requests.get(next_page_url, auth=HTTPBasicAuth(username, password))
  page_json = response.json()

  # Parse repositories from the JSON
  for repo in page_json['values']:
    reponame=repo['slug']
    repourl=repo['links']['html']['href']

    print  ("Repo url: ", reponame+","+repourl)
    full_repo_list.append(repo['slug'])

    #--- IQ Server - create new application with repo name

    app_public_id = repo_prefix+reponame


    #-- Check if application already exists before creating t=new application --->
    print ("Check if application exists: ", app_public_id)

    iq_app_exist_url = iq_server__url+"api/v2/applications?publicId="+app_public_id
    payload = {}
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("GET", iq_app_exist_url, auth=HTTPBasicAuth(iq_username, iq_password), headers=headers, data=payload)
    app_json = response.json()

    count = len(app_json['applications'])

    #print("Count app: ", count)


    if (count>0) :
        print (app_public_id + " is already used as a name and will not be evaluated")
        repo_exist_count += 1
        continue
    else:
        # -- Create new spplication with the name of the repo

        print ("Create new application: " + app_public_id)
        iq_url = iq_server__url+"api/v2/applications"

        payload = json.dumps({
        "publicId": app_public_id,
        "name": repo_prefix+reponame,
        "organizationId": org_id,
        "contactUserName": iq_username
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", iq_url, auth=HTTPBasicAuth(iq_username, iq_password), headers=headers, data=payload)
        #print("IQ response: "+response.text)
        iq_json = response.json()
        app_id=iq_json['id']

        # -- IQ create source control for new application

        scm_url = iq_server__url+"api/v2/sourceControl/application/"+app_id
        payload = json.dumps({
                            "repositoryUrl": repourl,
                            "baseBranch": "master"
                            })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", scm_url, auth=HTTPBasicAuth(iq_username, iq_password), headers=headers, data=payload)


        # ---IQ Server - eval scm - easy onboard of the newly created application
        onboard_url = iq_server__url+"api/v2/evaluation/applications/"+app_id+"/sourceControlEvaluation"

        payload = json.dumps({
                        "stageId": stage_id,
                        "branchName": repo_branch
                        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", onboard_url, auth=HTTPBasicAuth(iq_username, iq_password), headers=headers, data=payload)


        repo_eval_count += 1

        continue
# -------------------------------------------------------------------------------
# Get the next page URL, if present
  # It will include same query parameters, so no need to append them again
  next_page_url = page_json.get('next', None)

# Result length will be equal to `size` returned on any page

print ("Result: Total repos found", len(full_repo_list),  "; Total repos onboarded: ", repo_eval_count, "; Total repos skipped due to previous onboarding in IQ: ", repo_exist_count )

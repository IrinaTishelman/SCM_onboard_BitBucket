# SCM_onboard_BitBucket

Update configuration section of the script with speciic login credentails and url for BitBucket and IQ server
Tokens are acceptable

##--------**Configuration**-------------------------------------------------------------------------------->


# ---- BitBucket authentication credentails ------
username = 'xxxxxx'
password = 'xxxxxx'
scm_repo_url = 'https://api.bitbucket.org/2.0/repositories/xxxxxx'

#---------**IQ Server** --------------------------------
iq_username = 'admin'
iq_password = 'admin123'
repo_prefix = 'BB_'
#repo prefix is optional and can be used to differentiate scm applications from other applications with the same name scanned in IQ. Set it to '' if not needed

repo_branch = 'master'
stage_id = 'source'

# iq server organization designated to be used for onboarding
iq_auto_org_name = 'BitBucket'

iq_server__url = 'http://localhost:8070/'


**Running Script**
python3 BitBucket-List-Repos.py

**Troubleshooting**
ImportError: No module named requests

Use $ pip install requests (or pip3 install requests for python3) if you have pip installed. If pip is installed but not in your path you can use python -m pip install requests (or python3 -m pip install requests for python3)

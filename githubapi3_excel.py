#!/usr/bin/env python

import requests
import base64
import json
import os,sys

class gBranch:
    def __init__(self, org=''):
        self.__ss = self.__load_json("./.setting.json")
        self.__org = self.__ss["organization"] if not org else org 
        self.__file_url = {}

    def __load_json(self, file):
        try:
            with open(file, "rb") as f:
                return json.load(f)
        except IOError:
            print "Json file load error"
            return None
    
    def __save_protected_branches(self, js_data):
        with open(self.__pbh_file, "w+") as f:
            json.dump(js_data,f)
            f.flush

    def __githubapi_request(self, url, data="", method='GET'):
        base64string = base64.encodestring('%s/token:%s' % (self.__ss['org_owner_id'],self.__ss['org_token'])).replace('\n', '')
        headers={ 'Content-Type': 'application/json', 'Authorization': "Basic %s" % base64string } 
        #request.get_method = lambda: method
        try:
            res = requests.get(url,data=json.dumps(data), headers=headers)
            response=res.json()
            while 'next' in res.links.keys():
                res=requests.get(res.links['next']['url'],headers=headers)
                response.extend(res.json())
            # print json.dumps(response,sort_keys=True, indent=4)
            return response

        # except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        # except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
            print e
            sys.exit(1)

    # list all repositories in an organization
    def list_repos(self):
        #url = "%s/orgs/%s/repos" % ( self.__ss['api_endpoint'], self.__org )
        url = "%s/users/%s/repos" % ( self.__ss['api_endpoint'], self.__org )
        print "list repoistories url %s in organization %s "  % ( url, self.__org )
        resp = self.__githubapi_request(url)
        return [ r['name'] for r in resp ] 
        
    # list all content in an organization
    def list_files(self, repos ):
        #url = "%s/orgs/%s/repos" % ( self.__ss['api_endpoint'], self.__org )
        url = "%s/repos/%s/%s/contents" % ( self.__ss['api_endpoint'], self.__ss['org_owner_id'], repos )
        print "list file url %s in repos %s "  % ( url, repos )
        resp = self.__githubapi_request(url)
        print json.dumps(resp, sort_keys=True, indent=4)
        for r in resp:
            self.__file_url[r['path']] = r['url']
        return self.__file_url

    # list all content in an organization
    def download_file(self, filename):
        #url = "%s/orgs/%s/repos" % ( self.__ss['api_endpoint'], self.__org )
        # url = "%s/repos/%s/%s/contents/file" % ( self.__ss['api_endpoint'], self.__ss['org_owner_id'], repos )
        print "list file url %s "  % ( self.__file_url[filename])
        resp = self.__githubapi_request(self.__file_url[filename])
        content = base64.decodestring(resp['content'])
        with open(filename, "wb") as f:
            f.write(content)
 
    # list all branches in a repository
    def list_branch(self, repos):
        url = "%s/repos/%s/%s/branches" % ( self.__ss['api_endpoint'], self.__org, repos)
        # print "list branches url %s in repository %s" % ( url, repos )
        resp = self.__githubapi_request(url)
        # print json.dumps(resp, sort_keys=True, indent=4)
        return [ r['name'] for r in resp ]
 
    # get informatoin in a branch of repository
    def get_branch(self, repos, branch, protected=False):
        if protected == 0:
            url = "%s/repos/%s/%s/branches/%s" % ( self.__ss['api_endpoint'], self.__org, repos, branch)
        else:
            url = "%s/repos/%s/%s/branches/%s/protection" % ( self.__ss['api_endpoint'],self.__org, repos, branch)
        resp = self.__githubapi_request(url)
        print json.dumps(resp, sort_keys=True, indent=4)

def main():
    gb=gBranch()
    # gb=gBranch('UnixServerOperations')
    # gb=gBranch('NGSE')
    repos = gb.list_repos()
    print repos[0]
    #for r in repos:
    #    for bh in gb.list_branch(r):
    #        gb.get_branch(r, bh)
    #files = gb.list_files(repos[0])
    #for f in files:
    #    print f
    #    gb.download_file(f)

if __name__ == "__main__": main()


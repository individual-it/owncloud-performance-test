import owncloud
import os
import sys
import time
import multiprocessing 

servers=[
#          {'name':'git_master',
#           'url':'http://10.49.32.226/owncloud_git',
#          'users':[{'login':'test1','password':'test1'},{'login':'test2','password':'test2'},{'login':'test3','password':'test3'},{'login':'test4','password':'test4'}],
#          'pre-execution-command':'',
#          },

          {'name':'git_master',
           'url':'http://localhost/owncloud-core',
          'users':[{'login':'test1','password':'test1'},{'login':'test2','password':'test2'},{'login':'test3','password':'test3'},{'login':'test4','password':'test4'}],                    
          'pre-execution-command':''

          },

          {'name':'skip_unnecessary_cache_updates',
           'url':'http://localhost/owncloud-fix',
          'users':[{'login':'test1','password':'test1'},{'login':'test2','password':'test2'},{'login':'test3','password':'test3'},{'login':'test4','password':'test4'}],          
          'pre-execution-command':''
          },

    ]

def downloadFolderRecursive (oc):
    directories=oc.list('owncloudtest')
    for directory in directories:
        files=oc.list(directory.path)

        for file in files:
            if file.file_type == 'file':
                oc.get_file(file.path,'/dev/null')
                            
                sys.stdout.write(".")
                sys.stdout.flush()

def uploadFoderRecursive (oc):
    for directory, subdirectories, files in os.walk('owncloudtest/'):

        for subdirectory in subdirectories:
            directoryToCreate=os.path.join(directory, subdirectory)
            oc.mkdir(directoryToCreate)
            
        for file in files:
            filename = os.path.join(directory, file)
            oc.put_file(filename,filename)
            sys.stdout.write(".")
            sys.stdout.flush()
                
    
if __name__ == '__main__':
 
    results={'small_files_upload':[],
             'small_files_download':[]}

    for server in servers:
        multiOc=[]
        os.system(server['pre-execution-command'])
        time.sleep(1)
        for user in server['users']:
            oc=owncloud.Client(server['url'])
            oc.login(user['login'],user['password'])
            multiOc.append(oc)
        
        
        for oc in multiOc:
            try:
                oc.delete('owncloudtest')
            except Exception:
                pass

        start = time.time()

        for oc in multiOc:
            oc.mkdir('owncloudtest')

        print "testing upload small files to " + server['url']
        jobs = []

        for oc in multiOc:        
            p = multiprocessing.Process(target=uploadFoderRecursive, args=(oc,))
            p.start()
            jobs.append(p)
            
        for j in jobs:
            j.join()  
        
        end = time.time()
        result = (end - start)
        results['small_files_upload'].append(result)
        print
        print "Time used: " + str(result)
        time.sleep(2)
        
        print "testing PROFIND + download small files from " + server['url']
        start = time.time()

        jobs = []

        for oc in multiOc:
            p = multiprocessing.Process(target=downloadFolderRecursive,args=(oc,))
            p.start()
            jobs.append(p)

        for j in jobs:
            j.join()

        end = time.time()
        result = (end - start)
        results['small_files_download'].append(result)  
        print
        print "Time used: " + str(result)


    sys.stdout.write ('"";')
    for server in servers:
        sys.stdout.write ('"'+server['name']+'";')

    print

    for test in results:
        sys.stdout.write ('"'+test+'";')
        for result in results[test]:
            sys.stdout.write (str(result)+';')
        print


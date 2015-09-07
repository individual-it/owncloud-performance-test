import owncloud
import os
import sys
import time
import multiprocessing 

servers=[

          {'name':'git_master',
           'url':'http://localhost/owncloud-core',
          'users':[{'login':'test1','password':'test1'},{'login':'test2','password':'test2'},{'login':'test3','password':'test3'},{'login':'test4','password':'test4'}],                    
          'pre-execution-command':'cd /home/artur/www/owncloud-core/;git checkout master'

          },

          {'name':'skip_unnecessary_cache_updates',
           'url':'http://localhost/owncloud-core',
          'users':[{'login':'test1','password':'test1'},{'login':'test2','password':'test2'},{'login':'test3','password':'test3'},{'login':'test4','password':'test4'}],          
          'pre-execution-command':'cd /home/artur/www/owncloud-core/;git checkout skip_unnecessary_cache_updates'
          },

    ]

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
        jobs_alive=0

        for directory, subdirectories, files in os.walk('owncloudtest/'):

            for subdirectory in subdirectories:
                for oc in multiOc:
                    directoryToCreate=os.path.join(directory, subdirectory)
                    #oc.mkdir(directoryToCreate)
                    p = multiprocessing.Process(target=oc.mkdir, args=(directoryToCreate,))
                    p.start()
                    jobs.append(p)

                for j in jobs:
                    j.join()
                 
            for file in files:
                filename = os.path.join(directory, file)
                for oc in multiOc:
                    p = multiprocessing.Process(target=oc.put_file, args=(filename,filename))
                    p.start()
                    jobs.append(p)


                sys.stdout.write(".")
                sys.stdout.flush()

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
            directories=oc.list('owncloudtest')
            for directory in directories:
                files=oc.list(directory.path)

                for file in files:
                    if file.file_type == 'file':
                        p = multiprocessing.Process(target=oc.get_file, args=(file.path,'/dev/null'))
                        p.start()
                        jobs.append(p)

                        sys.stdout.write(".")
                        sys.stdout.flush()
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


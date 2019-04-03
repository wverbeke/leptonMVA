import os
import subprocess
import time


def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def walkLimitedDepth( input_directory, max_depth ):
	
	#remove trailing separators 
	input_directory = input_directory.rstrip( os.path.sep )

	#depth of input directory 
	base_depth = input_directory.count( os.path.sep )

	for directory, subdirectories, files in os.walk( input_directory ):
		yield directory, subdirectories, files
		current_depth = directory.count( os.path.sep )
		if ( current_depth - base_depth ) >= max_depth :
			del subdirectories[:]



def listSampleDirectories( input_directory, name_to_search ):
    for directory, subdirectories, files in walkLimitedDepth( input_directory, 1):
        for subdir in subdirectories:
            if name_to_search in subdir:
                yield directory, subdir


def listFiles( input_directory, identifier ):
    for directory, subdirectories, files in os.walk( input_directory ):
        for f in files:
            if identifier in f:
                yield os.path.join( directory, f )


def listParts( input_list, chunk_size ):
    for i in range( 0, len(input_list), chunk_size ):
        yield input_list[ i : i + chunk_size ]
 

if __name__ == '__main__': 

    #identify all present samples in input directory 
    input_directory = '/pnfs/iihe/cms/store/user/wverbeke/heavyNeutrino'
    name_to_search = 'PFN_list'
    #sample_directories = listSampleDirectories( input_directory, name_to_search )
    sample_directories = []
    sample_sub_directories = []
    for sample_directory, subdirectory in listSampleDirectories( input_directory, name_to_search ):
        sample_directories.append( sample_directory )
        sample_sub_directories.append( subdirectory )

    sample_names = [ directory.rstrip( os.path.sep ).split( os.path.sep )[-1] for directory in sample_directories ]

    #make output directories 
    output_directory_base = '/user/wverbeke/Work/'
    output_directory_base = os.path.join( output_directory_base, 'ntuples_temp_' )

    sample_output_directories = []
    for sample in sample_names:
        output_directory = output_directory_base + sample
        if not os.path.exists( output_directory ):
            os.makedirs( output_directory )
        sample_output_directories.append( output_directory )


    for sample_directory, sub_directory, output_directory in zip( sample_directories, sample_sub_directories, sample_output_directories ):

        #identify locations of files to process for a given sample 
        root_files = list( listFiles( os.path.join( sample_directory, sub_directory ), '.root' ) )

        files_per_job = 10
        #split_files in lists of files_per_job
        for chunk in listParts( root_files, files_per_job ):
            
            #make a job script 
            with open('flatFileProducer.sh', 'w') as script:
                script.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
                script.write('cd CMSSW_10_2_13/src\n' )
                script.write('eval `scram runtime -sh`\n') 
                script.write('cd {}\n'.format( output_directory ) ) 
                command = 'python flatTuple.py'
                for root_file in chunk:
                	command += ' {}'.format( root_file )
                script.write( command + '\n')
            
        	#submit job and catch errors 
            while True:
                try:
                    qsub_output = subprocess.check_output( 'qsub flatFileProducer.sh', shell=True, stderr=subprocess.STDOUT )

                #submission failed, try again after one second 
                except subprocess.CalledProcessError as error:
                    print('Caught error : "{}".\t Attempting resubmission.'.format( error.output.split('\n')[0] ) )
                    time.sleep( 1 )

                #submission succeeded 
                else:
                    first_line = qsub_output.split('\n')[0]
                    print( first_line )
                    break

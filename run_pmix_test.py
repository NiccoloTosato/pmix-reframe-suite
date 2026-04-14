import os
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import time
from prrte_build_class import build_prrte
from pmix_build_class import build_pmix
from libevent_build_class import build_libevent

class fetch_pmixtest(rfm.RunOnlyRegressionTest):
    descr = "Fetch pmix test"
    repository = f"https://github.com/NiccoloTosato/pmix-tests.git"
    executable = 'git'
    executable_opts = ["clone",f"{repository}"]
    local = True
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode,0)
    
    
class base_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    prrte = fixture(build_prrte, scope = 'environment')
    pmix =  fixture(build_pmix, scope = 'environment')
    libevent = fixture(build_libevent, scope = 'environment')
    pmix_tests = fixture(fetch_pmixtest, scope = 'session')
    path = list()
    ld_library_path = list()
    num_cpus_per_task = 1
    time_limit = '0d0h5m0s'
    @run_before('run')
    def prepare_run(self):
        for fix in [self.prrte, self.pmix, self.libevent]:
            self.path.append(os.path.join(fix.stagedir,"bin"))
            self.ld_library_path.append(os.path.join(fix.stagedir,"lib"))
        self.env_vars = {
            "PATH" : ":".join(self.path) + ":${PATH}",
            "LD_LIBRARY_PATH" : ":".join(self.ld_library_path) + ":${LD_LIBRARY_PATH}"
        }
        self.executable = os.path.join("")
        # prepare the environment, with LD and PATH
    @sanity_function
    def retcode(self):
        return sn.assert_eq(self.job.exitcode,0)
    @run_before('run', always_last=True)
    def start_internal_timer(self):
        # Starts the moment ReFrame prepares to submit the job to Slurm
        self.t_start = time.time()

    @run_after('run')
    def stop_internal_timer(self):
        # Triggers the moment ReFrame detects the Slurm job has finished
        self.t_end = time.time()

    @performance_function('s')
    def total_walltime(self):
        # Calculate the difference and return it as your performance metric
        return self.t_end - self.t_start

@rfm.simple_test
class hello_test(base_test):
    descr = "Test if it works"
    test_name = "hello_world"
    num_tasks = 120
    num_tasks_per_node = 12

    @run_before("run")
    def compile_test(self):
        test_dir_base = self.pmix_tests.stagedir
        test_path = os.path.join(test_dir_base, "pmix-tests/prrte", self.test_name)
        print(test_path)
        self.prerun_cmds = [ f'cd {test_path}', './build.sh' ]    
        self.executable="./run.sh"
    @performance_function('s')
    def hostname_test(self):
        patt = r"^RUNTIME,(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)"
        # Extract the values
        return sn.extractall(
            patt, 
            self.stderr,          
            tag=(1),        # Capture Group 1 (Real), Group 2 (User), Group 3 (Sys), Get only 1
            conv=float            
        )[0]
    @performance_function('s')
    def pmix_lib_test(self):
        patt = r"^RUNTIME,(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)"
        # Extract the values
        return sn.extractall(
            patt, 
            self.stderr,          
            tag=(1),        # Capture Group 1 (Real), Group 2 (User), Group 3 (Sys), Get only 1
            conv=float            
        )[1]

    
@rfm.simple_test
class cycle_test(base_test):
    descr = "Test Cycle in pmix-test"
    test_name = "cycle"
    num_tasks = 120
    num_tasks_per_node = 12

    @run_before("run")
    def compile_test(self):
        test_dir_base = self.pmix_tests.stagedir
        test_path = os.path.join(test_dir_base, "pmix-tests/prrte", self.test_name)
        print(test_path)
        self.prerun_cmds = [ f'cd {test_path}', './build.sh' ]    
        self.executable="./run.sh"

@rfm.simple_test
class prun_wrapper_test(base_test):
    descr = "Test prun-wrapper in pmix-test"
    test_name = "prun-wrapper"
    num_tasks = 120
    num_tasks_per_node = 12

    @run_after("init")
    def setup_deps(self):
        # This is encessary, there could be concurrency problems, since both test compile hello world
        self.depends_on('hello_test')
        
    @run_before("run")
    def compile_test(self):
        test_dir_base = self.pmix_tests.stagedir
        test_path = os.path.join(test_dir_base, "pmix-tests/prrte", self.test_name)
        print(test_path)
        self.prerun_cmds = [ f'cd {test_path}', './build.sh', 'scontrol show hostnames $SLURM_JOB_NODELIST > hostfile.txt' ]    
        self.executable="./run.sh"
        self.env_vars['CI_HOSTFILE'] = f"{os.path.join(test_path,'hostfile.txt')}"

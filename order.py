import os
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn

class fetch_libevent(rfm.RunOnlyRegressionTest):
    descr = "Fetch libevent"
    version = variable(str,value = '2.1.12')
    url = f"https://github.com/libevent/libevent/releases/download/release-{version}-stable/libevent-{version}-stable.tar.gz"
    executable = 'wget'
    executable_opts = [f"{url}"]
                       
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode,0)

class fetch_pmix(rfm.RunOnlyRegressionTest):
    descr = "Fetch pmix"
    version = variable(str,value = '6.1.0')
    url = f"https://github.com/openpmix/openpmix/releases/download/v{version}/pmix-{version}.tar.gz"
    executable = 'wget'
    executable_opts = [f"{url}"]
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode,0)

class fetch_prrte(rfm.RunOnlyRegressionTest):
    descr = "Fetch prrte"
    version = variable(str,value = '4.1.0')
    url = f"https://github.com/openpmix/prrte/releases/download/v{version}/prrte-{version}.tar.gz"
    executable = 'wget'
    executable_opts = [f"{url}"]
    
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode,0)

class fetch_pmixtest(rfm.RunOnlyRegressionTest):
    descr = "Fetch pmix test"
    repository = f"https://github.com/openpmix/pmix-tests.git"
    executable = 'git'
    executable_opts = ["clone",f"{repository}"]
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode,0)
    

class build_libevent(rfm.CompileOnlyRegressionTest):
    descr = 'Build libevent'
    build_system = 'Autotools'
    build_prefix = variable(str)
    libevent = fixture(fetch_libevent, scope='session')

    @run_before('compile')
    def prepare_build(self):
        self.build_system.config_opts = [f"--prefix={self.stagedir}"]
        tarball = f"libevent-{self.libevent.version}-stable.tar.gz"
        self.build_prefix = ".".join(tarball.split(".")[:3])
        fullpath = os.path.join(self.libevent.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8
        self.postbuild_cmds = ['make install']
    

class build_pmix(rfm.CompileOnlyRegressionTest):
    descr = 'Build pmix'
    build_system = 'Autotools'
    build_prefix = variable(str)
    pmix = fixture(fetch_pmix, scope='session')
    libevent = fixture(build_libevent, scope='environment')
    @run_before('compile')
    def prepare_build(self):
        tarball = f"pmix-{self.pmix.version}.tar.gz"
        self.build_prefix = ".".join(tarball.split(".")[:3])
        fullpath = os.path.join(self.pmix.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8
        self.postbuild_cmds = ['make install']
        self.build_system.config_opts = [f"--prefix={self.stagedir} --with-libevent={self.libevent.stagedir}"]

class build_prrte(rfm.CompileOnlyRegressionTest):
    descr = 'Build prrte'
    build_system = 'Autotools'
    build_prefix = variable(str)
    prrte = fixture(fetch_prrte, scope='session')
    libevent = fixture(build_libevent, scope='environment')
    pmix = fixture(build_pmix, scope='environment')

    @run_before('compile')
    def prepare_build(self):
        tarball = f"prrte-{self.prrte.version}.tar.gz"
        self.build_prefix = ".".join(tarball.split(".")[:3])
        fullpath = os.path.join(self.prrte.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8
        self.postbuild_cmds = ['make install']
        self.build_system.config_opts = [f"--prefix={self.stagedir}  --with-libevent={self.libevent.stagedir}  --with-pmix={self.pmix.stagedir}"]
        
    
class base_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    prrte = fixture(build_prrte, scope = 'environment')
    pmix =  fixture(build_pmix, scope = 'environment')
    libevent = fixture(build_libevent, scope = 'environment')
    pmix_tests = fixture(fetch_pmixtest, scope = 'session')
    path = list()
    ld_library_path = list()
    
    @run_before('run')
    def prepare_run(self):
        for fix in [prrte,pmix,libevent]:
            print(c)
            self.path.append(os.path.join(fix.stagedir,"bin"))
            self.ld_library_path.append(os.path.join(fix.stagedir,"lib"))
        self.env_vars = {
            "PATH" : ":".join(self.path) + ":${PATH}",
            "LD_LIBRARY_PATH" : ":".join(self.ld_library_path) + ":${LD_LIBRARY_PATH}"
        }
        
        self.executable = os.path.join("")
        # prepare the environment, with LD and PATH
    @sanity_function
    def dummy(self):
        return sn.assert_eq(self.job.exitcode,0)

@rfm.simple_test
class first_test(base_test):
    descr = "Test if it works"
    executable = "./run.sh"
    test_name = "hello_world"
    @run_before("run")
    def compile_test(self):
        test_dir_base = self.pmix_tests.stagedir
        test_path = os.path.join(test_dir_base, "prrte", test_name)
        self.prerun_cmds = [ f'cd {test_path}', './build.sh' ]    
        


    

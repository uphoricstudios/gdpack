import shutil
import ruamel.yaml
from os import path
import semver
import os
import sys
from github import Github
from shutil import copy2
import secret
import requests
from zipfile import ZipFile

class Project:

    GDPACK_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\.gdpack'
    BIN_CACHE_DIR = GDPACK_DIR + '\\bin_cache'
    PROJECT_LIST = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\project.list'
    PROJECT_FILE = 'gdpack.project'
    DEV_VERSION = 'dev'
    PROJECT_LIB_DIR = 'libs'
    git = Github(secret.TOKEN)
    #git = Github()

    def __init__(self):
        self.package_list = {}
        self.repo_cache = {}
        self.create_gdpack_folder()
        self.load_package_list()
        self.create_bin_cache_folder()
        print(self.git.rate_limiting) #temp

    def t(self):
        lib_package_path = path.join(self.PROJECT_LIB_DIR, 'gdpack')
        print(os.listdir(lib_package_path))

    def download_release(self, package, tag, add_to_req = True):
        zip_file_name = package + '-' + tag + '.zip'
        zip_path = path.join(self.BIN_CACHE_DIR, package, zip_file_name)
        lib_package_path = path.join(self.PROJECT_LIB_DIR, package)
        self.create_project_libs_folder()
        print(zip_path)
        print(lib_package_path)

        #check if cache exists, if it does, copy that
        if(path.exists(lib_package_path)):
            print(package + " already exists, do you want to override?")
            ans = self._yes_or_no("[y/N]: ", 'n')
            
            if(ans == 'n'):
                print('Aborting...')
                quit()
            
            else:
                shutil.rmtree(lib_package_path)

            
        os.mkdir(lib_package_path)

        if(not path.exists(zip_path)):
            self.make_package_cache_folder(package)
            zipdata = requests.get(self.repo_cache[package].get_release(tag).zipball_url, allow_redirects = True)
            open(zip_path, 'wb').write(zipdata.content)
        
        
        shutil.unpack_archive(zip_path, lib_package_path)
        git_folder = path.join(lib_package_path, os.listdir(lib_package_path)[0])
        
        for content in os.listdir(git_folder):
            shutil.move(path.join(git_folder, content), lib_package_path)
        
        shutil.rmtree(git_folder)
        
        if(add_to_req):
            self.add_requirement(package, tag)

        installed_packages = self.get_installed_packages()
        package_project_file = self.get_package_project_file(package)
        package_requirements = self.get_package_requirements(package_project_file)

        for req in package_requirements:
            if(req['package'] in installed_packages):
                continue
            self.download_release(req['package'], req['tag'], False)
        



    def get_package_requirements(self, project_dict) -> list:
        return project_dict.get('requirements', [])


    def get_package_project_file(self, package):
        package_project = path.join(self.PROJECT_LIB_DIR, package, self.PROJECT_FILE)
        
        with open(package_project, 'r') as project_file:
            return ruamel.yaml.load(project_file.read(), Loader=ruamel.yaml.Loader)
    

    def get_installed_packages(self):
        package_list = []
        
        for package_dir in os.listdir(self.PROJECT_LIB_DIR):
            if(path.isdir(path.join(self.PROJECT_LIB_DIR, package_dir))):
                package_list.append(package_dir)
        
        return package_list


    def add_requirement(self, package, tag):
        if(self.project_file_exists()):
            project_dict = self.load_project_file()

            if('requirements' not in project_dict):
                project_dict['requirements'] = []
            
            for package_dict in project_dict['requirements']:
                if(package == package_dict.get('package', '')):
                    package_dict['tag'] = tag
                    break
            else:
                project_dict['requirements'].append({
                    'package': package,
                    'tag': tag
                })
            
            self.save_project_file(project_dict)


    def make_package_cache_folder(self, package):
        if(path.exists(path.join(self.BIN_CACHE_DIR, package))):
            return
        
        os.mkdir(path.join(self.BIN_CACHE_DIR, package))

    
    @classmethod
    def create_bin_cache_folder(cls):
        if(path.exists(cls.BIN_CACHE_DIR)):
            return
        
        os.mkdir(cls.BIN_CACHE_DIR)

    
    def check_release_tag_exists(self, package, tag):
        try:
            self.get_package(package)
            self.repo_cache[package].get_release(tag)
            return True
        except:
            return False
    

    def get_package(self, package):
        try:
            self.repo_cache[package] = self.git.get_repo(self.package_list[package])
            return True
        
        except:
            return False


    def check_package_exists(self, package):
        if package in self.package_list:
            return True
        
        return False


    def load_package_list(self):
        with open(self.PROJECT_LIST, 'r') as list:
            self.package_list = ruamel.yaml.load(list.read(), Loader=ruamel.yaml.Loader)


    def load_project_file(self) -> dict:
        if(self.project_file_exists()):
            with open(self.PROJECT_FILE, 'r') as project_file:
                return ruamel.yaml.load(project_file.read(), Loader=ruamel.yaml.Loader)
        
        else:
            return None


    def save_project_file(self, project_dict):
        with open(self.PROJECT_FILE, 'w') as project_file:
            ruamel.yaml.dump(project_dict, project_file, default_flow_style=False)

    @classmethod
    def create_gdpack_folder(cls):
        if(path.exists(cls.GDPACK_DIR)):
            return
        
        os.mkdir(cls.GDPACK_DIR)


    @classmethod
    def create_project_libs_folder(cls):
        if(path.exists(cls.PROJECT_LIB_DIR)):
            return
        
        os.mkdir(cls.PROJECT_LIB_DIR)


    @classmethod
    def project_file_exists(cls):
        if(path.exists(cls.PROJECT_FILE)):
            return True
        
        return False

    
    def create_project_file(self):
        if(self.project_file_exists()):
            print('A gdpack project file already exists.')
            overwrite = self._yes_or_no('Would you like to overwrite? (y/N): ', 'n')

            if(overwrite == 'n'):
                print('Aborting...')
                quit()
            
            self.init_project_file()


    def init_project_file(self):
        project_dict = {}
        project_dict['project'] = {}
        project_dict['project']['project_name'] = self._get_project_name()
        project_dict['project']['description'] = input('Description: ')
        project_dict['project']['version'] = self._get_version()
        project_dict['project']['authors'] = input('Authors: ')
        project_dict['project']['git_repository'] = input('Git Repository: ')

        self.save_project_file(project_dict)


    @staticmethod
    def _get_project_name():
        project_name = input('Project name: ').lower()
        
        while project_name == '':
            print('Project name cannot be empty: ')
            project_name = input('Project name: ').lower()
        
        return project_name


    def _get_version(self):
        version = input('Version: ').lower()
        
        while self._try_get_version(version) == False:
            print('Invalid version, only semantic version supported: ')
            version = input('Version: ').lower()
        
        return version


    @staticmethod
    def _try_get_version(version):
        try:
            version = semver.VersionInfo.parse(version)
            return True
        except:
            return False


    @staticmethod
    def _yes_or_no(msg, default = -1):
        choices = ['y', 'n']
        choice = input(msg).lower()

        if(choice == '' and default != -1):
            return default
        else:
            while choice not in choices:
                choice = input('Choose one of [%s]:' % ', '.join(choices)).lower()
        
        return choice

import ruamel.yaml
from os import path
import semver
import os
import sys
from github import Github
import secret
import requests

GDPACK_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\.gdpack'
BIN_CACHE_DIR = GDPACK_DIR + '\\bin_cache'
PROJECT_LIST = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\project.list'
PROJECT_FILE = 'gdpack.project'
DEV_VERSION = 'dev'
PROJECT_LIB_DIR = 'libs'
git = Github(secret.TOKEN)
#git = Github()

project_dict = {}
package_list = {}
repo_cache = {}


def download_release(package, tag):
    global repo_cache

    #check if cache exists, if it does, copy that

    create_gdpack_folder()
    create_bin_cache_folder()
    make_package_cache_folder(package)
    
    zipdata = requests.get(repo_cache[package].get_release(tag).zipball_url, allow_redirects = True)
    zip_file_name = package + '-' + tag + '.zip'
    open(_create_path(BIN_CACHE_DIR, package, zip_file_name), 'wb').write(zipdata.content)


def make_package_cache_folder(package):
    if(path.exists(_create_path(BIN_CACHE_DIR, package))):
        return
    
    os.mkdir(_create_path(BIN_CACHE_DIR, package))


def create_bin_cache_folder():
    if(path.exists(BIN_CACHE_DIR)):
        return
    
    os.mkdir(BIN_CACHE_DIR)

def check_release_tag_exists(package, tag):
    global repo_cache

    try:
        repo_cache[package].get_release(tag)
        return True
    except:
        return False


def check_package_accessible(package):
    global package_list
    load_package_list()
    
    try:
        repo_cache[package] = git.get_repo(package_list[package])
        return True
    
    except:
        return False


def check_package_exists(package):
    global package_list
    load_package_list()
    
    if package in package_list:
        return True
    
    return False


def load_package_list():
    global package_list

    with open(PROJECT_LIST, 'r') as list:
        package_list = ruamel.yaml.load(list.read(), Loader=ruamel.yaml.Loader)


def load_project_file():
    global project_dict

    if(project_file_exists()):
        with open(PROJECT_FILE, 'r') as project_file:
            project_dict = ruamel.yaml.load(project_file.read(), Loader=ruamel.yaml.Loader)
            return True
    
    else:
        print('No project file exists.')
        print('Create one with "gdpack init".')
        return False


def create_gdpack_folder():
    if(path.exists(GDPACK_DIR)):
        return
    
    os.mkdir(GDPACK_DIR)


def create_project_libs_folder():
    if(path.exists(PROJECT_LIB_DIR)):
        return
    
    os.mkdir(PROJECT_LIB_DIR)


def project_file_exists():
    if(path.exists(PROJECT_FILE)):
        return True
    
    return False


def create_project_file():
    if(project_file_exists()):
        print('A gdpack project file already exists.')
        overwrite = _yes_or_no('Would you like to overwrite? (y/N): ', 'n')

        if(overwrite == 'n'):
            print('Aborting...')
            quit()
        
        init_project_file()


def init_project_file():
    global project_dict
    project_dict = {}
    project_dict['project'] = {}
    project_dict['project']['project_name'] = get_project_name()
    project_dict['project']['description'] = input('Description: ')
    project_dict['project']['version'] = get_version()
    project_dict['project']['authors'] = input('Authors: ')
    project_dict['project']['git_repository'] = input('Git Repository: ')

    with open(PROJECT_FILE, 'w') as project_file:
        ruamel.yaml.dump(project_dict, project_file, default_flow_style=False)


def get_project_name():
    project_name = input('Project name: ').lower()
    
    while project_name == '':
        print('Project name cannot be empty: ')
        project_name = input('Project name: ').lower()
    
    return project_name


def get_version():
    version = input('Version: ').lower()
    
    while _try_get_version(version) == False:
        print('Invalid version, only semantic version supported: ')
        version = input('Version: ').lower()
    
    return version


def _try_get_version(version):
    try:
        version = semver.VersionInfo.parse(version)
        return True
    except:
        return False


def _yes_or_no(msg, default = -1):
    choices = ['y', 'n']
    choice = input(msg).lower()

    if(choice == '' and default != -1):
        return default
    else:
        while choice not in choices:
            choice = input('Choose one of [%s]:' % ', '.join(choices)).lower()
    
    return choice

def _create_path(*argv):
    if(argv.count == 0):
        return ''
    
    result = argv[0]

    for path in argv:
        if(result == path):
            continue

        result += '\\' + path
    
    return result
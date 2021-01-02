import click
import configparser
import semver
#from github import Github
#from secret import secret_token
from os import path

PROJECT_FILE = 'gdpack.project' 
config = configparser.ConfigParser()
#print(Github(secret_token).get_user().name)

@click.group()
def cli():
    pass

@cli.command(name='init')
def init():
    if(path.exists(PROJECT_FILE)):
        print('A gdpack project file already exists.')
        overwrite = yes_or_no('Would you like to overwrite? (y/N): ', 'n')

        if(overwrite == 'n'):
            print("Aborting...")
            return
        
    
    config['project'] = {}
    config['project']['project_name'] = get_project_name()
    config['project']['description'] = input('Description: ')
    config['project']['version'] = get_version()
    config['project']['authors'] = input('Authors (comma separated): ')
    config['project']['git_repository'] = input('Git Repository: ')

    with open(PROJECT_FILE, 'w') as configfile:
        config.write(configfile)



def yes_or_no(msg, default = -1):
    choices = ['y', 'n']
    choice = input(msg).lower()

    if(choice == '' and default != -1):
        return default
    else:
        while choice not in choices:
            choice = input("Choose one of [%s]:" % ", ".join(choices)).lower
    
    return choice


def get_project_name():
    project_name = input("Project name: ")
    
    while project_name == "":
        project_name = input("Project name cannot be empty: ")
    
    return project_name

def get_version():
    version = input("Version: ")
    while _try_get_version(version) == False:
        print("Invalid version, only semantic version supported: ")
        version = input("Version: ")
    
    return version
    
def _try_get_version(version):
    try:
        version = semver.VersionInfo.parse(version)
        return True
    except:
        return False

    # name: (project-name) project-name
    # version: (0.0.0) 0.0.1
    # description: The Project Description
    # entry point: //leave empty
    # test command: //leave empty
    # git repository: //the repositories url
    # keywords: //leave empty
    # author: // your name
    # license: N/A

if __name__ == '__main__':
    cli()
import click
from project import Project


project = Project()

@click.group()
def cli():
    pass


@cli.command(name='init')
def init():
    if(project.project_file_exists()):
        print('Project File exists, override?')
        ans = project._yes_or_no('[y/N]', 'n')
        
        if(ans == 'n'):
            print('Aborting...')
            quit()
    
    project.init_project_file()
    


@cli.command(name='install')
@click.argument('package')
@click.argument('tag', default='latest')
def install(package, tag):
    print(package)
    print(tag)
    if(project.check_release_tag_exists(package, tag)):
        project.download_release(package, tag)
    
    else:
        print("Package could not be found! Is your version correct?")



if __name__ == '__main__':
    cli()
import click
import semver
import project
import os
import sys
#from github import Github


#project.create()

@click.group()
def cli():
    pass


@cli.command(name='init')
def init():
    if(project.check_package_accessible('gdpack')):
        pass
        #project.download_release('gdpack', '0.0.1')


@cli.command(name='install')
@click.argument('package')
@click.argument('tag', default='latest')
def install(package):
    print(project.check_package_exists(package))



if __name__ == '__main__':
    cli()
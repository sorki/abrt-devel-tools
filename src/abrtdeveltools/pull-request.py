import git
import sys
from abrtgithub import get_team_repos
from configreader import read_config


def get_repo_dict():
	repo_dict = {}
	ghrepos = get_team_repos(*read_config(path_to_conf="/home/jmoskovc/redhat/snippets/management_scripts/github.conf"))
	for ghrepo in ghrepos:
		repo_dict[ghrepo.name] = ghrepo

	return repo_dict


if __name__ == "__main__":
	#print ref
	if len(sys.argv) < 2:
		print "Usage:\n\tpull-request reponame"
		sys.exit(1)

	repo = git.Repo(".")  # must be run from the to dir in the git tree (dir containing .git/)
	ref = repo.head.reference
	repo_dict = get_repo_dict()
	print ref.commit.message
	#branch_name = head.split('/')[-1]
	print "Going to create pull request from branch '{0}' to master branch of repo '{1}'".format(ref, repo_dict[sys.argv[1]].name)
     #create_pull(self, *args, **kwds)
     #    :calls: `POST /repos/:user/:repo/pulls <http://developer.github.com/v3/todo>`_
     #    :param title: string
     #    :param body: string
     #    :param issue: :class:`github.Issue.Issue`
     #    :param base: string
     #    :param head: string

	pull = repo_dict[sys.argv[1]].create_pull(title=ref.commit.message, body="", base="master", head=str(ref))
	if pull:
		print "Successfully created new pull request: '{0}'".format(pull.html_url)

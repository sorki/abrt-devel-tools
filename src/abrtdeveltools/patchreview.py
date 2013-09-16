#! /bin/python

import re
import sys
from subprocess import Popen, PIPE

OK = 0
FAIL = 1
BRANCHES_REQUIRING_BUGZILLA = ["rhel6"]

# just for testing
string = """
    abrt-ccpp: try to read hs_err.log from crash's CWD

    - it is expected that this may fail in some particular cases but the
      failure is not critical a the hook will pass it

    - closes #622

    Signed-off-by: Jakub Filak <jfilak@redhat.com>
    Signed-off-by: Jiri Moskovcak <jmoskovc@redhat.com>
"""


def get_branch():
    # git rev-parse --abbrev-ref HEAD
    git_branch = Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=PIPE, bufsize=-1).communicate()[0]

    if not git_branch:
        raise Exception("Can't get current branch")

    return git_branch.strip()


def read_commits():
    git_log = Popen(["git", "log", "@{u}.."], stdout=PIPE, bufsize=-1).communicate()[0]
    #print "'%s'" % git_log
    if not git_log:
        print "No new commits on branch '{0}'".format(get_branch())
        return ""

    return git_log


def parse_commits(git_log):
    commit_start = "commit"
    commits = {}
    lines = git_log.split('\n')
    #print lines
    current_commit = None
    commit = None
    for line in lines:
        if line[0:len(commit_start)] == commit_start:
            if commit:
                commits[current_commit] = commit
                commit = ""
            else:
                commit = line + "\n"
            current_commit = line[len(commit_start)+1:]
        else:
            commit += line + "\n"

    else:
        commits[current_commit] = commit

    return commits


def check_signoff(sha, msg):
    """
    Checks if the commit is properly signed
    """
    retval = OK
    signoff_regexp = re.compile(r'(Signed-off-by: \w+ \w+ <\w+@\w+(?:\.\w+)+>)')

    matches = signoff_regexp.findall(msg)
    if not matches:
        print "ERROR: The patch '{0}' is not properly signed, please use git commit -s when committing changes".format(sha)
        retval = FAIL

    return retval


def check_ticket(sha, msg):
    """
    Checks if the commit references a ticket, either form github or bugzilla
    Alowed values:
      -- TODO@@ abrt/abrt#686
      rhbz#12345
      closes #1234
      related #12345

    """
    #print "ticket"
    retval = OK

    rhbz_regexp = re.compile(r'(rhbz#\d+)')
    # closes #1234 or related #12345
    github_regexp = re.compile(r'((loses|elated) #\d+)')

    matches_rhbz = rhbz_regexp.findall(msg)
    if get_branch() in BRANCHES_REQUIRING_BUGZILLA:
        matches_github = 0  # we don't care about github tickets in the internal branches
    else:
        matches_github = github_regexp.findall(msg)
    if not (matches_rhbz or matches_github):
        print "ERROR: The commit message of the commit '{0}' doesn't reference any ticket, it should either reference github (closes|related #12345) or bugzilla (rhbz#12345)".format(sha)
        retval = FAIL

    return retval


if __name__ == "__main__":
    retval = OK
    git_log = read_commits()
    if not git_log:
        sys.exit(0)
    commits = parse_commits(git_log)

    for sha, msg in commits.items():
        retval |= check_signoff(sha, msg)
        retval |= check_ticket(sha, msg)

    sys.exit(retval)

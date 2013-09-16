#! /bin/python
# -*- coding: utf-8 -*-

from github import Github
import sys
from datetime import datetime, timedelta
from ticket import Ticket

ORGANIZATION = "abrt"

GHLOGIN_TO_RHLOGIN = {
    "dkutalek":"dkutalek@redhat.com",
    "dvlasenk":"dvlasenk@redhat.com",
    "jfilak":"jfilak@redhat.com",
    #"karelklic":"karelklic@redhat.com",
    "mlichvar":"mlichvar@redhat.com",
    "mmilata":"mmilata@redhat.com",
    "mozeq":"jmoskovc@redhat.com",
    "mtoman":"mtoman@redhat.com",
    "pkubatrh":"pkubat@redhat.com",
    "sorki":"rmarko@redhat.com",
}


def get_team_repos(login, password, team=ORGANIZATION):
    hub = Github(login, password)
    org = hub.get_organization(ORGANIZATION)
    repos = org.get_repos()
    return repos

def get_repo(login, password, reponame=""):
    hub = Github(login, password)
    return hub.get_repo("mozeq/{0}".format(reponame))

def get_pull_requests(login, password):
    pulls_dict = {}
    for repo in get_team_repos(login, password):
        pulls = pulls_dict.get(repo.name, [])
        pulls += list(repo.get_pulls())
        pulls_dict[repo.name] = pulls


    return pulls_dict


def get_issues_for_current_sprint(login, password, sprintname="Feb2013"):

    issue_list = []

    hub = Github(login, password)
    org = hub.get_organization(ORGANIZATION)
    repos = org.get_repos()
    for repo in repos:
        #print repo.name
        try:
            #sprintlabel = repo.get_label("Feb2013")
            #sprintlabel = repo.get_label("Mar2013")
            sprintlabel = repo.get_label("Apr2013")
        except Exception:
            #print ex
            continue

        issues = list(repo.get_issues(labels=[sprintlabel], state=u"closed"))
        issues += list(repo.get_issues(labels=[sprintlabel], state=u"open"))
        for issue in issues:
            issue.repo = repo
            assignee = issue.assignee
            assignee_name = "NOBODY"
            try:
                assignee_name = assignee.name
            except Exception:
                pass

            issue_list.append(Ticket(
                                    issue.repo.name,
                                    issue.number,
                                    issue.title,
                                    issue.assignee.name if issue.assignee else "NOBODY",
                                )
            )

    return issue_list

def closed_this_month(login, password):

    today = datetime.today()
    since = datetime(year=today.year, month=today.month, day=1)

    print "{0} - {1}".format(today, since)

    issue_list = []

    hub = Github(login, password)
    org = hub.get_organization(ORGANIZATION)
    repos = org.get_repos()
    for repo in repos:

        issues = list(repo.get_issues(since=since, state=u"closed"))
        for issue in issues:
            issue.repo = repo
            issue_list.append(Ticket(
                                    issue.repo.name,
                                    "gh#{0}".format(issue.number),
                                    issue.title,
                                    GHLOGIN_TO_RHLOGIN.get(issue.closed_by.login, "UNKNOWN"),
                                )
            )

    return issue_list

def state_color(issue):
    if issue.state == "closed":
        return "#99CC66"

    if issue.state == "open":
        if issue.assignee != None:
            return "#FFAA44"
        else:
            return "#FF6600"

    return

def print_issues(tickets, format=None):

    if not format:
        for ticket in tickets:
            print u"{0!s} | {1!s} | {2!s}".format(
               ticket.get_component(),
               ticket.get_id(),
               ticket.get_summary(),
               ticket.get_assignee(),
               #ticket.created_at,
               # the encoding is needed when piping the output
               # otherwise it throws an exception
               #ticket.updated_at
               ).encode("utf-8", "ignore")

        return

    if format == "html":
        print ("<html>\n\t<body><head>"
        "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>")
        print "<p>Last updated: {0!s}</p>".format(datetime.now())
        print u"\t<table>"
        print u"<tr><th>Assignee</th><th>Project</th><th>Ticket URL</th><th>Summary</th></tr>"
        for ticket in tickets:
            color = state_color(ticket)
            print u"<tr bgcolor=\"{4!s}\"><td>{3!s}</td><td>{0!s}</td><td><a href=\"https://github.com/abrt/{0!s}/tickets/{1!s}\">#{1!s}</a></td><td>{2!s}</td></tr>".format(
                   ticket.get_component(),
                   ticket.get_id(),
                   ticket.get_summary(),
                   ticket.get_assignee(),
                   color
                   # the encoding is needed when piping the output
                   # otherwise it throws an exception
                   ).encode("utf-8", "ignore")

        print u"\t</table>"
        print u"\t</body>\n</html>"

if __name__ == "__main__":
    format = None
    if len(sys.argv) < 3:
        print "Usage: {0!s} login password".format(sys.argv[0])
        sys.exit()

    if "htmlout" in sys.argv:
        format = "html"

    #tickets = get_issues_for_current_sprint(sys.argv[1], sys.argv[2])
    issues = closed_last_month(sys.argv[1], sys.argv[2])
    print_issues(issues, format, state_filter="closed")



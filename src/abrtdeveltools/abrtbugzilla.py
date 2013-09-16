#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import bugzilla
from datetime import datetime
from datetime import timedelta
import getpass
from ticket import Ticket


def closed_since(login, password, since=None):
    sys.stderr.write("Closed bugs since: {0!s}  until: {1!s}\n".format(since, datetime.today()))

    rhbz = bugzilla.bugzilla3.Bugzilla36(url="https://bugzilla.redhat.com/xmlrpc.cgi")
    try:
        #print "Logging in"
        rhbz.login(login, password)
    except Exception, ex:
        print "Can't login: %s" % ex

    query_dict = {
        "product":["Fedora", "Red Hat Enterprise Linux 6", "Red Hat Enterprise Linux 7", "Fedora EPEL"],
        #"component":["libreport", "abrt", "btparser", "satyr", "retrace-server", "busybox", "strace", "gnome-abrt"],
        "assigned_to":[
            "mtoman@redhat.com",
            "jfilak@redhat.com",
            "jmoskovc@redhat.com",
            "mmilata@redhat.com",
            "mlichvar@redhat.com",
            "rmarko@redhat.com",
            "dvlasenk@redhat.com",
            "pkubat@redhat.com",
            "abrt-devel-list@redhat.com"
        ],
        #"assigned_to": "abrt-devel-list@redhat.com",
        "bug_status":["CLOSED", "ON_QA", "VERIFIED", "MODIFIED"],
        "last_change_time": since,
        #"cf_last_closed":since,
    }

    #print "Querying bugzilla for:"
    #for k,v in query_dict.iteritems():
    #    print "\t %s : %s" % (k,v)

    #query_dict = {
    #    "bug_id":702723
    #}

    print "Querying bz"
    rh_bugs = rhbz.query(query_dict)
    #print "Found: ", len(rh_bugs)
    #needinfo = rh_bugs[0].requestees.login_nameget_flags("needinfo")
    #print needinfo

    #for field in rhbz.getbugfields():
    #    print field

    # filter closed since, because the query returns all changed since
    bugs = []
    counter=0
    filtered_out = []
    for bug in rh_bugs:
        counter+=1
        sys.stdout.write("\033[sProcessing ticket '{0}' ({1} of {2}){3}:\033[u"
                    .format
                    (
                        bug.bug_id,
                        counter,
                        len(rh_bugs),
                        "(filtered: '{0}')".format(len(filtered_out)) if filtered_out else "",
                    )
            )
        sys.stdout.flush()  # need to flush because we don't print \n

        try:
            cf_last_closed = bug.__getattr__("cf_last_closed")
            bug.last_closed = cf_last_closed
        except KeyError, ex:  # the bug is not closed, but is one of ON_QA, VERIFIED
            #print ex
            #print "ERROR: ", bug.bug_id, ex
            #print bug.bug_id, bug.short_desc
            #continue
            cf_last_closed = bug.__getattr__("last_change_time")
            bug.last_closed = cf_last_closed

        last_closed = datetime.strptime(str(cf_last_closed), "%Y%m%dT%H:%M:%S")
        delta = last_closed - since
        if delta.days >= 0 and delta < datetime.today() - since:
            #print "({0!s}) | {1!s} | {2!s} | {3!s}".format(bug.assigned_to, bug.bug_id, bug.resolution, bug.short_desc)
            #print "{1!s} | {0!s} | {2!s} {3}".format(bug.bug_id, bug.component[0], bug.short_desc, last_closed)
            bugs.append(Ticket(
                    bug.component[0],
                    "rhbz#{0}".format(bug.bug_id),
                    bug.short_desc,
                    bug.assigned_to,
                ))
        else:
            filtered_out.append(bug)

    if filtered_out:
        print "Filtered:"
        for bug in filtered_out:
            print "{0} | {1}".format(bug.bug_id, bug.last_closed)


    if rh_bugs:
        sys.stdout.write("\n")  # have to print line feed because the status line doesn't end with \n
        sys.stdout.flush()

    return bugs


def closed_last_month(login, password):

    delta30 = timedelta(days=30)
    today = datetime.today()
    start = today - delta30
    month_ago = start.strftime("%Y-%m-%d 00:00:00")

    return closed_since(login, password, since=month_ago)


def closed_this_month(login, password):
    now = datetime.today()
    start = datetime(year=now.year, month=now.month, day=1)
    bugs = closed_since(login, password, since=start)

    #print "#rh bugs: ", len(bugs)
    return bugs


def print_monthly_stats(tickets, output=sys.stdout):
    print "Monthly stats"
    delta30 = timedelta(days=30)
    today = datetime.today()
    start = today - delta30

    #print "Searching bugs closed in last month"
    for bug in bugs:
        last_closed = datetime.strptime(str(bug.last_closed), "%Y%m%dT%H:%M:%S")
        delta = last_closed - start
        if delta.days > 0 and delta < delta30:
            #print "({0!s}) | {1!s} | {2!s} | {3!s}".format(bug.assigned_to, bug.bug_id, bug.resolution, bug.short_desc)
            output.write(u"{1!s} | {0!s} | {2!s}\n".format(bug.bug_id, bug.component[0], bug.short_desc).encode("utf8", "ignore"))

def print_stats_per_maintainer(tickets, output=sys.stdout, verbose=False):
    print "Monthly summary"
    ticket_dict = {}
    for ticket in tickets:
        if ticket.assigned_to not in ticket_dict:
            ticket_dict[ticket.assigned_to] = []

        ticket_dict[ticket.assigned_to].append(ticket)

    sorted_list = sorted(ticket_dict.items(), key=lambda x: len(x[1]), reverse=True)
    for maintainer, buglist in sorted_list:
        output.write("{0} has {1} bugs\n".format(maintainer, len(buglist)))
        if verbose:
            for ticket in buglist:
                output.write(">>> {0} {1} {2}\n".format(ticket.bug_id, ticket.short_desc, ticket.bug_status))

    return ticket_dict


if __name__ == "__main__":
    login, password = read_config()
    my_bzs = ""
    bz_list = []
    output = sys.stdout


    if not (login and password):
        if len(sys.argv) < 3:
            login = raw_input("Bugzilla login: ")
            password = getpass.getpass("Bugzilla password: ")
        else:
            login = sys.argv[1]
            password = sys.argv[2]

        if not (login and password):
            print "Usage:\n\t%s bzlogin bzpassword" % sys.argv[0]
            sys.exit(1)

    for opt in sys.argv:
        if "--output" in opt:
            opt, filename = opt.split('=')
            output = open(filename, "w")

    #bugs = closed_last_month(login, password)

    bugs = closed_this_month(login, password)
    print_stats_per_maintainer(bugs, output=output)
    print_monthly_stats(bugs, output=output)

    if output is not None and output is not sys.stdout:
        output.close()


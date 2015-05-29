---
layout: page
title: "Contributing"
category: dev
date: 2015-05-28 15:20:16
order: 1
---
Further contributions to lidar2dems are very much welcome.  Contributions can be as simple as reporting issue
s, or can be enhancements and new features to the code.  Here are guidelines and summary for how to contribut
e. The first step, is to make sure you have a [GitHub account](https://github.com/signup/free) 

## Filing Issues
* Look through the existing issues to see if a similar one already exists.
* If one exists, add any new information about your specific case, if not adequately covered.j
* If one does not exist, submit a new ticket for the issue.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.

## Documentation
For changes of a trivial nature to comments and documentation, it is not necessary to create a new issue. Doc
umentation is done completely on the GitHub wiki, and any changes take effect immediately.  However, document
ation is also published to the [lidar2dems GitHub pages](http://applied-geosolutions.github.io/lidar2dems/). 

Publishing the updated wiki documentation to GitHub pages requires more steps to clone the wiki on a local ma
chine, run Jekyll to convert the markdown to static HTML, commit the changes to the gh-pages branch, then pus
h to the repository.  For now, if any user contributes to the wiki, file an issue that the wiki documentation
 has been updated, and a core committer will update the GitHub pages.

## Making Code Changes
* Fork the repository on GitHub
* Create a topic branch from where you want to base your work.
  * lidar2dems currently uses just the master branch
  * Avoid working on the `master` branch, which should remain in sync with the main repository master
  * To create topic branch based on master: `git checkout -b fix_something master`
* Check for unnecessary changes with `git diff --check` before committing.
* Make commits of logical units, with adequate commit messages. 
* Make sure your commit messages contain something descriptive enough.
* If a commit fixes an issue, make note in the message (e.g., fixes #12), which automatically references and 
closes it when ultimately pushed.

## Submitting Changes
* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository in the puppetlabs organization.
* Update your Jira ticket to mark that you have submitted code and are ready for it to be reviewed (Status: R
eady for Merge).
  * Include a link to the pull request in the ticket.
* The core team looks at Pull Requests on a regular basis in a weekly triage
  meeting that we hold in a public Google Hangout. The hangout is announced in
  the weekly status updates that are sent to the puppet-dev list. Notes are
  posted to the [Puppet Community community-triage
  repo](https://github.com/puppet-community/community-triage/tree/master/core/notes)
  and include a link to a YouTube recording of the hangout.
* After feedback has been given we expect responses within two weeks. After two
  weeks we may close the pull request if it isn't showing any activity.

# Additional Resources

* [General GitHub documentation](http://help.github.com/)
* [GitHub pull request documentation](http://help.github.com/send-pull-requests/)

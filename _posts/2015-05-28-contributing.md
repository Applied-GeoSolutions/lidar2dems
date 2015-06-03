---
layout: page
title: "Contributing"
category: dev
date: 2015-05-28 15:20:16
order: 1
---
Further contributions to lidar2dems are very much welcome.  Contributions can be as simple as reporting issues, or can be enhancements and new features to the code.  Here are guidelines and summary for how to contribute. The first step, is to make sure you have a [GitHub account](https://github.com/signup/free) 

## Filing Issues
* Look through the existing issues to see if a similar one already exists.
* If one exists, add any new information about your specific case, if not adequately covered.
* If one does not exist, submit a new ticket for the issue.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.

## Documentation
For changes of a trivial nature to comments and documentation, it is not necessary to create a new issue. Documentation is done completely using GitHub pages, which uses a special branch called gh-pages in the lidar2dems repository. To make documentation changes, clone the repo and checkout the gh-pages branch.  Changes can be commited just like with regular code, then issue a pull request.

## Making Code Changes
* Fork the repository on GitHub
* Create a topic branch from where you want to base your work.
  * lidar2dems currently uses just the master branch
  * Avoid working on the `master` branch, which should remain in sync with the main repository master
  * To create topic branch based on master: `git checkout -b fix_something master`
* Check for unnecessary changes with `git diff --check` before committing.
* Make commits of logical units, with adequate commit messages. 
* Make sure your commit messages contain something descriptive enough.
* If a commit fixes an issue, make note in the message (e.g., fixes #12), which automatically references and closes it when ultimately pushed.
* Issue a Pull Request

# Additional Resources

* [General GitHub documentation](http://help.github.com/)
* [GitHub pull request documentation](http://help.github.com/send-pull-requests/)

r"""
This module provides a python interface to Sage's git repository.

TESTS::

    sage: from sage.dev.sagedev import SageDev, doctest_config
    sage: git = SageDev(doctest_config()).git
    sage: git.add("untracked_testfile1")
    0
    sage: git.rm('untracked_testfile1',force=True)
    rm 'untracked_testfile1'
    0
    sage: git.mv('testfile', 'new_testfile')
    0
    sage: git.checkout('HEAD', '--', 'testfile')
    0
    sage: git.reset('HEAD', '--', 'new_testfile')
    0
    sage: git.status()
    # On branch first_branch
    # Untracked files:
    #   (use "git add <file>..." to include in what will be committed)
    #
    #   new_testfile
    #   untracked_testfile2
    nothing added to commit but untracked files present (use "git add" to track)
    0
    sage: git.show('master')
    commit ...
    Author: doctest <doctest>
    Date:   Sat Mar 3 09:46:40 1973 +0000
    <BLANKLINE>
        add a testfile
    <BLANKLINE>
    diff --git a/testfile b/testfile
    new file mode 100644
    index 0000000...
    --- /dev/null
    +++ b/testfile
    @@ -0,0 +1 @@
    +this is a test file
    0

AUTHORS:

- TODO: add authors from github's history and trac's history
"""
#*****************************************************************************
#       Copyright (C) 2013 TODO
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import os
import subprocess
import sage.doctest
from sage.env import SAGE_DOT_GIT, SAGE_REPO_AUTHENTICATED
class GitInterface(object):
    r"""
    A wrapper around the ``git`` command line tool.
    Most methods of this class correspond to actual git commands. Some add
    functionality which is not directly available in git. However, all of the
    methods should be non-interactive. If interaction is required the method
    should live in :class:`saged.dev.sagedev.SageDev`.
        sage: from sage.dev.test.config import Config
        sage: from sage.dev.git_interface import GitInterface
        sage: GitInterface(Config())
    def __init__(self, config, UI):
        r"""
        Initialization.
            sage: from sage.dev.git_interface import GitInterface
            sage: type(GitInterface())
        self._UI = UI
        self._config = config
        self._gitcmd = self._config.get('gitcmd', 'git')
        self._repository = self._config.get('repository', SAGE_REPO_AUTHENTICATED)
            raise ValueError("`%s` does not point to an existing directory."%self._dot_git)
        r"""
        Return a printable representation of this instance.


    
    def get_state(self):
        r"""
        Get the current state of merge/rebase/am/etc operations.
        RETURN VALUE:
        A tuple of strings which consists of any of the following:
        ``'rebase'``, ``'am'``, ``'rebase-i'``, ``'rebase-m'``, ``'merge'``,
        ``'bisect'``, ``'cherry-seq'``, ``'cherry'``.
            sage: git.execute_supersilent('merge', 'second_branch')
            sage: git.execute_silent('merge', abort=True)
            sage: git.execute_supersilent('rebase', 'second_branch')
            sage: git.execute_silent('rebase', abort=True)
            sage: git.execute_supersilent('rebase', 'HEAD^', interactive=True,
            sage: git.execute_supersilent('merge', 'second_branch')
            sage: git.execute_silent('rebase', abort=True)

    def reset_to_clean_state(self):
        r"""
        Get out of a merge/am/rebase/etc state and returns True
            sage: git.execute_supersilent('merge', 'second_branch')
            sage: git.execute_supersilent('rebase', 'HEAD^', interactive=True,
            sage: git.execute_supersilent('merge', 'second_branch')
        state = states[0]
        if state.startswith('rebase'):
            self.execute_silent('rebase', abort=True)
        elif state == 'am':
            self.execute_silent('am', abort=True)
        elif state == 'merge':
            self.execute_silent('merge', abort=True)
        elif state == 'bisect':
            raise NotImplementedError(state)
        elif state.startswith('cherry'):
            self.execute_silent('cherry-pick', abort=True)
        else:
            raise RuntimeError("'%s' is not a valid state"%state)
        return self.reset_to_clean_state()
    def reset_to_clean_working_directory(self, remove_untracked_files=False, remove_untracked_directories=False, remove_ignored=False):
        self.execute_silent('reset', hard=True)
        if remove_untracked_files:
            switches = ['-f']
            if remove_untracked_directories: switches.append("-d")
            if remove_ignored: switches.append("-x")
            self.clean(*switches)
    def _run_git(self, cmd, args, kwds, **ckwds):
        r"""
        common implementation for :meth:`execute`,
        :meth:`execute_silent`, :meth:`execute_supersilent`, and
        :meth:`read_output`

        INPUT:

        - ``cmd`` - git command run

        - ``args`` - extra arguments for git

        - ``kwds`` - extra keywords for git

        - ``ckwds`` - Popen like keywords but with the following changes

          - ``stdout`` - if set to `False` will supress stdout

          - ``stderr`` - if set to `False` will supress stderr

        .. WARNING::

            This method does not raise an exception if the git call returns a
            non-zero exit code.

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: r = git._run_git('status', (), {})
            # On branch first_branch
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked_testfile1
            #   untracked_testfile2
            nothing added to commit but untracked files present (use "git add" to track)
            sage: r
            (0, None, None)
            sage: git._run_git('status', (), {}, stdout=False)
            (0, None, None)
            sage: git._run_git('rebase', ('HEAD^',),
            ....:     {'interactive':True,
            ....:      'env':{'GIT_SEQUENCE_EDITOR':'sed -i s+pick+edit+'}}, stdout=False)
            Stopped at ... edit the testfile differently
            You can amend the commit now, with
            <BLANKLINE>
                git commit --amend
            <BLANKLINE>
            Once you are satisfied with your changes, run
            <BLANKLINE>
                git rebase --continue
            <BLANKLINE>
            (0, None, None)
            sage: git._run_git('rebase', (), {'abort':True}, stdout=False, stderr=False)
            (0, None, None)
            sage: git._run_git('log', (), {'oneline':True}, stdout=str)
            (0, '... edit the testfile differently\n... add a testfile\n', None)
        """
        assert self._doctest_mode or not sage.doctest.DOCTEST_MODE, "running doctests which use git/trac is not supported from within a running session of sage"

        s = [self._gitcmd, "--git-dir=%s"%self._dot_git, cmd]

        env = ckwds.setdefault('env', dict(os.environ))
        env.update(kwds.pop('env', {}))

                k = '-' + k
                k = '--' + k.replace('_', '-')
                s.append(k)
            elif v is not False:
                s.extend((k, v))
            s.extend(a for a in args if a is not None)

        s = [str(arg) for arg in s]

        if not self._doctest_mode:
            self._UI.show("[git] %s"%(" ".join(s)))

        if ckwds.get('dryrun', False):

        devnull = open(os.devnull, 'w')
        if ckwds.get('stdout') is False:
            ckwds['stdout'] = devnull
        elif ckwds.get('stdout') is str:
            ckwds['stdout'] = subprocess.PIPE
        if ckwds.get('stderr') is False:
            ckwds['stderr'] = devnull
        elif ckwds.get('stderr') is str:
            ckwds['stderr'] = subprocess.PIPE
        process = subprocess.Popen(s, **ckwds)
        stdout, stderr = process.communicate()
        retcode = process.poll()
        return retcode, stdout, stderr
        r"""
        Run git.

        Raises an exception if git has non-zero exit code.

        INPUT:

        - ``cmd`` - git command to be run

        - ``args`` - extra arguments to supply to git command

        - ``kwds`` - extra arguments through keywords. E.g.

          ::

              graph=True                  => --graph
              message="this is a message" => --message 'this is a message'

        EXAMPLES::

            sage: r = dev.git.execute('status')
            # On branch first_branch
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked_testfile1
            #   untracked_testfile2
            nothing added to commit but untracked files present (use "git add" to track)
            sage: r
            0
            sage: _ = dev.git.execute('log', 'first_branch' , '--', 'testfile', graph=True)
            * commit ...
            | Author: doctest <doctest>
            | Date:   Thu Jul 5 05:20:00 1979 +0000
            |
            |     edit the testfile differently
            |
            * commit ...
              Author: doctest <doctest>
              Date:   Sat Mar 3 09:46:40 1973 +0000
            <BLANKLINE>
                  add a testfile
            sage: r = dev.git.execute('commit')
            # On branch first_branch
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked_testfile1
            #   untracked_testfile2
            nothing added to commit but untracked files present (use "git add" to track)
            sage: r
            1
        """
        exit_code = self._run_git(cmd, args, kwds)[0]
        if exit_code:
            raise GitError(exit_code)

    __call__ = execute
        r"""
        Run git and supress its output to stdout.

        Same input as :meth:`execute`.

        Raises an error if git returns a non-zero exit code.

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: git.execute_silent('status')
            0
            sage: git.execute_silent('rebase', 'HEAD^', interactive=True,
            ....:     env={'GIT_SEQUENCE_EDITOR':'sed -i s+pick+edit+'})
            Stopped at ... edit the testfile differently
            You can amend the commit now, with
            <BLANKLINE>
                git commit --amend
            <BLANKLINE>
            Once you are satisfied with your changes, run
            <BLANKLINE>
                git rebase --continue
            <BLANKLINE>
            0
        """
        exit_code = self._run_git(cmd, args, kwds, stdout=False)[0]
        if exit_code:
            raise GitError(exit_code)
        r"""
        Run git and supress its output to stdout and stderr.

        Same input as :meth:`execute`.

        Raises an error if git returns a non-zero exit code.

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: git.execute_supersilent('status')
            0
            sage: git.execute_supersilent('rebase', 'HEAD^', interactive=True,
            ....:     env={'GIT_SEQUENCE_EDITOR':'sed -i s+pick+edit+'})
            0
        """
        exit_code = self._run_git(cmd, args, kwds, stdout=False, stderr=False)[0]
        if exit_code:
            raise GitError(exit_code)
        r"""
        Run git and return its output to stdout.
        Same input as :meth:`execute`.

        Raises an error if git returns a non-zero exit code.

        EXAMPLES::

            sage: dev.git.read_output('log', oneline=True)
            '... edit the testfile differently\n... add a testfile\n'
        exit_code, ret, _ = self._run_git(cmd, args, kwds, stdout=str, stderr=False)
        if exit_code:
            raise GitError(exit_code)
        return ret

    def is_child_of(self, a, b):
        r"""
            sage: dev.git.is_child_of('master', 'second_branch')
            sage: dev.git.is_child_of('second_branch', 'master')
        r"""
            sage: dev.git.is_ancestor_of('master', 'second_branch')
            sage: dev.git.is_ancestor_of('second_branch', 'master')
        try:
            self.execute('diff', quiet=True)
            return False
        except GitError:
            return True
        r"""
        commits all changes

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: import os
            sage: git = SageDev(doctest_config()).git
            sage: with open(os.path.join(git._tmp_dir, 'testfile'), 'w') as f:
            ....:     f.write('modified this file\n')
            sage: git.has_uncommitted_changes()
            True
            sage: git.commit_all(message="modified a file")
            [first_branch ...] modified a file
                 1 file changed, 1 insertion(+), 1 deletion(-)
            sage: git.has_uncommitted_changes()
            False
            sage: git.commit_all(message="made no changes")
            # On branch first_branch
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked_testfile1
            #   untracked_testfile2
            nothing added to commit but untracked files present (use "git add" to track)
        """
        kwds['all'] = True
        r"""
        returns the list of files that are not being tracked by git
        EXAMPLES::

            sage: dev.git.unknown_files()
            ['untracked_testfile1', 'untracked_testfile2']
        return self.read_output('ls-files',
                        other=True, exclude_standard=True).splitlines()

    def local_branches(self):
        r"""
            ['first_branch', 'second_branch', 'master']
        result = self.read_output('for-each-ref', 'refs/heads/',
                    sort='-committerdate', format="%(refname)").splitlines()
        r"""
        return the current branch
            'first_branch'
        r"""
            sage: dev.git._branch_printname('first_branch')
            'first_branch'
        r"""
        r"""
        r"""
        returns the commit id of the local branch, or ``None`` if
        branch does not exist
            sage: git.branch_exists("first_branch")          # random
            '087e1fdd0fe6f4c596f5db22bc54567b032f5d2b'
            sage: int(git.branch_exists("first_branch"), 16) # random
            48484595766010161581593150175214386043155340587L
            sage: type(git.branch_exists("first_branch"))
            sage: len(git.branch_exists("first_branch"))
        return self.ref_exists("refs/heads/%s"%branch)
        r"""
        returns the commit id of the ref, or ``None`` if
        branch does not exist
        EXAMPLES::

            sage: git = dev.git
            sage: git.ref_exists("refs/tags/test_tag")          # random
            'abdb32da3a1e50d4677e4760eda9433ac8b45414'
            sage: int(git.ref_exists("refs/tags/test_tag"), 16) # random
            981125714882459973971230819971657414365142078484L
            sage: type(git.ref_exists("refs/tags/test_tag"))
            <type 'str'>
            sage: len(git.ref_exists("refs/tags/test_tag"))
            40
            sage: git.ref_exists("refs/tags/asdlkfjasdlf")
        """
        try:
            self.execute("show-ref", ref, quiet=True, verify=True)
        except GitError:
            return None
        return self.read_output("show-ref", ref, hash=True, verify=True).strip()

    def create_branch(self, branchname, basebranch=None, remote_branch=True):
        r"""
        creates branch ``branchname`` based off of ``basebranch`` or the
        current branch if ``basebranch`` is ``None``

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: git.create_branch("third_branch")
            sage: git.branch_exists("third_branch") == git.branch_exists("first_branch")
            True
            sage: git.create_branch("fourth_branch", "second_branch")
            sage: git.branch_exists("fourth_branch") == git.branch_exists("second_branch")
            True
        """
        if branchname in ("t", "ticket", "all", "dependencies", "commit",
                "release", "beta", "master"):
            raise ValueError("bad branchname")
            raise ValueError("branch already exists")

        if basebranch is None:
            ret = self.execute("branch", branchname)
            ret = self.execute("branch", branchname, basebranch)

            self._sagedev._remote[branchname] = remote_branch

        if ret: # return non-zero exit codes
            return ret
        r"""
        renames branch ``oldname`` to ``newname``

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: bool(git.branch_exists("third_branch"))
            False
            sage: git.rename_branch("first_branch", "third_branch")
            sage: bool(git.branch_exists("first_branch"))
            False
            sage: bool(git.branch_exists("third_branch"))
            True
            sage: git.rename_branch("third_branch", "second_branch")
            fatal: A branch named 'second_branch' already exists.
        """
        r"""
        switch to ``branchname`` in a detached state if ``detached`` is
        set to True

        EXAMPLES::

            sage: from sage.dev.sagedev import SageDev, doctest_config
            sage: git = SageDev(doctest_config()).git
            sage: git.current_branch()
            'first_branch'
            sage: git.switch_branch('second_branch')
            Switched to branch 'second_branch'
            sage: git.current_branch()
            'second_branch'
            sage: git.branch_exists('third_branch')
            sage: git.switch_branch('third_branch')
            Switched to branch 'third_branch'
            sage: git.branch_exists('third_branch') # random
            '5249e7a56067e9f30244930192503d502558b6c3'
            sage: git.switch_branch('first_branch', detached=True)
            Note: checking out 'first_branch'.
            <BLANKLINE>
            You are in 'detached HEAD' state. You can look around, make experimental
            changes and commit them, and you can discard any commits you make in this
            state without impacting any branches by performing another checkout.
            <BLANKLINE>
            If you want to create a new branch to retain commits you create, you may
            do so (now or later) by using -b with the checkout command again. Example:
            <BLANKLINE>
              git checkout -b new_branch_name
            <BLANKLINE>
            HEAD is now at ... edit the testfile differently
        """
        move = None
            move = self.save_uncommitted_changes()

        if not detached and self.branch_exists(branchname) is None:
            if self.create_branch(branchname) is not None:
                raise RuntimeError("could not create new branch")

        self.execute("checkout", branchname, detach=detached)

            self.unstash_changes()
    def unstash_changes(self):
        try:
            self.execute_silent("stash", "apply")
            self.execute_silent("stash", "drop")
        except GitError:
            self.execute_silent("reset", hard=True)
            self._UI.show("Changes did not apply cleanly to the new branch. "+
                          "They are now in your stash.")

    def vanilla(self, release=True):
        r"""
        switch to released version of sage
        """
            release = "master"
            release = "release"
            release = str(release)
            if is_release_name(release.split('.')):
                self.execute('fetch', 'origin', tags=True)
                release = self.ref_exists('refs/tags/%s'%release)
                if release is None:
                    raise ValueError("was unable to find desired release")
        self.switch_branch(release)
        r"""
        move branch to trash
            sage: git.abandon('second_branch')
            ['first_branch', 'abandoned/second_branch', 'master']
        if oldtrash is not None:
        self.rename_branch(branchname, trashname)
    @classmethod
    def is_atomic_name(x):
        r"""
        returns true if x is a valid atomic branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import is_atomic_name
            sage: is_atomic_name(["branch"])
            True
            sage: is_atomic_name(["/branch"])
            False
            sage: is_atomic_name(["refs","heads","branch"])
            False
            sage: is_atomic_name([""])
            False
            sage: is_atomic_name(["u"])
            False
            sage: is_atomic_name(["1234"])
            True
        """
        if len(x) != 1:
            return False
        if '/' in x[0]:
            return False
        return x[0] not in ("t", "ticket", "u", "g", "abandoned","")

    @classmethod
    def is_ticket_name(x):
        r"""
        returns true if x is a valid ticket branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import is_ticket_name
            sage: is_ticket_name(["t", "1234"])
            True
            sage: is_ticket_name(["u", "doctest", "branch"])
            False
            sage: is_ticket_name(["padics", "feature"])
            False
            sage: is_ticket_name(["ticket", "myticket"])
            False
            sage: is_ticket_name(["ticket", "9876"])
            True
        """
        if len(x) != 2:
            return False
        if x[0] not in ('ticket', 't'):
            return False
        return x[1].isdigit()

    @classmethod
    def is_local_group_name(x):
        r"""
        returns true if x is a valid local group branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import is_local_group_name
            sage: is_local_group_name(["padic", "feature"])
            True
            sage: is_local_group_name(["g", "padic", "feature"])
            False
            sage: is_local_group_name(["padic", "feature", "1234"])
            False
            sage: is_local_group_name(["padic", "ticket", "1234"])
            True
        """
        if len(x) == 0:
            return False
        if not is_atomic_name(x[0:1]):
            return False
        if len(x) == 2:
            return is_atomic_name(x[1:])
        else:
            return is_ticket_name(x[1:])

    @classmethod
    def is_remote_group_name(x):
        r"""
        returns true if x is a valid remote group branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import is_remote_group_name
            sage: is_remote_group_name(["padic", "feature"])
            False
            sage: is_remote_group_name(["g", "padic", "feature"])
            True
            sage: is_remote_group_name(["g", "padic", "feature", "1234"])
            False
            sage: is_remote_group_name(["g", "padic", "ticket", "1234"])
            True
            sage: is_remote_group_name(["u", "doctest", "ticket", "1234"])
            False
        """
        if len(x) < 3:
            return False
        if x[0] != "g":
            return False
        return is_local_group_name(x[1:])

    @classmethod
    def is_remote_user_name(x):
        r"""
        returns true if x is a valid remote user branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import is_remote_user_name
            sage: is_remote_user_name(["u", "doctest", "ticket", "12345"])
            True
            sage: is_remote_user_name(["u", "doctest", "ticket", ""])
            False
            sage: is_remote_user_name(["u", "doctest"])
            False
            sage: is_remote_user_name(["g", "padic", "feature"])
            False
            sage: is_remote_user_name(["u", "doctest", "feature"])
            True
        """
        if len(x) < 3:
            return False
        if x[0] != "u":
            return False
        return all(x[1:])

    @classmethod
    def is_release_name(x):
        r"""
        returns true if x is a valid release name

        WARNING: this does not imply the existence of such a release

        EXAMPLES::

            sage: from sage.dev.git_interface import is_release_name
            sage: is_release_name(['5', '2', '7'])
            True
            sage: is_release_name(['6', '-2'])
            False
            sage: is_release_name(['6', 'beta0'])
            True
            sage: is_release_name(['7', 'rc'])
            False
            sage: is_release_name(['7', 'rc1'])
            True
        """
        for v in x[:-1]:
            try:
                if int(v) < 0:
                    return False
            except ValueError:
                return False
        v = x[-1]
        if v.startswith('alpha'):
            v = v[5:]
        elif v.startswith('beta'):
            v = v[4:]
        elif v.startswith('rc'):
            v = v[2:]
        try:
            return int(v) >= 0
        except ValueError:
            return False

    @classmethod
    def normalize_ticket_name(x):
        r"""
        returns the normalized ticket branch name for x

        WARNING: it does not check to see if x is a valid ticket branch name

        EXAMPLES::

            sage: from sage.dev.git_interface import normalize_ticket_name
            sage: normalize_ticket_name(["t", "12345"])
            'ticket/12345'
            sage: normalize_ticket_name(["cow", "goes", "moo"])
            'ticket/goes'
            sage: normalize_ticket_name(["branch"])
            Traceback (most recent call last):
            ...
            IndexError: list index out of range
        """
        return '/'.join(('ticket', x[1]))

def _git_cmd_wrapper(git_cmd):
    r"""
    creates a method for GitInterface that wraps a git command

    EXAMPLES::

        sage: from sage.dev.git_interface import _git_cmd_wrapper, GitInterface
        sage: cmd = _git_cmd_wrapper("ls-tree")
        sage: setattr(GitInterface, 'ls_tree', cmd)
        sage: r = dev.git.ls_tree('first_branch')
        100644 blob 13d5431ac2f249eb07313624ec8fa041ea0f34a4        testfile
        sage: r
        0
    """
    def meth(self, *args, **kwds):
        self.execute(git_cmd.replace("_", "-"), *args, **kwds)
    meth.__doc__ = r"""
            direct call to \`git %s\`

            see :meth:`execute` for full documentation
            """%git_cmd
    return meth

for git_cmd in (
        "add",
        "am",
        "apply",
        "bisect",
        "branch",
        "checkout",
        "clean",
        "clone",
        "commit",
        "diff",
        "fetch",
        "format_patch",
        "grep",
        # "init",
        "log",
        "merge",
        "mv",
        "pull",
        "push",
        "rebase",
        "reset",
        "rm",
        "show",
        "stash",
        "status",
        # "tag"
        ):
    setattr(GitInterface, git_cmd, _git_cmd_wrapper(git_cmd))

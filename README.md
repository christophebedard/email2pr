# email2pr

Open a GitHub PR by sending a patch file by email.

[![Build Status](https://travis-ci.org/christophebedard/email2pr.svg?branch=master)](https://travis-ci.org/christophebedard/email2pr)

## Prereqs

```shell
$ pip3 install --trusted-host pypi.python.org -r requirements.txt
```

## Setup

We'll need a couple things.

1. Email account access to send your patches.

    Add [information for `git send-email`](https://git-scm.com/docs/git-send-email#_examples) to your `.gitconfig` file. For Gmail, you can easily generate an [app password](https://myaccount.google.com/apppasswords). Under *Select app*, click *Other (custom name)* and simply enter something like *email2pr*.
    ```
    [sendemail]
        smtpEncryption = tls
        smtpServer = smtp.gmail.com
        smtpUser = 
        smtpPass = 
        smtpServerPort = 587
    ```

2. Email account access to receive patches.

    This is the email address we'll send our `git` patches to. You can use the same email address and application password generated above, or you can use another email address.

    You also need to know the host and port to connect to the IMAP4 server over SSL. Default values are provided for Gmail, so no need to worry about this if you're using Gmail.

3. GitHub account access to create pull requests.

    Generate a [personal access token](https://github.com/settings/tokens). Under *Note*, you can again enter something like *email2pr*. Under *Select scopes*, you'll need to check at least *public_repo*, but you might want to simply check *repo* if you want this to work with your private repos).

## Parameters file

Once you've gathered the necessary information, it's time to create your `params.yaml` file.

```yaml
# Email account username (email address)
email_user:
# Email account password (generated app password)
email_pass:
# GitHub username for pushing changes and creating pull requests
repo_user:
# GitHub token (generated personal access token)
repo_token:
# Directory to use for cloning repos (optional, default: /tmp/email2pr)
repo_dir: /tmp/email2pr
```

You can also define `email_host` and `email_port` if you don't want to use the default Gmail values.

## How to use

First, launch `email2pr` in the root directory of this repository.
```shell
$ ./email2pr.py
```

Every time you want to create a pull request:

1. Do your changes and commit.

    Include the corresponding GitHub repo URL on the third line of your commit message. The `.git` suffix is optional.

    ```shell
    $ git add your/file
    $ git commit -m "Do some changes<enter>
    $ <enter>
    $ Repo-Url: https://github.com/username-or-org/repo"
    ```

2. Create your patch file and send it.

    For example, create a patch file from your last commit and then send it.
    ```shell
    $ git format-patch -1
    $ git send-email --to=emailaddress@gmail.com *.patch
    ```

## Current limitations

* Does not support creating a PR from multiple patches/emails.
* No feedback after sending the patch by email (unless you have access to the `email2pr` output directly).

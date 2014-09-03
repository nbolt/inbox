# -*- coding: utf-8 -*-
# base.py: Basic functions for end-to-end testing.
#
# Here's how testing works. The tests for a specific REST resource
# are in test_resource.py. Each file contains one or more test class
# which inherits E2ETest, and an additional mixin class.
#
# For instance, if you want to define a test which will run against
# a gmail account, you test class will inherit E2ETest and GmailMixin.
from time import time, sleep
from inbox.auth import handler_from_email
from inbox.util.url import provider_from_address
from inbox.models.session import session_scope
from conftest import (passwords, TEST_MAX_DURATION_SECS,
                      TEST_GRANULARITY_CHECK_SECS)
from google_auth_helper import google_auth
from outlook_auth_helper import outlook_auth
from inbox.auth.gmail import create_auth_account as create_gmail_account
from inbox.auth.outlook import create_auth_account as create_outlook_account
from client import InboxTestClient


def for_all_available_providers(fn):
    """Run a test on all providers defined in accounts.py. This function
    handles account setup and teardown."""
    def f(*args, **kwargs):
        for email, password in passwords:
            with session_scope() as db_session:
                create_account(db_session, email, password)

            client = None
            _client = InboxTestClient(email)
            start_time = time()
            while time() - start_time < TEST_MAX_DURATION_SECS:
                sleep(TEST_GRANULARITY_CHECK_SECS)
                namespaces = _client.namespaces.all()
                if len(namespaces):
                    client = _client
                    client.provider = namespaces[0]['provider']
                    break

            assert client, ("Failed to create account in {} secs."
                            .format(TEST_MAX_DURATION_SECS))
            format_test_result("namespace_creation_time", client.provider,
                               email, start_time)

            # wait a little time for the sync to start. It's necessary
            # because a lot of tests rely on stuff setup at the beginning
            # of the sync (for example, a folder hierarchy).
            start_time = time()
            sync_started = False
            while time() - start_time < TEST_MAX_DURATION_SECS:
                msgs = client.messages
                if len(msgs) > 0:
                    sync_started = True
                    break
                sleep(TEST_GRANULARITY_CHECK_SECS)

            assert sync_started, ("The initial sync should have started")

            start_time = time()
            fn(client, *args, **kwargs)
            format_test_result(fn.__name__, provider, email, start_time)

            with session_scope() as db_session:
                # delete account
                pass

    return f


def create_account(db_session, email, password):
    provider = provider_from_address(email)
    auth_handler = handler_from_email(email)
    # Special-case Gmail and Outlook, because we need to provide an oauth token
    # and not merely a password.
    if provider == 'gmail':
        token = google_auth(email, password)
        account = create_gmail_account(db_session, email, token, False)
    elif provider == 'outlook':
        token = outlook_auth(email, password)
        account = create_outlook_account(db_session, email, token, False)
    else:
        response = {"email": email, "password": password}
        account = auth_handler.create_account(db_session, email, response)

    auth_handler.verify_account(account)

    db_session.add(account)
    db_session.commit()
    return account


def format_test_result(function_name, provider, email, start_time):
    print "%s\t%s\t%s\t%f" % (function_name, provider,
                              email, time.time() - start_time)

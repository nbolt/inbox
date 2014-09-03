# -*- coding: utf-8 -*-
import pytest
from time import time, sleep
from base import for_all_available_providers, format_test_result
from conftest import TEST_MAX_DURATION_SECS, TEST_GRANULARITY_CHECK_SECS


@for_all_available_providers
def test_sending(client):
    # Let's send a message to ourselves and check that it arrived.

    subject = "Test email from Inbox - %s" % time.strftime("%H:%M:%S")
    message = {"to": [{"email": client.email_address}],
               "body": "This is a test email, disregard this.",
               "subject": subject}

    client.send_message(message)

    start_time = time()
    found_email = False
    while time() - start_time < TEST_MAX_DURATION_SECS:
        sleep(TEST_GRANULARITY_CHECK_SECS)
        threads = client.threads.where(subject=subject)
        if len(threads) != 2:
            continue

        tags = [t.name for thread in threads for t in thread.tags]
        if ("sent" in tags and "inbox" in tags):
            format_test_result("self_send_test", client.provider,
                               client.email_address, start_time)
            found_email = True
            break

    assert found_email, ("Failed to self send an email in less"
                         "than {} seconds on account: {}"
                         .format(TEST_MAX_DURATION_SECS,
                                 client.email_address))

    # Now let's archive the email.

    threads = client.threads.where(subject=subject)
    # Note: this uses python's implicit scoping
    for thread in threads:
        if "inbox" in thread.tags:
            break

    threads.first().archive()

    updated_tags = False
    start_time = time()
    while time() - start_time < TEST_MAX_DURATION_SECS:
        sleep(TEST_GRANULARITY_CHECK_SECS)
        thr = client.threads.find(thread.id)

        tags = [tag.name for tag in thr.tags]
        if "archive" in tags and "inbox" not in tags:
            format_test_result("archive_test", client.provider,
                               client.email_address, start_time)
            updated_tags = True
            break

    assert updated_tags, ("Failed to archive an email in less"
                         "than {} seconds on account: {}"
                         .format(TEST_MAX_DURATION_SECS,
                                 client.email_address))

    threads.first().trash()

    updated_tags = False
    start_time = time()
    while time() - start_time < TEST_MAX_DURATION_SECS:
        sleep(TEST_GRANULARITY_CHECK_SECS)
        thr = client.get_thread(thread.id)

        if "trash" in thr.tags and "archive" not in thr.tags:
            format_test_result("move_to_trash_test", client.provider,
                               client.email_address, start_time)
            updated_tags = True
            break

    assert updated_tags, ("Failed to move an email to trash in less"
                         "than {} seconds on account: {}"
                         .format(TEST_MAX_DURATION_SECS,
                                 client.email_address))


if __name__ == '__main__':
    pytest.main([__file__])

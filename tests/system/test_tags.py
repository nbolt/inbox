# -*- coding: utf-8 -*-
import pytest
import random
import time
import datetime
import requests.exceptions
from inbox.client.errors import NotFoundError
from base import for_all_available_providers, timeout_loop
from conftest import TEST_MAX_DURATION_SECS, TEST_GRANULARITY_CHECK_SECS


@timeout_loop('tags')
def wait_for_tag(client, thread_id, tagname):
    try:
        thread = client.namespaces[0].threads.find(thread_id)
        tags = [tag['name'] for tag in threads.tags]
        return True if tagname in tags
    except NotFoundError:
        return False


@for_all_available_providers
def test_read_status(client):
    # toggle a thread's read status
    messages = client.namespaces[0].messages.all()
    msg = random.choice(messages)
    unread = msg.unread
    thread = msg.thread

    if unread:
        thread.update_tags(add=["read"])
        wait_for_tag(client, thread.id, "read")
    else:
        thread.update_tags(add=["unread"])
        wait_for_tag(client, thread.id, "unread")


@for_all_available_providers
def test_custom_tag(client):
    threads = client.namespaces[0].threads.all()
    thread = random.choice(threads)
    tagname = "custom-tag" + datetime.datetime.now().strftime("%s.%f")
    thread.update_tags(add=[tagname])
    wait_for_tag(client, thread.id, tagname)


if __name__ == '__main__':
    pytest.main([__file__])

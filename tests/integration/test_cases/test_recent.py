import unittest
import os
import random
import time

import pytest

from . import utils
import kloudless


@pytest.fixture(params=[acc for acc in utils.accounts])
def account(request):
    return request.param


class TestRecent:

    def create_test_files(self, acc):
        self.test_file_1 = utils.create_test_file(acc)
        self.test_file_2 = utils.create_test_file(acc)

    def test_retrieve_recent(self, account):
        self.create_test_files(account)
        time.sleep(0.5)
        results = account.recent.all()
        for i in range(len(results) - 1):
            if results[i].modified and results[i+1].modified:
                assert results[i].modified > results[i+1].modified

    def test_recent_page_size(self, account):
        self.create_test_files(account)
        results = account.recent.all(page_size=1)
        assert len(results) == 1

    def test_bad_recent_page_size(self, account):
        self.create_test_files(account)
        try:
            account.recent.all(page_size=1001)
        except kloudless.exceptions.APIException:
            pass

    def test_simple_recent_page(self, account):
        self.create_test_files(account)
        acc = account
        test_file_3 = utils.create_test_file(acc)
        time.sleep(0.5)
        results = acc.recent.all(page_size=1, page=1)
        assert len(results) == 1

        # Subject to race conditions.
        results = acc.recent.all()
        assert test_file_3.id in [r.id for r in results]

    def test_complex_recent_page(self, account):
        self.create_test_files(account)
        acc = account
        files = {}
        for i in range(1, 6):
            files['test_file_{0}'.format(i)] = utils.create_test_file(acc)
        time.sleep(0.5)
        results = acc.recent.all(page_size=3, page=1)
        assert len(results) == 3

        # Subject to race conditions
        assert results[0].id == files['test_file_5'].id
        assert results[1].id == files['test_file_4'].id
        assert results[2].id == files['test_file_3'].id

        results = acc.recent.all(page_size=1, page=5)
        assert results[0].id == files['test_file_1'].id

    def test_bad_recent_page(self, account):
        self.create_test_files(account)
        try:
            account.recent.all(page_size=1, page=0)
        except kloudless.exceptions.APIException:
            pass

    def test_outofbounds_recent_page(self, account):
        self.create_test_files(account)
        length = account.recent.all().total
        try:
            account.recent.all(page_size=1, page=length+1)
        except kloudless.exceptions.APIException:
            pass

    def test_bad_after_timestamp(self, account):
        self.create_test_files(account)
        assert account.recent.all(after="00/00/00") == []

    def test_after_timestamp(self, account):
        self.create_test_files(account)
        acc = account
        test_file_4 = utils.create_test_file(acc)
        after = test_file_4.modified
        test_file_5 = utils.create_test_file(acc)
        time.sleep(2)
        results = acc.recent.all(after=after)
        assert test_file_4.id not in [r.id for r in results]
        assert results[0].modified >= after

        results = acc.recent.all(after=test_file_5.modified)
        assert test_file_5.id not in [r.id for r in results]

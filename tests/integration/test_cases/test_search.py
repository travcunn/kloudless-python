import unittest
import os
import base64
import random
import time

import pytest

from . import utils
import kloudless


@pytest.fixture(params=[acc for acc in utils.accounts])
def account(request):
    return request.param


class TestSearch:

    @utils.skip_long_test(services=['box'])
    def test_simple_search(self, account):
        acc = account
        test_file_name = 'search' + str(random.random())[2:] + '.txt'
        test_file = utils.create_test_file(acc, file_name=test_file_name)
        if acc.service == 'box':
            time.sleep(210)
        results = acc.search.all(q=test_file_name)
        assert results > 0
        assert results[0].id == test_file.id

    def test_bad_search(self, account):
        q = base64.b64encode(os.urandom(40))
        assert account.search.all(q=q) == []

    def test_empty_str_search(self, account):
        try:
            account.search.all(q='')
        except kloudless.exceptions.APIException:
            pass

    @utils.skip_long_test(services=['box'])
    def test_mult_results_search(self, account):
        acc = account
        test_file_name = 'search' + str(random.random())[2:] + '.txt'
        root_folder = utils.create_or_get_test_folder(acc)
        test_folder_1 = acc.folders.create(data={
            'parent_id': root_folder.id,
            'name': 'folder %s' % random.randint(0, 10e8)})
        test_folder_2 = acc.folders.create(data={
            'parent_id': root_folder.id,
            'name': 'folder %s' % random.randint(0, 10e8)})
        test_file_1 = utils.create_test_file(acc, folder=test_folder_1,
                                             file_name=test_file_name)
        test_file_2 = utils.create_test_file(acc, folder=test_folder_2,
                                             file_name=test_file_name)
        if acc.service == 'box':
            time.sleep(210)
        results = acc.search.all(q=test_file_name)
        set1 = {results[0].id, results[1].id}
        set2 = {test_file_1.id, test_file_2.id}
        assert set1 == set2

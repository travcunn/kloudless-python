import unittest
import os
import random
import json
import time

import pytest

from . import utils
import kloudless


@pytest.fixture(params=[acc for acc in utils.accounts])
def account(request):
    return request.param


class TestFile:

    def create_test_files(self, acc):
        self.folder = utils.create_or_get_test_folder(acc)
        self.file = utils.create_test_file(acc)

    def test_create_file(self, account):
        # CREATE
        self.create_test_files(account)

        assert self.file.account == account.id
        new_file = utils.create_test_file(account, file_data='test data1',
                                          overwrite=False)
        assert self.file.name != new_file.name
        new_file = utils.create_test_file(account, file_data='test data2',
                                          file_name=self.file.name, overwrite=True)
        assert self.file.name == new_file.name

    def test_read_file(self, account):
        # Read
        self.create_test_files(account)
        read_file = account.files.retrieve(self.file.id)
        assert hasattr(read_file, 'id')
        assert hasattr(read_file, 'name')
        assert hasattr(read_file, 'size')
        assert hasattr(read_file, 'created')
        assert hasattr(read_file, 'modified')
        assert read_file.type == 'file'
        assert hasattr(read_file, 'account')
        assert hasattr(read_file, 'parent')
        assert hasattr(read_file, 'ancestors')
        assert hasattr(read_file, 'path')
        assert hasattr(read_file, 'mime_type')
        assert hasattr(read_file, 'downloadable')

    def test_rename_file(self, account):
        # Rename, Move and Copy
        self.create_test_files(account)
        new_name = 'renamed %s' % self.file.name
        self.file.name = new_name
        assert self.file.save()
        assert self.file.name == new_name
        assert self.file.account == account.id

    def test_move_file(self, account):
        self.create_test_files(account)
        new_name = 'moved %s' % self.file.name
        folder1 = account.folders.create(
            data={'parent_id': self.folder.id,
                  'name': 'folder %s' % random.randint(0, 10e10)})
        assert utils.is_folder_present(folder1.name, self.folder)
        self.file.parent_id = folder1.id
        self.file.name = new_name
        assert self.file.name == new_name
        assert self.file.save()
        assert not utils.is_file_present(self.file.name, self.folder)
        assert utils.is_file_present(self.file.name, folder1)

    def test_copy_file(self, account):
        self.create_test_files(account)
        new_name = 'copied %s' % self.file.name
        folder1 = account.folders.create(
            data={'parent_id': self.folder.id,
                  'name': 'folder %s' % random.randint(0, 10e10)})
        assert utils.is_folder_present(folder1.name, self.folder)
        new_file = self.file.copy_file(parent_id=folder1.id, name=new_name)
        assert new_file
        assert new_file.name == new_name
        assert utils.is_file_present(self.file.name, self.folder)
        assert utils.is_file_present(new_file.name, folder1)

    def test_put_file(self, account):
        # Update [update contents]
        self.create_test_files(account)
        self.file.update(file_data='hello there')
        assert self.file.contents().text == 'hello there'

    def test_delete_file(self, account):
        # Delete
        self.create_test_files(account)
        try:
            self.file.delete(permanent=True)
            read_file = account.files.retrieve(self.file.id)
        except kloudless.exceptions.KloudlessException as e:
            error_data = json.loads(str(e).split('Error data: ')[1])
            assert error_data['status_code'] == 404

    def test_properties(self, account):

        if account.service not in ['box', 'egnyte', 'gdrive']:
            return

        self.create_test_files(account)
        def parse(properties):
            result = {}
            for prop in properties['properties']:
                result[prop['key']] = prop['value']
            return result

        self.file.properties.delete_all()
        # Test PATCH
        time.sleep(0.5)
        properties = self.file.properties.update(data=[
            {
                'key': 'key1',
                'value': 'value1'
            },
            {
                'key': 'key2',
                'value': 'value2'
            }
        ])

        properties = parse(properties)
        assert len(properties) == 2
        assert properties['key1'] == 'value1'
        assert properties['key2'] == 'value2'

        time.sleep(0.5)
        self.file.properties.update(data=[
            {
                'key': 'key1', # delete property
                'value': None
            },
            {
                'key': 'key2', # update property
                'value': 'hello'
            },
            {
                'key': 'key3', # add property
                'value': 'value3'
            }
        ])

        # Test GET
        time.sleep(0.5)
        properties = parse(self.file.properties.all())
        assert len(properties) == 2
        assert properties['key2'] == 'hello'
        assert properties['key3'] == 'value3'

        # Test DELETE
        self.file.properties.delete_all()
        time.sleep(0.5)
        properties = parse(self.file.properties.all())
        assert len(properties) == 0

    def test_upload_url(self, account):
        if account.service in ['onedrive', 'onedrivebiz', 'sharepoint']:
            return
        self.create_test_files(account)
        contents = account.folders().contents()
        name = 'test_file_name'
        if contents:
            obj = contents[0]
            data = {}
            data['parent_id'] = obj.id
            data['name'] = name
            response = account.files.upload_url(data=data)
            assert 'url' in response

import unittest
import os

import pytest

from tests.integration.test_cases import utils
import sdk


@pytest.fixture(params=[acc for acc in utils.accounts])
def account(request):
    return request.param


class TestUsers:

    def not_admin(self, account):
        return not account.admin

    def test_list_users(self, account):

        users = account.users.all()

        if self.not_admin(account):
            return
        assert users
        assert len(users) > 0
        for user in users:
            assert isinstance(user, sdk.resources.User)

    def test_retrieve_user(self, account):

        users = account.users.all()

        if self.not_admin(account):
            return

        user = account.users.retrieve(users[0].id)
        assert type(user) == sdk.resources.User
        assert user.id == users[0].id

    def test_user_membership(self, account):

        users = account.users.all()

        if self.not_admin(account):
            return

        for user in users:
            groups = user.get_groups()
            for group in groups:
                assert isinstance(group, sdk.resources.Group)

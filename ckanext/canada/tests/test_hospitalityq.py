# -*- coding: UTF-8 -*-
from nose.tools import assert_equal, assert_raises
from ckanapi import LocalCKAN, ValidationError

import pytest
from ckanext.canada.tests.factories import CanadaOrganization as Organization

from ckanext.recombinant.tables import get_chromo

@pytest.mark.usefixtures('clean_db')
class TestHospitalityQ(object):
    def __init__(self):
        org = Organization()
        lc = LocalCKAN()
        lc.action.recombinant_create(dataset_type='hospitalityq', owner_org=org['name'])
        rval = lc.action.recombinant_show(dataset_type='hospitalityq', owner_org=org['name'])
        self.resource_id = rval['resources'][0]['id']

    def test_example(self):
        lc = LocalCKAN()
        record = get_chromo('hospitalityq')['examples']['record']
        lc.action.datastore_upsert(
            resource_id=self.resource_id,
            records=[record])

    def test_blank(self):
        lc = LocalCKAN()
        assert_raises(ValidationError,
            lc.action.datastore_upsert,
            resource_id=self.resource_id,
            records=[{}])


@pytest.mark.usefixtures('clean_db')
class TestHospitalityQNil(object):
    def __init__(self):
        org = Organization()
        lc = LocalCKAN()
        lc.action.recombinant_create(dataset_type='hospitalityq', owner_org=org['name'])
        rval = lc.action.recombinant_show(dataset_type='hospitalityq', owner_org=org['name'])
        self.resource_id = rval['resources'][1]['id']

    def test_example(self):
        lc = LocalCKAN()
        record = get_chromo('hospitalityq-nil')['examples']['record']
        lc.action.datastore_upsert(
            resource_id=self.resource_id,
            records=[record])

    def test_blank(self):
        lc = LocalCKAN()
        assert_raises(ValidationError,
                      lc.action.datastore_upsert,
                      resource_id=self.resource_id,
                      records=[{}])

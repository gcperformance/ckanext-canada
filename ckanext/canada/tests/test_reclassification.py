# -*- coding: UTF-8 -*-
from nose.tools import assert_raises
from ckanapi import LocalCKAN, ValidationError

from ckanext.canada.tests.factories import CanadaOrganization as Organization

from ckanext.recombinant.tables import get_chromo
from ckanext.canada.tests import CanadaTestBase


class TestReclassification(CanadaTestBase):
    def setup(self):
        super(TestReclassification, self).setup()
        org = Organization()
        self.lc = LocalCKAN()
        self.lc.action.recombinant_create(dataset_type='reclassification', owner_org=org['name'])
        rval = self.lc.action.recombinant_show(dataset_type='reclassification', owner_org=org['name'])
        self.resource_id = rval['resources'][0]['id']


    def test_example(self):
        record = get_chromo('reclassification')['examples']['record']
        self.lc.action.datastore_upsert(
            resource_id=self.resource_id,
            records=[record])


    def test_blank(self):
        assert_raises(ValidationError,
            self.lc.action.datastore_upsert,
            resource_id=self.resource_id,
            records=[{}])


class TestReclassificationNil(CanadaTestBase):
    def setup(self):
        super(TestReclassificationNil, self).setup()
        org = Organization()
        self.lc = LocalCKAN()
        self.lc.action.recombinant_create(dataset_type='reclassification', owner_org=org['name'])
        rval = self.lc.action.recombinant_show(dataset_type='reclassification', owner_org=org['name'])
        self.resource_id = rval['resources'][1]['id']


    def test_example(self):
        record = get_chromo('reclassification-nil')['examples']['record']
        self.lc.action.datastore_upsert(
            resource_id=self.resource_id,
            records=[record])


    def test_blank(self):
        assert_raises(ValidationError,
                      self.lc.action.datastore_upsert,
                      resource_id=self.resource_id,
                      records=[{}])


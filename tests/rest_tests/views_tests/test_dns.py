# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db.models import Q

import rest.models
from lib import WsFaker
from tests.rest_tests.base import WsDjangoViewTestCase
from tests.rest_tests.mixin import ListTestCaseMixin, PresentableTestCaseMixin, ExporterCustomFieldsMixin, \
    ExporterTestCaseMixin, RetrieveTestCaseMixin, DeleteTestCaseMixin, CustomFieldsMixin, ParameterizedRouteMixin


class TestDnsRecordTypeListView(
    ListTestCaseMixin,
    PresentableTestCaseMixin,
    ExporterCustomFieldsMixin,
    ExporterTestCaseMixin,
    WsDjangoViewTestCase,
):
    """
    This is a test case for testing the DnsRecordTypeListView APIView.
    """

    _api_route = "/dns-record-types/"

    def __send_list_request(self, user="user_1", query_string=None, login=True):
        """
        Send an HTTP request to the configured API endpoint and return the response.
        :param user: A string depicting the user to send the request as.
        :param query_string: The query string to include in the URL.
        :param login: Whether or not to log the requesting user in.
        :return: The HTTP response.
                """
        if login:
            self.login(user=user)
        return self.get(query_string=query_string)

    def test_regular_user_list(self):
        """
        Tests that requesting the endpoint on behalf of a regular user returns the expected
        number of results.
        :return: None
        """
        response = self.__send_list_request(user="user_1")
        user = self.get_user(user="user_1")
        total_count = rest.models.DnsRecordType.objects\
            .filter(
                Q(scan_config__user=user) |
                Q(scan_config__is_default=True) |
                Q(
                    scan_config__organization__auth_groups__users=user,
                    scan_config__organization__auth_groups__name="org_read",
                )
            ).count()
        self.assertEqual(response.json()["count"], total_count)

    def test_admin_user_list(self):
        """
        Tests that requesting the endpoint on behalf of an admin user returns the expected
        number of results.
        :return: None
        """
        response = self.__send_list_request(user="admin_1")
        total_count = rest.models.DnsRecordType.objects.count()
        self.assertEqual(response.json()["count"], total_count)

    @property
    def custom_fields_field(self):
        return "uuid"

    @property
    def custom_fields_method(self):
        return self.__send_list_request

    @property
    def list_method(self):
        return self.__send_list_request

    @property
    def presentation_method(self):
        return self.__send_list_request

    @property
    def response_has_many(self):
        return True


class TestDnsRecordTypeDetailView(
    RetrieveTestCaseMixin,
    DeleteTestCaseMixin,
    PresentableTestCaseMixin,
    CustomFieldsMixin,
    ParameterizedRouteMixin,
    WsDjangoViewTestCase,
):
    """
    This is a test case for testing the DnsRecordTypeDetailView APIView.
    """

    _api_route = "/dns-record-types/%s/"
    _url_parameters = None

    def create_delete_object_for_user(self, user="user_1"):
        scan_config = self.get_scan_config_for_user(user=user)
        return scan_config.dns_record_types.create(**WsFaker.get_dns_record_type_kwargs())

    def __create_default_scan_config(self):
        """
        Create and return a ScanConfig that is configured as default.
        :return: A ScanConfig configured as a default ScanConfig.
        """
        to_return = rest.models.ScanConfig.objects.create()
        to_return.is_default = True
        to_return.save()
        return to_return

    def __create_organization_for_user(self, user_string="user_1"):
        user = self.get_user(user=user_string)
        org = rest.models.Organization.objects.create(name="Name", description="Description")
        org.add_admin_user(user)
        org.save()
        return org

    def __send_delete_request(self, user="user_1", login=True, query_string=None, input_uuid="POPULATE"):
        """
        Send a delete request to the API endpoint and return the response.
        :param user: The user to submit the request as.
        :param login: Whether or not to log the user in prior to sending the request.
        :param query_string: The query string to submit alongside the URL.
        :param input_uuid: The UUID of the organization to delete.
        :return: The HTTP response.
        """
        if login:
            self.login(user=user)
        if input_uuid == "POPULATE":
            order = self.get_dns_record_type_for_user(user=user)
            input_uuid = str(order.uuid)
        self._url_parameters = str(input_uuid)
        return self.delete(query_string=query_string)

    def __send_retrieve_request(self, user="user_1", query_string=None, login=True, input_uuid="POPULATE"):
        """
        Send an HTTP request to the configured API endpoint and return the response.
        :param user: The user to send the request as.
        :param query_string: The query string to include in the URL.
        :param login: Whether or not to log in before sending the request.
        :param input_uuid: The UUID of the order to retrieve.
        :return: The HTTP response.
        """
        if login:
            self.login(user=user)
        if input_uuid == "POPULATE":
            order = self.get_dns_record_type_for_user(user=user)
            input_uuid = str(order.uuid)
        self._url_parameters = input_uuid
        return self.get(query_string=query_string)

    def test_delete_regular_is_default_fails(self):
        """
        Tests that attempting to delete a DnsRecordType from an is_default ScanConfig as a regular user fails.
        :return: None
        """
        default_config = self.__create_default_scan_config()
        response = self.__send_delete_request(user="user_1", input_uuid=default_config.dns_record_types.first().uuid)
        default_config.delete()
        self.assert_request_not_authorized(response)

    def test_delete_admin_is_default_succeeds(self):
        """
        Tests that attempting to delete a DnsRecordType from an is_default ScanConfig as an admin user succeeds.
        :return: None
        """
        default_config = self.__create_default_scan_config()
        response = self.__send_delete_request(user="admin_1", input_uuid=default_config.dns_record_types.first().uuid)
        default_config.delete()
        self.assert_request_succeeds(response, status_code=204)

    def test_retrieve_regular_is_default_succeeds(self):
        """
        Tests that attempting to retrieve a DnsRecordType from an is_default ScanConfig as a regular user succeeds.
        :return: None
        """
        default_config = self.__create_default_scan_config()
        response = self.__send_retrieve_request(user="user_1", input_uuid=default_config.dns_record_types.first().uuid)
        default_config.delete()
        self.assert_request_succeeds(response)

    def test_retrieve_admin_is_default_succeeds(self):
        """
        Tests that attempting to retrieve a DnsRecordType from an is_default ScanConfig as an admin user succeeds.
        :return: None
        """
        default_config = self.__create_default_scan_config()
        response = self.__send_retrieve_request(user="admin_1", input_uuid=default_config.dns_record_types.first().uuid)
        default_config.delete()
        self.assert_request_succeeds(response)

    def test_regular_user_delete_cant_be_modified_fails(self):
        """
        Tests that attempting to delete a DnsRecordType from a ScanConfig that the requesting user owns as a regular
        user fails when the ScanConfig cannot be modified.
        :return: None
        """
        scan_config = self.get_scan_config_for_user(user="user_1")
        scan_config.order.has_been_placed = True
        scan_config.order.save()
        response = self.__send_delete_request(input_uuid=scan_config.dns_record_types.first().uuid, user="user_1")
        scan_config.order.has_been_placed = False
        scan_config.order.save()
        self.assert_request_not_authorized(response)

    def test_admin_user_delete_cant_be_modified_fails(self):
        """
        Tests that attempting to delete a DnsRecordType from a ScanConfig that the requesting user owns as an admin
        user fails when the ScanConfig cannot be modified.
        :return: None
        """
        scan_config = self.get_scan_config_for_user(user="admin_1")
        scan_config.order.has_been_placed = True
        scan_config.order.save()
        response = self.__send_delete_request(input_uuid=scan_config.dns_record_types.first().uuid, user="admin_1")
        scan_config.order.has_been_placed = False
        scan_config.order.save()
        self.assert_request_not_authorized(response)

    def test_delete_as_org_admin_succeeds(self):
        """
        Tests that deleting an object from a ScanConfig related to an organization that the requesting
        user has administrative permissions for succeeds.
        :return: None
        """
        org = self.__create_organization_for_user(user_string="user_1")
        scan_config = org.scan_config
        dns_record = scan_config.dns_record_types.first()
        response = self.__send_delete_request(input_uuid=dns_record.uuid, user="user_1")
        org.delete()
        self.assert_request_succeeds(response, status_code=204)

    def test_delete_as_not_org_admin_fails(self):
        """
        Tests that deleting an object from a ScanConfig related to an organization that the requesting user
        does not have administrative permissions for fails.
        :return: None
        """
        org = self.__create_organization_for_user(user_string="user_1")
        user = self.get_user(user="user_1")
        org.set_user_permissions(user=user, permission_level="write")
        scan_config = org.scan_config
        dns_record = scan_config.dns_record_types.first()
        response = self.__send_delete_request(input_uuid=dns_record.uuid, user="user_1")
        org.delete()
        self.assert_request_not_authorized(response)

    def test_delete_as_not_org_admin_superuser_succeeds(self):
        """
        Tests that deleting an object from a ScanConfig related to an organization that the requesting user
        does not have administrative permissions for succeeds when the requesting user is a superuser.
        :return: None
        """
        org = self.__create_organization_for_user(user_string="user_1")
        scan_config = org.scan_config
        dns_record = scan_config.dns_record_types.first()
        response = self.__send_delete_request(input_uuid=dns_record.uuid, user="admin_1")
        org.delete()
        self.assert_request_succeeds(response, status_code=204)

    @property
    def custom_fields_field(self):
        return "uuid"

    @property
    def custom_fields_method(self):
        return self.__send_retrieve_request

    @property
    def delete_method(self):
        return self.__send_delete_request

    @property
    def deleted_object_class(self):
        return rest.models.DnsRecordType

    @property
    def presentation_method(self):
        return self.__send_retrieve_request

    @property
    def response_has_many(self):
        return False

    @property
    def retrieve_method(self):
        return self.__send_retrieve_request

    @property
    def retrieved_object_class(self):
        return rest.models.DnsRecordType

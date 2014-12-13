import unittest
import json
import privacyideautils.clientutils as clientutils
from privacyideautils.clientutils import PrivacyIDEAClientError


PWFILE = "/home/cornelius/src/flask/tests/testdata/passwords"

class TestClientUtils(unittest.TestCase):

    serial1 = "S1"
    reso1 = "reso1"
    realm1 = "realm1"

    @classmethod
    def setUpClass(cls):
        cls.client = clientutils.privacyideaclient("user",
                                                   "pass",
                                                   "http://localhost:5000")

    def _delete_resolver(self):
        try:
            # delete the realm of the resolver
            response = self.client.deleterealm(self.realm1)
            self.assertTrue(response.status == 200, response)
        except:
            pass

        try:
            # delete the resolver if it exist
            response = self.client.deleteresolver(self.reso1)
            self.assertTrue(response.status == 200, response)
        except:
            pass

    def test_00_delete(self):
        # Cleanup in case the token database of the server contains old
        # remnants
        try:
            # delete the token, if it exist
            response = self.client.deletetoken(self.serial1)
            self.assertTrue(response.status == 200, response)
            result = response.data.get("result")
            self.assertTrue(result.get("status") is True, result)
        except PrivacyIDEAClientError:
            pass

        self._delete_resolver()

    def test_01_init_token(self):
        response = self.client.inittoken({"serial": self.serial1,
                                          "genkey": 1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(result.get("value") is True, result)

    def test_02_list_token(self):
        response = self.client.listtoken({})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("count") == 1, value)
        self.assertTrue(value.get("tokens")[0].get("serial") == self.serial1,
                        value)
        self.assertTrue(value.get("tokens")[0].get("active") is True,
                        value)

    def test_03_disable_enable_token(self):
        response = self.client.disabletoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % result)

        # disable the same token again returns 0
        response = self.client.disabletoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 0, "%r" % value)

        # check in list
        response = self.client.listtoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("count") == 1, value)
        self.assertTrue(value.get("tokens")[0].get("active") is False,
                        value)

        # enable the token again returns 1
        response = self.client.enabletoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

        # check in list
        response = self.client.listtoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("count") == 1, value)
        self.assertTrue(value.get("tokens")[0].get("active") is True,
                        value)

    def test_04_get_setresolver(self):

        # missing parameter "resolver" raises client error
        self.assertRaises(PrivacyIDEAClientError, self.client.setresolver, {})

        # missing type raises client error
        self.assertRaises(PrivacyIDEAClientError, self.client.setresolver,
                          {"resolver": self.reso1})

        # unknown resolver type
        self.assertRaises(PrivacyIDEAClientError, self.client.setresolver,
                          {"resolver": self.reso1,
                           "type": "unknown"})

        # missing rf_file for passwd raises errir
        self.assertRaises(PrivacyIDEAClientError, self.client.setresolver,
                          {"resolver": self.reso1,
                           "type": "passwd"})

        # set the resolver as a passwd resolver
        response = self.client.setresolver({"resolver": self.reso1,
                                            "type": "passwd",
                                            "filename": PWFILE})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

        # get the resolvers
        response = self.client.getresolver()
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(self.reso1 in value, "%r" % value)

        response = self.client.getresolver(self.reso1)
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(self.reso1 in value, "%r" % value)

        clientutils.showresult(value)

        # delete the resolver
        response = self.client.deleteresolver(self.reso1)
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)


    def test_05_create_a_realm(self):
        # set the resolver as a passwd resolver
        response = self.client.setresolver({"resolver": self.reso1,
                                            "type": "passwd",
                                            "filename": PWFILE})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

        # set the realm
        response = self.client.setrealm(self.realm1, {"resolvers": self.reso1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("added") == [self.reso1], "%r" % value)

        # get the realm
        response = self.client.getrealms()
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue("realm1" in value, "%r" % value)

    def test_06_userlist(self):
        # list the user
        response = self.client.userlist({"username": "*"})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        # We get a list...
        self.assertTrue(len(value) > 0, "%r" % value)

    def test_07_assign_unassign_token(self):
        # assign token
        response = self.client.assigntoken({"user": "cornelius",
                                            "realm": self.realm1,
                                            "serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)

        # check the token list
        response = self.client.listtoken({"user": "cornelius"})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("count") == 1, value)
        self.assertTrue(value.get("tokens")[0].get("user_id") == "1000", value)

        # unassign token
        response = self.client.unassigntoken({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value is True, result)

    def test_08_resynctoken(self):
        response = self.client.resynctoken({"serial": self.serial1,
                                            "otp1": "123456",
                                            "otp2": "123456"})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        # Resyncing does not work: False
        self.assertTrue(value is False, result)

    def test_09_resettoken(self):
        response = self.client.resetfailcounter({"serial": self.serial1})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        # One token resetted: 1
        self.assertTrue(value == 1, result)

    def test_10_tokenrealm(self):
        response = self.client.tokenrealm(self.serial1, self.realm1)
        self.assertTrue(response.status == 200, response)

        # test the realms of the token
        response = self.client.listtoken({})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        # One token resetted: 1
        self.assertTrue(self.realm1 in value.get("tokens")[0].get("realms"),
                        value)

        #dumpresult
        clientutils.dumpresult(result['status'], result['value']['tokens'])

    def test_11_get_set_config(self):
        response = self.client.setconfig({"key1": "value1"})
        self.assertTrue(response.status == 200, response)

        response = self.client.getconfig({})
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value.get("key1") == "value1", result)

        # delete config
        response = self.client.deleteconfig("key1")
        self.assertTrue(response.status == 200, response)

    def test_18_delete_default_realm(self):
        response = self.client.setdefaultrealm(self.realm1)
        self.assertTrue(response.status == 200, response)

        response = self.client.deletedefaultrealm()
        self.assertTrue(response.status == 200, response)

    def test_19_delete_realm_and_resolver(self):
        # delete the realm
        response = self.client.deleterealm(self.realm1)
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

        # delete the resolver
        response = self.client.deleteresolver(self.reso1)
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

    def test_20_delete_token(self):
        # delete the token S1
        response = self.client.deletetoken(self.serial1)
        self.assertTrue(response.status == 200, response)
        result = response.data.get("result")
        value = result.get("value")
        self.assertTrue(result.get("status") is True, result)
        self.assertTrue(value == 1, "%r" % value)

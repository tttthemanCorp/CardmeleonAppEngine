'''
Created on Sep 20, 2011

@author: jlu
'''
from django.test import TestCase
from django.test.client import Client
from django.db import connection
from datetime import datetime
from django.contrib.auth.models import User
import json
import base64
from api import setup_func
from server.models import UserPoint, UserReward


class ServerTest(TestCase):
    fixtures = ['testdata.json',]

    def setUp(self):
        #User.objects.create_user('testuser', 'my@test.com', 'testpassword')
        self.extra = self.getAuthorizationHeader('testuser', 'ttttheman')
        
    def getAuthorizationHeader(self, username, password):
        auth = '%s:%s' % (username, password)
        auth = 'Basic %s' % base64.encodestring(auth)
        auth = auth.strip()
        header = {
            'HTTP_AUTHORIZATION': auth,
        }
        #print auth
        return header
        
    def test_user(self):
        """
        Tests UserHandler
        """
        c = Client()
        
        '''
        {"id":2}
        '''
        response = c.get("/api/auth", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(2, r['id'], '')
        
        '''
        {"user_count":3}
        '''
        response = c.get("/api/users", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(3, r['user_count'], '')
        
        '''
        {
            "pref": {
                "nearby_radius": 40.0
            },
            "userpoint": {
                "points": 200
            }, 
            "userrewards": [
                {
                    "user": {
                        "username": "testuser", 
                        "id": 2
                    }, 
                    "reward": {
                        "status": 1, 
                        "merchant": {
                            "name": "Safeway", 
                            "id": 1,
                            "address": "434 abc ave, san jose, ca", 
                            "longitude": 201.323, 
                            "latitude": 102.454,
                            "logo": "/path/to/logo.png"
                        }, 
                        "equiv_points": 20, 
                        "name": "free bread", 
                        "expire_in_days": 0, 
                        "id": 1, 
                        "expire_in_years": 3, 
                        "equiv_dollar": "20", 
                        "expire_in_months": 0, 
                        "description": "free whole-wheet bread"
                    }, 
                    "expiration": "2012-03-12", 
                    "forsale": false
                }, 
                {
                    "user": {
                        "username": "testuser", 
                        "id": 2
                    }, 
                    "reward": {
                        "status": 1, 
                        "merchant": {
                            "name": "StarBucks", 
                            "id": 2,
                            "address": "101 abc ave, san jose, ca", 
                            "longitude": 22.323, 
                            "latitude": 44.454,
                            "logo": "/path2/to/logo.png"
                        }, 
                        "equiv_points": 10, 
                        "name": "free starbucks", 
                        "expire_in_days": 0, 
                        "id": 2, 
                        "expire_in_years": 3, 
                        "equiv_dollar": "10", 
                        "expire_in_months": 0, 
                        "description": "free one cup of starbucks coffee"
                    }, 
                    "expiration": "2012-08-20", 
                    "forsale": true
                }
            ], 
            "user": {
                "username": "testuser", 
                "first_name": "test", 
                "last_name": "user", 
                "email": "jun@cardmeleon.me"
            }, 
            "userprogresses": [
                {
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "cur_times": 2, 
                    "cur_dollar_amt": "50.25"
                }, 
                {
                    "merchant": {
                        "name": "StarBucks", 
                        "id": 2
                    }, 
                    "cur_times": 200, 
                    "cur_dollar_amt": "206.5"
                }
            ], 
            "userprofile": {
                "referer": {
                    "id": 3
                }, 
                "phone": "4082323232", 
                "facebook": null, 
                "deviceid": "abcdefg"
            }
        }
        '''
        response = c.get("/api/users/2", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(6, len(r), '')
        self.assertEqual('testuser', r['user']['username'], '')
        self.assertEqual(40.0, r['pref']['nearby_radius'], '')
        self.assertEqual('4082323232', r['userprofile']['phone'], '')
        self.assertEqual(2, r['userprogresses'][0]['cur_times'], '')
        self.assertEqual('Safeway', r['userprogresses'][0]['merchant']['name'], '')
        self.assertEqual('StarBucks', r['userprogresses'][1]['merchant']['name'], '')
        self.assertEqual(200, r['userpoint']['points'], '')
        self.assertEqual(2, len(r['userrewards']), '')
        self.assertEqual('free bread', r['userrewards'][0]['reward']['name'], '')
        self.assertEqual('Safeway', r['userrewards'][0]['reward']['merchant']['name'], '')
        self.assertEqual('/path/to/logo.png', r['userrewards'][0]['reward']['merchant']['logo'], '')
        self.assertAlmostEqual(201.323, r['userrewards'][0]['reward']['merchant']['longitude'], '')
        self.assertEqual(10, r['userrewards'][1]['reward']['equiv_points'], '')
        self.assertEqual(True, r['userrewards'][1]['forsale'], '')
        self.assertEqual('StarBucks', r['userrewards'][1]['reward']['merchant']['name'], '')
        self.assertAlmostEqual(44.454, r['userrewards'][1]['reward']['merchant']['latitude'], '')
        self.assertEqual('/path2/to/logo.png', r['userrewards'][1]['reward']['merchant']['logo'], '')
        
        jsonstr = json.dumps({"username":"xin","email":"xin@test.com","phone":"4082538985","referer":{"refer_code":1}})
        response = c.post("/api/users", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')

        attrs = self.getAuthorizationHeader('jlu', 'ttttheman')
        
        response = c.get("/api/users/82", **attrs)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(6, len(r), '')
        self.assertEqual('xin', r['user']['username'], '')
        self.assertEqual('4082538985', r['userprofile']['phone'], '')
        self.assertEqual('xin@test.com', r['user']['email'], '')
        self.assertEqual('', r['user']['first_name'], '')
        self.assertIsNone(r['userpoint'], '')
        self.assertIsNone(r['pref'], '')
        
        jsonstr = json.dumps({"username":"xin2","email":"xin2@test.com","phone":"4082538985"})
        response = c.put("/api/users/82", jsonstr, 'application/json', **attrs)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/users/82", **attrs)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(6, len(r), '')
        self.assertEqual('xin', r['user']['username'], '')
        self.assertEqual('4082538985', r['userprofile']['phone'], '')
        self.assertEqual('xin2@test.com', r['user']['email'], '')
        
        response = c.delete("/api/users/82", **attrs)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/users", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(3, r['user_count'], '')

        
    def test_userpref(self):
        """
        Tests UserPrefHandler
        """
        c = Client()
        
        '''
        {
            "nearby_radius": 40.0
        }
        '''
        response = c.get("/api/users/2/pref", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(40.0, r['nearby_radius'], '')
        
        response = c.delete("/api/users/2/pref", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/users/2/pref", **self.extra)
        #print response
        self.assertContains(response, "DoesNotExist: UserPref matching query does not exist.", status_code=500)
        
        jsonstr = json.dumps({"nearby_radius":25.5})
        response = c.post("/api/users/2/pref", jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual("Created", response.content, '')
        
        response = c.get("/api/users/2/pref", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(25.5, r['nearby_radius'], '')
        
        jsonstr = json.dumps({"nearby_radius":45.0})
        response = c.put("/api/users/2/pref", jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/users/2/pref", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(45.0, r['nearby_radius'], '')      
        

    def test_userreview(self):
        """
        Tests UserReviewHandler
        """
        c = Client()
        
        """
        []
        """
        response = c.get("/api/users/2/review", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
   
        jsonstr = json.dumps({"merchant":{"id":1}, "review":"this merchant is awesome!", "rating":4.5})
        response = c.post("/api/users/2/review", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')
        
        jsonstr = json.dumps({"merchant":{"id":2}, "review":"very good! will come back", "rating":2.0})
        response = c.post("/api/users/2/review", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(83, r["id"], '')
        
        jsonstr = json.dumps({"merchant":{"id":1}, "review":"nice food", "rating":3.5})
        response = c.post("/api/users/2/review", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(84, r["id"], '')

        """
        [
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "3.5", 
                "review": "this merchant is awesome!", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": null
            }, 
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "4.5", 
                "review": "this merchant is awesome!", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": "2012-02-07"
            }, 
            {
                "merchant": {
                    "name": "StarBucks", 
                    "id": 2
                }, 
                "rating": "2.0", 
                "review": "very good! will come back", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": "2012-02-07"
            }, 
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "3.5", 
                "review": "nice food", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": "2012-02-07"
            }
        ]
        """
        response = c.get("/api/users/2/review", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual("this merchant is awesome!", r[0]['review'], '')
        self.assertEqual('3.5', r[0]['rating'], '')
        self.assertEqual("this merchant is awesome!", r[1]['review'], '')
        self.assertEqual('4.5', r[1]['rating'], '')
        self.assertEqual("very good! will come back", r[2]['review'], '')
        self.assertEqual(2.0, float(r[2]['rating']), '')
        self.assertEqual("nice food", r[3]['review'], '')
        self.assertEqual('3.5', r[3]['rating'], '')
        
        """
        [
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "3.5", 
                "review": "this merchant is awesome!", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": null
            }, 
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "4.0", 
                "review": "I love it!", 
                "user": {
                    "username": "testuser2", 
                    "id": 3
                }, 
                "time": null
            }, 
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "4.5", 
                "review": "this merchant is awesome!", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": "2012-02-07"
            }, 
            {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "rating": "3.5", 
                "review": "nice food", 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "time": "2012-02-07"
            }
        ]
        """
        response = c.get("/api/stores/1/review", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual("this merchant is awesome!", r[2]['review'], '')
        self.assertEqual('4.5', r[2]['rating'], '')
        self.assertEqual("nice food", r[3]['review'], '')
        self.assertEqual('3.5', r[3]['rating'], '')
        
        response = c.get("/api/stores/2/review", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual("very good! will come back", r[0]['review'], '')
        self.assertEqual(2.0, float(r[0]['rating']), '')
        
        response = c.delete("/api/users/2/review", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/users/2/review", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_merchant(self):
        """
        Tests merchant handler
        """
        c = Client()
        setup_func(connection)
        
        '''
        [
            {
                "distance": 0.27995036763905656, 
                "name": "Safeway", 
                "longitude": 201.323, 
                "id": 1, 
                "phone": "6502334332", 
                "reward_trigger": 200.0, 
                "address": "434 abc ave, san jose, ca", 
                "latitude": 102.454, 
                "logo": "/path/to/logo.png", 
                "email": "safeway@safeway.com", 
                "description": ""
            }
        ]
        '''
        response = c.get("/api/stores/prox/201.32,102.45,1", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('Safeway', r[0]['name'], '')
        self.assertEqual('6502334332', r[0]['phone'], '')
        self.assertEqual('/path/to/logo.png', r[0]['logo'], '')
        self.assertEqual(1, r[0]['id'], '')
        #self.assertGreater(1.0, r[0]['distance'], '')
        #self.assertEqual(200.0, r[0]['reward_trigger'], '')
        #self.assertEqual('', r[0]['description'], '')
        
        """
        [
            {
                "name": "Safeway", 
                "longitude": 201.323, 
                "id": 1, 
                "phone": "6502334332", 
                "address": "434 abc ave, san jose, ca", 
                "latitude": 102.454, 
                "logo": "/path/to/logo.png", 
                "email": "safeway@safeway.com"
            }, 
            {
                "name": "StarBucks", 
                "longitude": 22.323, 
                "id": 2, 
                "phone": "4082334332", 
                "address": "101 abc ave, san jose, ca", 
                "latitude": 44.454, 
                "logo": "/path2/to/logo.png", 
                "email": "support@starbucks.com"
            }
        ]
        """
        response = c.get("/api/stores/prox/201.32,102.45,10", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('Safeway', r[0]['name'], '')
        self.assertEqual('6502334332', r[0]['phone'], '')
        self.assertEqual('/path/to/logo.png', r[0]['logo'], '')
        self.assertEqual(1, r[0]['id'], '')
        #self.assertGreater(1.0, r[0]['distance'], '')
        #self.assertEqual(200.0, r[0]['reward_trigger'], '')
        #self.assertEqual('', r[0]['description'], '')
        self.assertEqual('StarBucks', r[1]['name'], '')
        self.assertEqual('4082334332', r[1]['phone'], '')
        self.assertEqual('/path2/to/logo.png', r[1]['logo'], '')
        self.assertEqual(2, r[1]['id'], '')
        #self.assertGreater(1.0, r[1]['distance'], '')
        #self.assertEqual(200.0, r[1]['reward_trigger'], '')
        #self.assertEqual('', r[1]['description'], '')
        
        '''
        {
            "name": "Safeway", 
            "rewardprogram_set": [
                {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway"
                    }, 
                    "name": "safeway loyalty program", 
                    "prog_type": 1, 
                    "reward_trigger": 200.0, 
                    "end_time": null, 
                    "reward": {
                        "equiv_points": 20, 
                        "name": "free bread"
                    }, 
                    "start_time": null
                }, 
                {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway"
                    }, 
                    "name": "safeway loyalty program 2", 
                    "prog_type": 0, 
                    "reward_trigger": 400.0, 
                    "end_time": null, 
                    "reward": {
                        "equiv_points": 10, 
                        "name": "free starbucks"
                    }, 
                    "start_time": null
                }
            ], 
            "longitude": 201.323, 
            "phone": "6502334332", 
            "userreview_set": [
                {
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "rating": "3.5", 
                    "review": "this merchant is awesome!", 
                    "user": {
                        "username": "testuser", 
                        "id": 2
                    }, 
                    "time": null
                }, 
                {
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "rating": "4.0", 
                    "review": "I love it!", 
                    "user": {
                        "username": "testuser2", 
                        "id": 3
                    }, 
                    "time": null
                }
            ], 
            "address": "434 abc ave, san jose, ca", 
            "latitude": 102.454, 
            "logo": "/path/to/logo.png", 
            "email": "safeway@safeway.com"
        }
        '''
        response = c.get("/api/stores/1", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(9, len(r), '')
        self.assertEqual('Safeway', r['name'], '')
        self.assertEqual('6502334332', r['phone'], '')
        self.assertEqual('/path/to/logo.png', r['logo'], '')
        self.assertEqual('safeway loyalty program', r['rewardprogram_set'][0]['name'], '')
        self.assertEqual(200.0, r['rewardprogram_set'][0]['reward_trigger'], '')
        self.assertEqual('free bread', r['rewardprogram_set'][0]['reward']['name'], '')
        self.assertEqual('safeway loyalty program 2', r['rewardprogram_set'][1]['name'], '')
        self.assertEqual(0, r['rewardprogram_set'][1]['prog_type'], '')
        self.assertEqual(10, r['rewardprogram_set'][1]['reward']['equiv_points'], '')
        self.assertEqual(2, len(r['userreview_set']), '')
        
        jsonstr = json.dumps({"name":"BostonMarket","email":"xin@test.com","phone":"4082538985","address":"973 1st st, san jose, ca","logo":"/logo/bm.png","longitude":"150.20","latitude":"90.09"})
        response = c.post("/api/stores", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')

        response = c.get("/api/stores/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(9, len(r), '')
        self.assertEqual('BostonMarket', r['name'], '')
        self.assertEqual('4082538985', r['phone'], '')
        self.assertEqual('/logo/bm.png', r['logo'], '')
        self.assertEqual('973 1st st, san jose, ca', r['address'], '')
        
        jsonstr = json.dumps({"email":"bm@test.com","phone":"6509234325"})
        response = c.put("/api/stores/82", jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(9, len(r), '')
        self.assertEqual('BostonMarket', r['name'], '')
        self.assertEqual('6509234325', r['phone'], '')
        self.assertEqual('bm@test.com', r['email'], '')
        
        response = c.delete("/api/stores/82", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/82", **self.extra)
        #print response.content
        self.assertContains(response, "DoesNotExist: Merchant matching query does not exist.", status_code=500)
 

    def test_purchase(self):
        """
        Tests purchase handler
        """
        c = Client()
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":1}, "dollar_amount":20.50, "description":"test purchase"})
        response = c.post('/api/users/2/purchase', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')
        
        '''
        [
            {
                "dollar_amount": "20.5", 
                "merchant": {
                    "name": "Safeway"
                }, 
                "description": "test purchase", 
                "time": "2011-09-30 23:49:03"
            }
        ]
        '''
        response = c.get('/api/users/2/purchase', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test purchase', r[0]['description'], '')
        self.assertEqual('Safeway', r[0]['merchant']['name'], '')
        
        response = c.delete('/api/users/2/purchase', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')


    def test_rewardprogram(self):
        """
        Tests rewardprogram handler
        """
        c = Client()
        setup_func(connection)
        
        '''
        {
            "status": 1, 
            "merchant": {
                "name": "Safeway"
            }, 
            "name": "safeway loyalty program", 
            "prog_type": 1, 
            "reward_trigger": 200.0, 
            "end_time": null, 
            "reward": {
                "equiv_points": 20, 
                "name": "free bread"
            }, 
            "start_time": null
        }
        '''
        response = c.get("/api/stores/1/program/1", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('safeway loyalty program', r['name'], '')
        self.assertEqual(1, r['prog_type'], '')
        self.assertEqual(None, r['end_time'], '')
        self.assertEqual(200.0, r['reward_trigger'], '')

        '''
        [
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway"
                }, 
                "name": "safeway loyalty program", 
                "prog_type": 1, 
                "reward_trigger": 200.0, 
                "end_time": null, 
                "reward": {
                    "equiv_points": 20, 
                    "name": "free bread"
                }, 
                "start_time": null
            }, 
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway"
                }, 
                "name": "safeway loyalty program 2", 
                "prog_type": 1, 
                "reward_trigger": 400.0, 
                "end_time": null, 
                "reward": {
                    "equiv_points": 10, 
                    "name": "free starbucks"
                }, 
                "start_time": null
            }
        ]
        '''
        response = c.get("/api/stores/1/program", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of merchant reward programs is not 2')
        self.assertEqual('safeway loyalty program', r[0]['name'], '')
        self.assertEqual(1, r[0]['prog_type'], '')
        self.assertEqual(None, r[0]['end_time'], '')
        self.assertEqual(200.0, r[0]['reward_trigger'], '')
        self.assertEqual('safeway loyalty program 2', r[1]['name'], '')
        self.assertEqual(0, r[1]['prog_type'], '')
        self.assertEqual(None, r[1]['end_time'], '')
        self.assertEqual(400.0, r[1]['reward_trigger'], '')
        
        jsonstr = json.dumps({"name":"BostonMarket loyalty program","status":1,"prog_type":1,"reward_trigger":150.0,"end_time":"2012-05-26","reward":{"id":1}})
        response = c.post("/api/stores/1/program", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')

        response = c.get("/api/stores/1/program/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('BostonMarket loyalty program', r['name'], '')
        self.assertEqual(1, r['prog_type'], '')
        self.assertEqual("2012-05-26", r['end_time'], '')
        self.assertEqual(150.0, r['reward_trigger'], '')
        self.assertEqual("free bread", r['reward']['name'], '')
        
        jsonstr = json.dumps({"prog_type":2,"reward_trigger":10,"reward":{"id":2}})
        response = c.put("/api/stores/1/program/82", jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/1/program/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('BostonMarket loyalty program', r['name'], '')
        self.assertEqual(2, r['prog_type'], '')
        self.assertEqual("2012-05-26", r['end_time'], '')
        self.assertEqual(10, r['reward_trigger'], '')
        self.assertEqual("free starbucks", r['reward']['name'], '')
        
        response = c.delete("/api/stores/1/program/82", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/program", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of merchant reward programs is not 2')
        
        response = c.delete("/api/stores/1/program", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/program", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), 'number of merchant reward programs is not 0')
 
    
    def test_reward(self):
        '''
        Test RewardHandler
        '''
        c = Client()
        setup_func(connection)
        
        '''
         {
            "status": 1, 
            "merchant": {
                "name": "Safeway", 
                "id": 1,
                "address": "434 abc ave, san jose, ca", 
                "longitude": 201.323, 
                "latitude": 102.454
            }, 
            "equiv_points": 20, 
            "name": "free bread", 
            "expire_in_days": 0, 
            "id": 1, 
            "expire_in_years": 3, 
            "equiv_dollar": "20", 
            "expire_in_months": 0, 
            "description": "free whole-wheet bread"
        }
        '''
        response = c.get("/api/stores/1/reward/1", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free bread', r['name'], '')
        self.assertEqual(20, r['equiv_points'], '')
        self.assertEqual(3, r['expire_in_years'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')
        self.assertEqual('434 abc ave, san jose, ca', r['merchant']['address'], '')
        self.assertAlmostEqual(201.323, r['merchant']['longitude'], '')

        '''
        [
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway", 
                    "id": 1,
                    "address": "434 abc ave, san jose, ca", 
                    "longitude": 201.323, 
                    "latitude": 102.454
                }, 
                "equiv_points": 20, 
                "name": "free bread", 
                "expire_in_days": 0, 
                "id": 1, 
                "expire_in_years": 3, 
                "equiv_dollar": "20", 
                "expire_in_months": 0, 
                "description": "free whole-wheet bread"
            }
        ]
        '''
        response = c.get("/api/stores/1/reward", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), 'number of merchant rewards is not 1')
        self.assertEqual('free bread', r[0]['name'], '')
        self.assertEqual(20, r[0]['equiv_points'], '')
        self.assertEqual(3, r[0]['expire_in_years'], '')
        self.assertEqual('Safeway', r[0]['merchant']['name'], '')
        self.assertEqual('434 abc ave, san jose, ca', r[0]['merchant']['address'], '')
        self.assertAlmostEqual(201.323, r[0]['merchant']['longitude'], '')

        
        jsonstr = json.dumps({"name":"free meal","status":1,"equiv_dollar":30,"equiv_points":30,"expire_in_days":"100","expire_in_years":"1","expire_in_months":"0","description":"free meal only"})
        response = c.post("/api/stores/1/reward", jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')

        response = c.get("/api/stores/1/reward/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free meal', r['name'], '')
        self.assertEqual(30, r['equiv_points'], '')
        self.assertEqual(1, r['expire_in_years'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')
        
        jsonstr = json.dumps({"equiv_points":50,"expire_in_months":5})
        response = c.put("/api/stores/1/reward/82", jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/1/reward/82", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free meal', r['name'], '')
        self.assertEqual(50, r['equiv_points'], '')
        self.assertEqual(5, r['expire_in_months'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')
        
        response = c.delete("/api/stores/1/reward/82", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/reward", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), 'number of merchant reward rewards is not 1')
        
        response = c.delete("/api/stores/1/reward", **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/reward", **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), 'number of merchant reward rewards is not 0')
        
        
    def test_userreward(self):
        '''
        Test UserRewardHandler
        '''
        c = Client()
        
        response = c.get('/api/users/reward', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        
        '''
        [
            {
                "id": 1, 
                "user": {
                    "username": "testuser2", 
                    "id": 3
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "longitude": 201.323, 
                        "address": "434 abc ave, san jose, ca", 
                        "latitude": 102.454, 
                        "logo": "/path/to/logo.png", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20.00", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "expiration": "2012-08-15", 
                "forsale": true
            }, 
            {
                "id": 2, 
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "longitude": 22.323, 
                        "address": "101 abc ave, san jose, ca", 
                        "latitude": 44.454, 
                        "logo": "/path2/to/logo.png", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10.00", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "expiration": "2012-08-20", 
                "forsale": true
            }
        ]  
        '''
        response = c.get('/api/users/reward/forsell', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('free one cup of starbucks coffee', r[1]['reward']['description'], '')
        self.assertEqual('testuser', r[1]['user']['username'], '')
        self.assertEqual(10, r[1]['reward']['equiv_points'], '')
        self.assertEqual(True, r[1]['forsale'], '')
        self.assertEqual(2, r[1]['id'], '')
        self.assertEqual('2012-08-20', r[1]['expiration'], '')
        self.assertEqual('StarBucks', r[1]['reward']['merchant']['name'], '')
        self.assertEqual('101 abc ave, san jose, ca', r[1]['reward']['merchant']['address'], '')
        self.assertEqual('free whole-wheet bread', r[0]['reward']['description'], '')
        self.assertEqual('testuser2', r[0]['user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual(True, r[0]['forsale'], '')
        self.assertEqual(3, r[0]['id'], '')
        self.assertEqual('2012-08-15', r[0]['expiration'], '')
        self.assertEqual('Safeway', r[0]['reward']['merchant']['name'], '')
        self.assertEqual('434 abc ave, san jose, ca', r[0]['reward']['merchant']['address'], '')
        
        jsonstr = json.dumps({"merchant_id":1, "rewardprogram_id":1})
        response = c.post('/api/users/2/reward', jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertContains(response, "user hasn't made enough purchases to be eligible for a reward")
        
        jsonstr = json.dumps({"merchant_id":1, "rewardprogram_id":1})
        response = c.post('/api/users/2/reward/1234', jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertContains(response, "Wrong free_code! user is not eligible for reward")
        
        jsonstr = json.dumps({"merchant_id":1, "rewardprogram_id":1})
        response = c.post('/api/users/2/reward/2011', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')
        
        jsonstr = json.dumps({"merchant_id":2, "rewardprogram_id":2})
        response = c.post('/api/users/2/reward', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(83, r["id"], '')
        
        jsonstr = json.dumps({"forsale":True, "userreward_id":83})
        response = c.put('/api/users/2/reward', jsonstr, 'application/json', **self.extra)
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        '''
        [
            {
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "longitude": 201.323, 
                        "address": "434 abc ave, san jose, ca", 
                        "latitude": 102.454, 
                        "logo": "/path/to/logo.png", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20.00", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "expiration": "2012-03-12", 
                "forsale": false
            }, 
            {
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "longitude": 22.323, 
                        "address": "101 abc ave, san jose, ca", 
                        "latitude": 44.454, 
                        "logo": "/path2/to/logo.png", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10.00", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "expiration": "2012-08-20", 
                "forsale": true
            }, 
            {
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "longitude": 201.323, 
                        "address": "434 abc ave, san jose, ca", 
                        "latitude": 102.454, 
                        "logo": "/path/to/logo.png", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20.00", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "expiration": "2015-02-06", 
                "forsale": false
            }, 
            {
                "user": {
                    "username": "testuser", 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "longitude": 22.323, 
                        "address": "101 abc ave, san jose, ca", 
                        "latitude": 44.454, 
                        "logo": "/path2/to/logo.png", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10.00", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "expiration": "2015-02-06", 
                "forsale": true
            }
        ]
        '''
        response = c.get('/api/users/2/reward', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual('free one cup of starbucks coffee', r[1]['reward']['description'], '')
        self.assertEqual('testuser', r[1]['user']['username'], '')
        self.assertEqual(10, r[1]['reward']['equiv_points'], '')
        self.assertEqual(True, r[1]['forsale'], '')
        self.assertEqual('2012-08-20', r[1]['expiration'], '')

        self.assertEqual('free whole-wheet bread', r[0]['reward']['description'], '')
        self.assertEqual('testuser', r[0]['user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual(False, r[0]['forsale'], '')
        self.assertEqual('2012-03-12', r[0]['expiration'], '')
        
        self.assertEqual('free whole-wheet bread', r[2]['reward']['description'], '')
        self.assertEqual('testuser', r[2]['user']['username'], '')
        self.assertEqual(20, r[2]['reward']['equiv_points'], '')
        self.assertEqual(False, r[2]['forsale'], '')
        #self.assertEqual('2015-02-06', r[2]['expiration'], '')

        self.assertEqual('free one cup of starbucks coffee', r[3]['reward']['description'], '')
        self.assertEqual('testuser', r[3]['user']['username'], '')
        self.assertEqual(10, r[3]['reward']['equiv_points'], '')
        self.assertEqual(True, r[3]['forsale'], '')
        #self.assertEqual('2015-02-06', r[2]['expiration'], '')
        
        response = c.delete('/api/users/2/reward', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')   
        
        response = c.get('/api/users/2/reward', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        
        
    def test_trade(self):
        """
        Tests trade activity handler
        """
        c = Client()
        jsonstr = json.dumps({"reward":{"id":1}, "from_user":{'id':3}, "description":"test buy"})
        response = c.post('/api/users/2/buy', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')
        
        '''
        [
            {
                "description": "test buy", 
                "points_value": 20, 
                "time": "2011-10-10 01:25:10", 
                "to_user": {
                    "username": "testuser", 
                    "first_name": "test", 
                    "last_name": "user", 
                    "email": "jun@cardmeleon.me"
                }, 
                "from_user": {
                    "username": "testuser2", 
                    "first_name": "test2", 
                    "last_name": "user2", 
                    "email": "jun@cardmeleon.me"
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 2
            }
        ]
        '''
        response = c.get('/api/users/2/buy', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test buy', r[0]['description'], '')
        self.assertEqual(20, r[0]['points_value'], '')
        self.assertEqual('testuser2', r[0]['from_user']['username'], '')
        self.assertEqual('testuser', r[0]['to_user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[0]['reward']['name'], '')
        self.assertEqual(2, r[0]['activity_type'], '')
        
        buyerPoint = UserPoint.objects.get(user__id=2)
        sellerPoint = UserPoint.objects.get(user__id=3)
        userrewards = UserReward.objects.filter(user__id=2, reward__id=1)
        self.assertEqual(180, buyerPoint.points, '')
        self.assertEqual(170, sellerPoint.points, '')
        self.assertEqual(2, len(userrewards), '')
        self.assertEqual(False, userrewards[0].forsale, '')
        self.assertEqual(False, userrewards[1].forsale, '')
        
        response = c.delete('/api/users/2/buy', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/2/buy', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_gift(self):
        """
        Tests gift activity handler
        """
        c = Client()
        
        jsonstr = json.dumps({"reward":{"id":1}, "to_user":{'id':3}, "description":"test gifting"})
        response = c.post('/api/users/2/gift', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["gift_code"], '')
        
        jsonstr = json.dumps({"reward":{"id":2}, "description":"test gifting for non-member"})
        response = c.put('/api/users/2/gift', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(83, r['gift_code'], '')
        
        '''
        [
            {
                "description": "test gifting for non-member", 
                "points_value": 10, 
                "time": "2012-01-27 04:04:06", 
                "to_user": null, 
                "from_user": {
                    "username": "testuser", 
                    "first_name": "test", 
                    "last_name": "user", 
                    "email": "jun@cardmeleon.me"
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "longitude": 22.323, 
                        "address": "101 abc ave, san jose, ca", 
                        "latitude": 44.454, 
                        "logo": "/path2/to/logo.png", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "activity_type": 3
            }, 
            {
                "description": "test gifting", 
                "points_value": 20, 
                "time": "2012-01-27 04:04:06", 
                "to_user": {
                    "username": "testuser2", 
                    "first_name": "test2", 
                    "last_name": "user2", 
                    "email": "jun@cardmeleon.me"
                }, 
                "from_user": {
                    "username": "testuser", 
                    "first_name": "test", 
                    "last_name": "user", 
                    "email": "jun@cardmeleon.me"
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "longitude": 201.323, 
                        "address": "434 abc ave, san jose, ca", 
                        "latitude": 102.454, 
                        "logo": "/path/to/logo.png", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 3
            }
        ]
        '''
        response = c.get('/api/users/2/gift', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('test gifting for non-member', r[0]['description'], '')
        self.assertEqual(10, r[0]['points_value'], '')
        self.assertEqual('testuser', r[0]['from_user']['username'], '')
        self.assertIsNone(r[0]['to_user'], '')
        self.assertEqual(10, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free starbucks', r[0]['reward']['name'], '')
        self.assertEqual(3, r[0]['activity_type'], '')
        self.assertEqual('test gifting', r[1]['description'], '')
        self.assertEqual(20, r[1]['points_value'], '')
        self.assertEqual('testuser', r[1]['from_user']['username'], '')
        self.assertEqual('testuser2', r[1]['to_user']['username'], '')
        self.assertEqual(20, r[1]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[1]['reward']['name'], '')
        self.assertEqual(3, r[1]['activity_type'], '')
        
        gifterPoint = UserPoint.objects.get(user__id=2)
        gifteePoint = UserPoint.objects.get(user__id=3)
        gifterrewards = UserReward.objects.filter(user__id=2, reward__id=1)
        gifteerewards = UserReward.objects.filter(user__id=3, reward__id=1)
        self.assertEqual(200, gifterPoint.points, '')
        self.assertEqual(150, gifteePoint.points, '')
        self.assertEqual(0, len(gifterrewards), '')
        self.assertEqual(2, len(gifteerewards), '')
        self.assertEqual(False, gifteerewards[0].forsale, '')
        self.assertEqual(True, gifteerewards[1].forsale, '')
        
        response = c.delete('/api/users/2/gift', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/2/gift', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_redeem(self):
        """
        Tests redeem activity handler
        """
        c = Client()
        jsonstr = json.dumps({"reward":{"id":1}, "description":"test redeem"})
        response = c.post('/api/users/2/redeem', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r["id"], '')
        
        '''
        [
            {
                "description": "test redeem", 
                "points_value": 20, 
                "time": "2011-10-02 02:08:27", 
                "to_user": null, 
                "from_user": {
                    "username": "ttttheman", 
                    "phone": "4082323232", 
                    "facebook": null, 
                    "email": "ttttheman@test.com", 
                    "referer": {
                        "id": 2
                    }
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 1
            }
        ]
        '''
        response = c.get('/api/users/2/redeem', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test redeem', r[0]['description'], '')
        self.assertEqual(20, r[0]['points_value'], '')
        self.assertEqual('testuser', r[0]['from_user']['username'], '')
        self.assertEqual(None, r[0]['to_user'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[0]['reward']['name'], '')
        self.assertEqual(1, r[0]['activity_type'], '')
        
        userrewards = UserReward.objects.filter(user__id=2, reward__id=1)
        self.assertEqual(0, len(userrewards), '')
        
        response = c.delete('/api/users/2/redeem', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/2/redeem', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_refer(self):
        """
        Tests referral activity handler
        """
        c = Client()
        
        """
        [
            {"referee_name":"Jun Lu", "refer_code":1},
            {"referee_name":"Yi Li", "refer_code":2},
            {"referee_name":"Xin Han", "refer_code":3}
        ]
        """
        jsonstr = json.dumps([
                              {"referee_name":"Jun Lu", "refer_method":1},
                              {"referee_name":"Yi Li", "refer_method":1},
                              {"referee_name":"Xin Han", "refer_method":1}
                            ]);
        response = c.post('/api/users/2/refer', jsonstr, 'application/json', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(82, r[0]['refer_code'], '')
        self.assertEqual(83, r[1]['refer_code'], '')
        self.assertEqual(84, r[2]['refer_code'], '')
        
        '''
        [
            {
                "referee_name": "Xin Han", 
                "referee_join_time": null, 
                "refer_method": 1, 
                "time": "2012-01-15 03:35:29"
            }, 
            {
                "referee_name": "Yi Li", 
                "referee_join_time": null, 
                "refer_method": 1, 
                "time": "2012-01-15 03:35:29"
            }, 
            {
                "referee_name": "Jun Lu", 
                "referee_join_time": null, 
                "refer_method": 1, 
                "time": "2012-01-15 03:35:29"
            }
        ]
        '''
        response = c.get('/api/users/2/refer', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(3, len(r), '')
        self.assertEqual('Xin Han', r[0]['referee_name'], '')
        self.assertEqual(None, r[0]['referee_join_time'], '')
        self.assertEqual(1, r[0]['refer_method'], '')
        self.assertEqual('Yi Li', r[1]['referee_name'], '')
        self.assertEqual(None, r[1]['referee_join_time'], '')
        self.assertEqual(1, r[1]['refer_method'], '')
        self.assertEqual('Jun Lu', r[2]['referee_name'], '')
        self.assertEqual(None, r[2]['referee_join_time'], '')
        self.assertEqual(1, r[2]['refer_method'], '')
        
        response = c.delete('/api/users/2/refer', **self.extra)
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/2/refer', **self.extra)
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

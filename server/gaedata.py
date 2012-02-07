'''
Created on Sep 20, 2011

@author: jlu
'''
import httplib, urllib, json, base64
from datetime import datetime


class GaeDataPrep:

    def getAuthorizationHeaderValue(self, username, password):
        auth = '%s:%s' % (username, password)
        auth = 'Basic %s' % base64.encodestring(auth)
        auth = auth.strip()
        #print auth
        return auth
    
    def rest(self, method, urlpath, payload):
        auth = self.getAuthorizationHeaderValue("testuser", "ttttheman")
        headers = {"Content-type":"application/json", "Authorization":auth}
        conn = httplib.HTTPConnection("cardmeleonapi.appspot.com", 80)
        conn.request(method, urlpath, payload, headers)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()
        return data
        
    def insertTestData(self):
        #params = urllib.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})

        m1 = {"id":5001}
        m2 = {"id":6001}
        m3 = {"id":5002}
        
        r1 = {"id":3005}
        r2 = {"id":4003}
        r3 = {"id":3006}
        
        p1 = {"id":8}
        p2 = {"id":8003}
        p3 = {"id":1005}
        
        u2 = {"id":3003}
        
        """
        
        # merchant
        jsonstr = json.dumps({"name":"BostonMarket","email":"xin@test.com","phone":"4082538985","address":"973 1st st, san jose, ca","logo":"/logo/bm.png","longitude":"150.20","latitude":"90.09"})
        response = self.rest("POST", "/api/stores", jsonstr)
        m1 = json.loads(response)
        print "1. merchant created: %d" % m1['id']

        jsonstr = json.dumps({"name":"Safeway","email":"jun@test.com","phone":"5108364344","address":"309 abc ave, san jose, ca","logo":"/logo2/bm.png","longitude":"150.30","latitude":"90.49"})
        response = self.rest("POST", "/api/stores", jsonstr)
        m2 = json.loads(response)
        print "2. merchant created: %d" % m2['id']
        
        jsonstr = json.dumps({"name":"StarBucks","email":"test@test.com","phone":"4083045439","address":"4420 bucks blvd, santa clara, ca","logo":"/logo3/bm.png","longitude":"152.53","latitude":"93.34"})
        response = self.rest("POST", "/api/stores", jsonstr)
        m3 = json.loads(response)
        print "3. merchant created: %d" % m3['id']
        
        # reward
        jsonstr = json.dumps({"name":"free meal","status":1,"equiv_dollar":30,"equiv_points":30,"expire_in_days":"0","expire_in_years":"1","expire_in_months":"0","description":"free meal only"})
        response = self.rest("POST", "/api/stores/%d/reward" % m1['id'], jsonstr)
        r1 = json.loads(response)
        print "4. reward created: %d" % r1['id']
        
        jsonstr = json.dumps({"name":"10% off any purchase","status":1,"equiv_dollar":100,"equiv_points":100,"expire_in_days":"0","expire_in_years":"1","expire_in_months":"0","description":"10% off any purchase. limited to 1 transaction only"})
        response = self.rest("POST", "/api/stores/%d/reward" % m1['id'], jsonstr)
        r2 = json.loads(response)
        print "5. reward created: %d" % r2['id']
        
        jsonstr = json.dumps({"name":"free StarBucks coffee","status":1,"equiv_dollar":5,"equiv_points":5,"expire_in_days":"0","expire_in_years":"1","expire_in_months":"0","description":"free one cup of coffee"})
        response = self.rest("POST", "/api/stores/%d/reward" % m1['id'], jsonstr)
        r3 = json.loads(response)
        print "6. reward created: %d" % r3['id']
        
        # program
        jsonstr = json.dumps({"name":"BostonMarket loyalty program","status":1,"prog_type":1,"reward_trigger":50.0,"end_time":"2012-12-26","reward":{"id":r1['id']}})
        response = self.rest("POST", "/api/stores/%d/program" % m1['id'], jsonstr)
        p1 = json.loads(response)
        print "7. program created: %d" % p1['id']
        
        jsonstr = json.dumps({"name":"Safeway loyalty program","status":1,"prog_type":1,"reward_trigger":30.0,"end_time":"2012-12-26","reward":{"id":r2['id']}})
        response = self.rest("POST", "/api/stores/%d/program" % m2['id'], jsonstr)
        p2 = json.loads(response)
        print "8. program created: %d" % p2['id']
        
        jsonstr = json.dumps({"name":"StarBucks loyalty program","status":1,"prog_type":1,"reward_trigger":10.0,"end_time":"2012-11-26","reward":{"id":r3['id']}})
        response = self.rest("POST", "/api/stores/%d/program" % m3['id'], jsonstr)
        p3 = json.loads(response)
        print "9. program created: %d" % p3['id']
        
        # user & profile
        jsonstr = json.dumps({"username":"xin","email":"xin@test.com","phone":"4082538985","password":"xin","first_name":"Xin","last_name":"Han","is_staff":False,"is_active":True,"is_superuser":False,"deviceid":"kajshfiweuh23","facebook":"xin"})
        response = self.rest("POST", "/api/users", jsonstr)
        u2 = json.loads(response)
        print "10. user created: %d" % u2['id']
        
        # userpref
        jsonstr = json.dumps({"nearby_radius":5.0})
        response = self.rest("POST", "/api/users/1/pref", jsonstr)
        print "11. userpref set for user 1: %s" % response
        
        jsonstr = json.dumps({"nearby_radius":10.0})
        response = self.rest("POST", "/api/users/%d/pref" % u2['id'], jsonstr)
        print "12. userpref set for user 2: %s" % response
        
        # user point
        jsonstr = json.dumps({"points":100})
        response = self.rest("PUT", "/api/users/1/point", jsonstr)
        print "13. userpoint set for user 1: %s" % response
        
        jsonstr = json.dumps({"points":90})
        response = self.rest("PUT", "/api/users/%d/point" % u2['id'], jsonstr)
        print "14. userpoint set for user 1: %s" % response
        
        # user reward
        jsonstr = json.dumps({"merchant_id":m1['id'], "rewardprogram_id":p1['id']})
        response = self.rest("POST", '/api/users/1/reward/2011', jsonstr)
        print "15. userreward set for user 1: %s" % response
        
        jsonstr = json.dumps({"merchant_id":m2['id'], "rewardprogram_id":p2['id']})
        response = self.rest("POST", '/api/users/1/reward/2011', jsonstr)
        print "16. userreward set for user 1: %s" % response
        
        jsonstr = json.dumps({"merchant_id":m1['id'], "rewardprogram_id":p1['id']})
        response = self.rest("POST", '/api/users/%d/reward/2011' % u2['id'], jsonstr)
        print "17. userreward set for user 2: %s" % response
        
        jsonstr = json.dumps({"merchant_id":m3['id'], "rewardprogram_id":p3['id']})
        response = self.rest("POST", '/api/users/%d/reward/2011' % u2['id'], jsonstr)
        print "18. userreward set for user 2: %s" % response
        
        # user progress: organic growth
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":m1['id']}, "dollar_amount":20.50, "description":"test purchase 1"})
        response = self.rest("POST", '/api/users/1/purchase', jsonstr)
        print "19. purchase recorded for user 1: %s" % response
        
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":m1['id']}, "dollar_amount":120.00, "description":"test purchase 2"})
        response = self.rest("POST", '/api/users/1/purchase', jsonstr)
        print "20. purchase recorded for user 1: %s" % response
        
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":m2['id']}, "dollar_amount":30.50, "description":"test purchase 3"})
        response = self.rest("POST", '/api/users/1/purchase', jsonstr)
        print "21. purchase recorded for user 1: %s" % response
        
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":m1['id']}, "dollar_amount":15.50, "description":"test purchase 1"})
        response = self.rest("POST", '/api/users/%d/purchase' % u2['id'], jsonstr)
        print "22. purchase recorded for user 2: %s" % response
        
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":m3['id']}, "dollar_amount":70.50, "description":"test purchase 2"})
        response = self.rest("POST", '/api/users/%d/purchase' % u2['id'], jsonstr)
        print "23. purchase recorded for user 2: %s" % response
        
        # user reviews
        jsonstr = json.dumps({"merchant":{"id":m1['id']}, "review":"this merchant is awesome!", "rating":4.5})
        response = self.rest("POST", "/api/users/1/review", jsonstr)
        print "24. userreview left by user 1: %s" % response
        
        jsonstr = json.dumps({"merchant":{"id":m2['id']}, "review":"will come back again!", "rating":5.0})
        response = self.rest("POST", "/api/users/1/review", jsonstr)
        print "25. userreview left by user 1: %s" % response
        
        jsonstr = json.dumps({"merchant":{"id":m3['id']}, "review":"love this place, recommend!", "rating":3.5})
        response = self.rest("POST", "/api/users/%d/review" % u2['id'], jsonstr)
        print "26. userreview left by user 2: %s" % response
        
        """
        
        
        
if __name__ == '__main__':
    from gaedata import GaeDataPrep
    gdp = GaeDataPrep()
    gdp.insertTestData()
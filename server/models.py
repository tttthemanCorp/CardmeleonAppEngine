from django.db import models
from django.contrib.auth.models import User


# Create your models here.
    
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    deviceid = models.CharField(max_length=100,null=True)
    facebook = models.EmailField(max_length=75,null=True)
    phone = models.CharField(max_length=20,null=True)
    referer = models.ForeignKey(User,related_name='User.referer',null=True)

    def __unicode__(self):
        return "username:{0}, facebook:{1}, deviceid:{2}, phone:{3}, referer:{4}".format(
                self.user.username, self.facebook, self.email, self.phone, self.referer.id)
    
class UserPoint(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField()
    
    def __unicode__(self):
        return "username:{0}, points:{1}".format(self.user.username, self.points)

class UserProgress(models.Model):
    user = models.ForeignKey(User)
    merchant = models.ForeignKey('Merchant')
    cur_dollar_amt = models.DecimalField(max_digits=10,decimal_places=2)
    cur_times = models.IntegerField()
    
    def __unicode__(self):
        return "username:{0}, merchant:{1}, dollars:{2}, times:{3}".format(self.user.username, self.merchant.name, self.cur_dollar_amt, self.cur_times)
    
class UserReward(models.Model):
    user = models.ForeignKey(User)
    reward = models.ForeignKey('Reward')
    expiration = models.DateField(null=True)
    forsale = models.BooleanField()
    
class UserPref(models.Model):
    user = models.OneToOneField(User)
    nearby_radius = models.FloatField()
    
class Merchant(models.Model):
    name = models.CharField(max_length=30)
    logo = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=75,null=True)
    address = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()
    description = models.CharField(max_length=500)
    
#    def updateValues(self, **data):
#        if 'name' in data:
#            self.name = data['name']
#        if 'logo' in data:
#            self.logo = data['logo']
#        if 'email' in data:
#            self.email = data['email']
#        if 'phone' in data:
#            self.phone = data['phone']
#        if 'address' in data:
#            self.address = data['address']
#        if 'longitude' in data:
#            self.longitude = data['longitude']
#        if 'latitude' in data:
#            self.latitude = data['latitude']
  
    def __unicode__(self):
        return "name:{0}, logo:{1}, email:{2}, phone:{3}, address:{4}, longitude:{5}, latitude:{6}".format(
                self.name, self.logo, self.email, self.phone, self.address, self.longitude, self.latitude)

class RewardProgram(models.Model):
    name = models.CharField(max_length=100,null=True)
    merchant = models.ForeignKey(Merchant)
    prog_type = models.SmallIntegerField()  # DollarAmount|PurchaseTimes: 0|1
    reward_trigger = models.FloatField(null=True)  # accumulated threshold to trigger rewards
    reward = models.ForeignKey('Reward')
    start_time = models.DateField(null=True)  # program start time
    end_time = models.DateField(null=True)  # program end time
    status = models.SmallIntegerField()  # active|inactive|paused
    
#    def updateValues(self, **data):
#        """
#        Update everything except merchant
#        """
#        if 'name' in data:
#            self.name = data['name']
#        if 'prog_type' in data:
#            self.prog_type = data['prog_type']
#        if 'reward_trigger' in data:
#            self.reward_trigger = data['reward_trigger']
#        if 'start_time' in data:
#            self.start_time = data['start_time']
#        if 'end_time' in data:
#            self.end_time = data['end_time']
#        if 'status' in data:
#            self.status = data['status']
#        if 'reward' in data:
#            self.reward = data['reward']
    
class Reward(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100,null=True)
    merchant = models.ForeignKey(Merchant)
    equiv_dollar = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    equiv_points = models.IntegerField(null=True)
    expire_in_days = models.IntegerField(null=True)
    expire_in_months = models.IntegerField(null=True)
    expire_in_years = models.IntegerField(null=True)
    status = models.SmallIntegerField()  # active|cancelled
    
#    def updateValues(self, **data):
#        """
#        Update everything except merchant
#        """
#        if 'name' in data:
#            self.name = data['name']
#        if 'description' in data:
#            self.description = data['description']
#        if 'equiv_dollar' in data:
#            self.equiv_dollar = data['equiv_dollar']
#        if 'equiv_points' in data:
#            self.equiv_points = data['equiv_points']
#        if 'expire_in_days' in data:
#            self.expire_in_days = data['expire_in_days']
#        if 'expire_in_months' in data:
#            self.expire_in_months = data['expire_in_months']
#        if 'expire_in_years' in data:
#            self.expire_in_years = data['expire_in_years']
#        if 'status' in data:
#            self.status = data['status']
    
class PurchaseActivity(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    merchant = models.ForeignKey(Merchant)
    dollar_amount = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.CharField(max_length=200,null=True)
    
    class Meta:
        ordering = ['-time']

class RewardActivity(models.Model):
    reward = models.ForeignKey(Reward)
    time = models.DateTimeField(auto_now_add=True)
    activity_type = models.SmallIntegerField()  # redeem|buy|gift: 1/2/3
    from_user = models.ForeignKey(User,related_name='User.initiating_rewardactivity_set',blank=True,null=True)  #redeemer|seller|gifter
    to_user = models.ForeignKey(User,related_name='User.receiving_rewardactivity_set',blank=True,null=True)  #(merchant)|buyer|gift-receiver
    description = models.CharField(max_length=200,null=True)
    points_value = models.IntegerField(null=True)
        
    class Meta:
        ordering = ['-time']
    
class ReferralActivity(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    referer = models.ForeignKey(User,related_name='User.referer_activity_set')
    referee = models.ForeignKey(User,related_name='User.referee_activity_set',null=True)
    referee_name = models.CharField(max_length=30,null=True)
    refer_method = models.SmallIntegerField()  # email|text|phone|web|other: 0|1|2|3|4
    referee_join_time = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-time']
    
class UserReview(models.Model):
    user = models.ForeignKey(User)
    merchant = models.ForeignKey(Merchant)
    review = models.CharField(max_length=1000)
    time = models.DateField(null=True)
    rating = models.DecimalField(max_digits=2,decimal_places=1,null=True)

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields import NullBooleanField
#from django.contrib.auth.models import User

User = get_user_model()

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    phone = models.CharField(max_length=12)
    desc = models.TextField()
    date = models.DateField()
    anyfile = models.FileField(upload_to='', null=True, blank=True)

    def __str__(self):
        return self.name

#Changes made by MANISH
class Seller(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=130)
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=200)
    price = models.FloatField()
    desc = models.TextField()
    img = models.ImageField(upload_to='')
    pdf = models.FileField(upload_to='pdf', null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return self.name

class Cathome(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural="Categories"

class Books(models.Model):
    category=models.ForeignKey(Cathome, on_delete=models.SET_NULL, null=True, blank=True)
    image=models.ImageField(null=False, blank=False)
    description = models.TextField(max_length=500, null=False, blank=False)
    name = models.CharField(max_length=100, null=True, blank=False)
    author = models.CharField(max_length=130, null=True, blank=False)
    price = models.FloatField(null=True, blank=False)
    pdf = models.FileField(null=True, blank=True)
    digital = models.BooleanField(default=False,null=True, blank=True)
    date = models.DateField(null=True)
    likes=models.ManyToManyField(User, related_name="video_loved")
    dislikes=models.ManyToManyField(User, related_name="video_disliked")

    def __str__(self):
        return self.name
    
    def num_likes(self):
        return self.likes.count()
    
    def num_dislikes(self):
        return self.dislikes.count()

    class Meta:
        verbose_name_plural="Books"

class Review(models.Model):
    customer = models.ForeignKey(User, related_name="reviews", on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Books, related_name="reviews", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=122, null=True, blank=True)
    email = models.CharField(max_length=122, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(null=True)

    def __str__(self):
        return 'name={0}'.format(self.name)
        

class Order(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False, null=True, blank=True)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 


class OrderItem(models.Model):
	product = models.ForeignKey(Books, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=200, null=False, default='India')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
	    return self.address

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="profile2.jpg", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
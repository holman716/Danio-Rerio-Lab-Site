from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# notes to self:
#  blank=True means the field is optional
#  choices=( ('short', 'long name'), )
#  default=?? to set default value
#  help_text="Text to help explain what to enter"
#  unique=True means unique for table
#  verbose_name="A Better Name For a Field"
# to update run "python manage.py syncdb"

class Action(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	slug = models.SlugField()

	class Meta:
		pass
	
	def __unicode__(self):
		return self.name
		
class HistoryItem(models.Model):
	id = models.AutoField(primary_key=True)
	action = models.ForeignKey('Action')
	who = models.ForeignKey('StaffMember', related_name='historyitem_who_set', blank=True, null=True)
	date = models.DateField(blank=True, null=True)
	reqd_by = models.ForeignKey('StaffMember', blank=True, null=True)
	reqd_date = models.DateField(blank=True, null=True)
	reqd_instructions = models.TextField(blank=True)
	finished = models.BooleanField()
	param_1 = models.IntegerField(blank=True, null=True)
	param_2 = models.IntegerField(blank=True, null=True)
	param_3 = models.IntegerField(blank=True, null=True)
	param_4 = models.IntegerField(blank=True, null=True)
	param_5 = models.IntegerField(blank=True, null=True)
	param_6 = models.IntegerField(blank=True, null=True)
	comments = models.TextField(blank=True)
	
	class Meta:
		pass
	
	def __unicode__(self):
		return u'%s by %s at %s' % (self.action.name, self.who, self.date)
		
class Permission(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	actions = models.ManyToManyField('Action')

	class Meta:
		pass
	
	def __unicode__(self):
		return self.name

class StaffMember(models.Model):
	user = models.OneToOneField(User) # requires Auth package

	first_name = models.CharField(max_length=64, blank=True)
	last_name = models.CharField(max_length=64, blank=True)
	
	position = models.CharField(max_length=128, blank=True)
	permissions = models.ManyToManyField('Permission', blank=True, null=True)
	lab_groups = models.ManyToManyField('LabGroup', blank=True, null=True)
	IACUC_numbers = models.ManyToManyField('IACUC_ids', null=True)

	class Meta:
		pass
	
	def __unicode__(self):
		return u'%s %s' % (self.first_name, self.last_name)
	
	def set_password(self, password):
		self.user.set_password(self.user, password)

def create_staff_member(sender, instance, created, **kwargs):
    if created:
        StaffMember.objects.get_or_create(user=instance)

post_save.connect(create_staff_member, sender=User)
		
class LabGroup(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	manager = models.ForeignKey('StaffMember', blank=True, null=True)
	permissions = models.ManyToManyField('Permission', blank=True, null=True)

	class Meta:
		pass
	
	def __unicode__(self):
		return self.name

class Line(models.Model):
	id = models.AutoField(primary_key=True)
	barcode = models.IntegerField(db_index=True, unique=True)
	name = models.CharField(max_length=256)
	IACUC_ID = models.CharField(max_length=256, blank=True)
	parent = models.ForeignKey('Line', null=True, blank=True)
	raised = models.BooleanField(default=False)
	current_quantity = models.IntegerField()
	original_quantity = models.IntegerField()
	container = models.ForeignKey('Container_types', null=True, blank=True)
	location = models.CharField(max_length=128, blank=True)
	strain = models.CharField(max_length=128, blank=True)
	SEX_CHOICES = (
		('M', 'Male'),
		('F', 'Female'),
		('U', 'Unknown'),
		('N', 'None'),
		('B', 'Both'),
	)
	sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='U')
	active = models.BooleanField()
	birthdate = models.DateField(null=True)
	owner = models.ForeignKey('StaffMember')
	genomes = models.ManyToManyField('GeneticElement', null=True)
	
	class Meta:
		pass
	
	def __unicode__(self):
		return self.name

class IACUC_ids(models.Model):
	id = models.AutoField(primary_key=True)
	IACUC_number = models.CharField(max_length=200)

	def __unicode__(self):
		return self.IACUC_number

class Container_types(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.type

class Product(models.Model):
	id = models.AutoField(primary_key=True)
	barcode = models.IntegerField(db_index=True, unique=True)
	name = models.CharField(max_length=200)
	line_id = models.ForeignKey('Line', null=True, blank=True, related_name='Parent1')
	line2_id = models.ForeignKey('Line', null=True, blank=True, related_name='Parent2')
	type = models.ForeignKey('ProductType')
	container = models.ForeignKey('Container_types', null=True, blank=True)
	active = models.BooleanField()
	owner = models.ForeignKey('StaffMember')

	class Meta:
		pass
	
	def __unicode__(self):
		return self.name
		
class GeneticElement(models.Model):
	id = models.AutoField(primary_key=True)
	version = models.ForeignKey('Genome_version')
	chromosome = models.CharField(max_length=128)
	position = models.BigIntegerField(null=True)
	insert_name = models.ForeignKey('Insert_name', null=True)
	allele_type = models.ForeignKey('Allele_type')

	def __unicode__(self):
		return self.chromosome + ' - ' + str(self.position)

class Genome_version(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)

	def __unicode__(self):
		return self.name

class Insert_name(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	creator = models.CharField(max_length=128)
	ref_number = models.CharField(max_length=128, null=True)
	sequence = models.TextField()

	def __unicode__(self):
		return self.name

class Allele_type(models.Model):
	id = models.AutoField(primary_key=True)
	TYPE_CHOICES = (
		 ('insertion','insertion'),
		 ('deletion','deletion'),
		 ('?>A','?>A'),
		 ('?>G','?>G'),
		 ('?>T','?>T'),
		 ('?>C','?>C'),
	)
	type = models.CharField(max_length=128)
	size = models.IntegerField()
	ORIENTATION_CHOICES = (
		('+', '+'),
		('-', '-')
	)
	orientation = models.CharField(max_length=1, choices=ORIENTATION_CHOICES, default='+')

	def __unicode__(self):
		return self.type + self.orientation + ': ' + str(self.size)

class ProductType(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=200)

	def __unicode__(self):
		return self.type

class Barcode(models.Model):
	id = models.AutoField(primary_key=True)
	used = models.BooleanField()

	class Meta:
		pass
	
	def __unicode__(self):
		return self.type
	
from django import forms
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from labinterface.models import *
from registration.models import RegistrationProfile

class AddLineForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	barcode = forms.IntegerField()
	name = forms.CharField()
	IACUC_ID = forms.CharField()
	parent = forms.ModelChoiceField(queryset=Line.objects.all(), empty_label="(No Parent)", required=False)
	raised = forms.BooleanField(required=False)
	current_quantity = forms.IntegerField()
	original_quantity = forms.IntegerField()
	location = forms.CharField()
	container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False)
	sex = forms.ChoiceField(choices=Line.SEX_CHOICES)
	strain = forms.CharField(required=False)
	active = forms.BooleanField(required=False)
	#owner = forms.ModelChoiceField(queryset=StaffMember.objects.all(), )
	birthdate = forms.DateField(required=False)

class EnterBarcodeForm(forms.Form):
	selection = forms.IntegerField()
	test = []
	for i in range (1,5):
		test.append(forms.IntegerField())

class AddProductTypeForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	name = forms.CharField()

class SelectProductTypeForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label=None)

class AddProductForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	barcode = forms.IntegerField()
	name = forms.CharField()
	line = forms.ModelChoiceField(queryset=Line.objects.all(), empty_label="(No Parent)", required=False)
	type = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label=None)
	container = forms.CharField()
	active = forms.BooleanField(required=False)
	owner = forms.ModelChoiceField(queryset=StaffMember.objects.all(), empty_label=None)


class AddGenomeForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	version = forms.ModelChoiceField(queryset=Genome_version.objects.all())
	chromosome = forms.CharField()
	position = forms.IntegerField()
	insert_name = forms.ModelChoiceField(queryset=Insert_name.objects.all())
	allele_type = forms.ModelChoiceField(queryset=Allele_type.objects.all())

class SelectGenomeForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=GeneticElement.objects.all(), empty_label=None)

class AddGenomeVersionForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	name = forms.CharField()

class SelectGenomeVersionForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=Genome_version.objects.all(), empty_label=None)

class AddGenomeAssociationForm(forms.Form):
	line = forms.ModelChoiceField(queryset=Line.objects.all(), empty_label=None)
	genome = forms.ModelChoiceField(queryset=GeneticElement.objects.all(), empty_label=None)

class MyRegistrationForm(RegistrationForm):
	attrs_dict = { 'class': 'required' }
	# this allows us to create profile objects (StaffMember objects) to
	# be 1-1 with User objects in the django.auth module
	first_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
	last_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
	position = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
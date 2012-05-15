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
	owner = forms.ModelChoiceField(queryset=StaffMember.objects.all(), )
	birthdate = forms.DateField(required=False)

class EnterBarcodeForm(forms.Form):
	selection = forms.IntegerField()

class PrintBarcodeForm(forms.Form):
	quantity = forms.IntegerField(help_text="How many barcodes will be printed?")

class AddProductTypeForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	type = forms.CharField()

class SelectProductTypeForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label=None)

class AddProductForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	barcode = forms.IntegerField()
	name = forms.CharField()
	line = forms.IntegerField()
	line2 = forms.IntegerField()
	type = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label=None)
	container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label=None)
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

class AddContainerTypeForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	type = forms.CharField()

class SelectContainerTypeForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label=None)

class AddAlleleTypeForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	type = forms.ChoiceField(choices=Allele_type.TYPE_CHOICES)
	size = forms.IntegerField()
	orientation = forms.ChoiceField(choices=Allele_type.ORIENTATION_CHOICES)

class SelectAlleleTypeForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=Allele_type.objects.all(), empty_label=None)

class AddInsertNameForm(forms.Form):
	pk = forms.CharField(widget=forms.HiddenInput(), required=False)
	name = forms.CharField()
	creator = forms.CharField()
	ref_number = forms.CharField(required=False)
	sequence = forms.CharField()

class SelectInsertNameForm(forms.Form):
	selection = forms.ModelChoiceField(queryset=Insert_name.objects.all(), empty_label=None)

class AddGenomeAssociationForm(forms.Form):
	line = forms.ModelChoiceField(queryset=Line.objects.all(), empty_label=None)
	genome = forms.ModelChoiceField(queryset=GeneticElement.objects.all(), empty_label=None)

class SplitLineInitialForm(forms.Form):
	choices = (('S','Singles'),('G','Groups'))
	step = forms.CharField(widget=forms.HiddenInput(), required=False)
	lineBarcode = forms.CharField(widget=forms.HiddenInput(), required=False)
	split_Type = forms.ChoiceField(choices=choices, help_text="Will the split be in singles or groups?")
	product_Type = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label="----------", help_text="What type of product will be produced?")
	product_container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False, help_text="In what type of container will the product be stored?")

class SplitLineSinglesForm(forms.Form):
	step = forms.CharField(widget=forms.HiddenInput(), required=False)
	lineBarcode = forms.CharField(widget=forms.HiddenInput(), required=False)
	product_Type = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=ProductType.objects.all(), empty_label="----------", required=False)
	product_container = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False)
	quantity = forms.IntegerField(help_text="How many individual lines should be split off from the original?")
	first_Barcode = forms.IntegerField(help_text="What is the first line barcode in the series? If the barcodes are not in order please use groups option and scan in each barcode one at a time.")
	first_product_Barcode = forms.IntegerField(help_text="What is the first product barcode in the series? If the barcodes are not in order please use groups option and scan in each barcode one at a time.")
	location = forms.CharField(help_text="Where will the lines be stored?")
	container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False, help_text="What container types will the lines be stored in?")
	active = forms.BooleanField(help_text="Are the groups active?")

class SplitLineGroupsForm(forms.Form):
	groupNum = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	step = forms.CharField(widget=forms.HiddenInput(), required=False)
	lineBarcode = forms.CharField(widget=forms.HiddenInput(), required=False)
	product_Type = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=ProductType.objects.all(), empty_label="----------", required=False)
	product_container = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False)
	quantity = forms.IntegerField(help_text="How many fish are in this group?")
	newLineBarcode = forms.IntegerField(help_text="What is the barcode associated with this group?")
	product_Barcode = forms.IntegerField(help_text="What is the barcode associated with this product?")
	location = forms.CharField(help_text="Where will the line group be stored?")
	container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False, help_text="What container will the line group be stored in?")
	active = forms.BooleanField(required=False, help_text="Is the line group active?")
	final = forms.BooleanField(required=False, help_text="Is this the last group to enter?")

class SplitLineFinalForm(forms.Form):
	step = forms.CharField(widget=forms.HiddenInput(), required=False)
	lineBarcode = forms.CharField(widget=forms.HiddenInput(), required=False)
	current_quantity = forms.IntegerField(help_text="How many fish are left?")
	location = forms.CharField(help_text="Where will the old line be stored?")
	container = forms.ModelChoiceField(queryset=Container_types.objects.all(), empty_label="(Unknown)", required=False, help_text="What container will now house the old line?")
	active = forms.BooleanField(required=False, help_text="Is the line still active?")

class ProcessMatingForm(forms.Form):
	productId = forms.CharField(widget=forms.HiddenInput(), required=False)

class MyRegistrationForm(RegistrationForm):
	attrs_dict = { 'class': 'required' }
	# this allows us to create profile objects (StaffMember objects) to
	# be 1-1 with User objects in the django.auth module
	first_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
	last_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
	position = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response
from django.http import *
from fish.labinterface.models import *
from fish.labinterface.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django import template

import urllib
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

def addLine(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddLineForm(request.POST)
			if form.is_valid():
				# process form data
				barcode = form.cleaned_data['barcode']
				name = form.cleaned_data['name']
				IACUC_ID = form.cleaned_data['IACUC_ID']
				parent = form.cleaned_data['parent']
				raised = form.cleaned_data['raised']
				current_quantity = form.cleaned_data['current_quantity']
				original_quantity = form.cleaned_data['original_quantity']
				container = form.cleaned_data['container']
				location = form.cleaned_data['location']
				sex = form.cleaned_data['sex']
				active = form.cleaned_data['active']
				strain = form.cleaned_data['strain']
				birthdate = form.cleaned_data['birthdate']
				owner = sm #form.cleaned_data['owner']
			
				newline = {}
				if parent == None:
					newline = Line(barcode=barcode ,name=name, IACUC_ID=IACUC_ID, raised=raised, original_quantity=original_quantity, current_quantity=current_quantity, container=container, location=location, sex=sex, active=active, strain=strain, birthdate=birthdate, owner=owner)
				else:
					newline = Line(barcode=barcode ,name=name, IACUC_ID=IACUC_ID, raised=raised, parent=parent, original_quantity=original_quantity, current_quantity=current_quantity, container=container, location=location, sex=sex, active=active, strain=strain, birthdate=birthdate, owner=owner)
				newline.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddLineForm()
		dict['form'] = form
		dict['action_slug'] = "addline"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editLine(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# submitting the modification
				form = AddLineForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = Line.objects.filter(pk=pk).get()
					
					new.barcode = form.cleaned_data['barcode']
					new.name = form.cleaned_data['name']
					new.IACUC_ID = form.cleaned_data['IACUC_ID']
					new.parent = form.cleaned_data['parent']
					new.raised = form.cleaned_data['raised']
					new.current_quantity = form.cleaned_data['current_quantity']
					new.original_quantity = form.cleaned_data['original_quantity']
					new.container = form.cleaned_data['container']
					new.sex = form.cleaned_data['sex']
					new.active = form.cleaned_data['active']
					new.strain = form.cleaned_data['strain']
					new.owner = form.cleaned_data['owner']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Line.objects.filter(barcode__exact=selection).get()
				initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode,'IACUC_ID': to_edit.IACUC_ID, 'raised': to_edit.raised,'current_quantity': to_edit.current_quantity,'original_quantity': to_edit.original_quantity, 'container': to_edit.container, 'sex': to_edit.sex, 'active': to_edit.active, 'strain': to_edit.strain, 'owner': to_edit.owner}
				if not to_edit.parent == None:
					initial['parent'] = to_edit.parent.pk
				form = AddLineForm(initial=initial)
		else:
			# choosing what object to edit
			form = EnterBarcodeForm()
		dict['form'] = form
		dict['action_slug'] = "editline"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def viewItemRedirect(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		if request.method == 'GET':
			selection = request.GET.get('barcode')
			destination = request.GET.get('type')
			if destination == 'Line':
				return viewLine(request,selection)
			else:
				if destination == 'Product':
					return viewProduct(request,selection)


def viewLine(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['id'] = id
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		dict['qr_code'] = qrcode(id)
		obj = Line.objects.filter(barcode=id).get()
		dict['name'] = obj.name
		dict['iacuc_id'] = obj.IACUC_ID
		if obj.parent == None:
			dict['parent'] = "None"
		else: 
			dict['parent'] = obj.parent
		dict['raised'] = obj.raised
		dict['current_quantity'] = obj.current_quantity
		dict['original_quantity'] = obj.original_quantity
		dict['owner'] = obj.owner
		dict['container'] = obj.container
		dict['sex'] = obj.sex
		dict['active'] = obj.active
		dict['products'] = Product.objects.filter(line_id=obj)
		dict['children'] = Line.objects.filter(parent=obj)
		
		return render_to_response('viewline.html', dict, context_instance=RequestContext(request))
		
def addProductType(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddProductTypeForm(request.POST)
			if form.is_valid():
				# process form data
				name = form.cleaned_data['name']
				new = ProductType(name=name)
				new.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddProductTypeForm()
		dict['form'] = form
		dict['action_slug'] = "addproducttype"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editProductType(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# submitting the modification
				form = AddProductTypeForm(request.POST)
				if form.is_valid():
					# process form data
					name = form.cleaned_data['name']
					pk = form.cleaned_data['pk']
					new = ProductType.objects.filter(pk=pk).get()
					new.name = name
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = ProductType.objects.filter(pk=selection).get()
				initial = {'name': to_edit.name, 'pk': to_edit.pk}
				form = AddProductTypeForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectProductTypeForm()
		dict['form'] = form
		dict['action_slug'] = "editproducttype"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def addProduct(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddProductForm(request.POST)
			if form.is_valid():
				# process form data
				barcode = form.cleaned_data['barcode']
				name = form.cleaned_data['name']
				line = form.cleaned_data['line']
				type = form.cleaned_data['type']
				container = form.cleaned_data['container']
				active = form.cleaned_data['active']
				owner = form.cleaned_data['owner']
			
				new = {}
				if line == None:
					new = Product(barcode=barcode, name=name, type=type, container=container, active=active, owner=owner)
				else:
					new = Product(barcode=barcode, name=name, line_id=line, type=type, container=container, active=active, owner=owner)
				new.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddProductForm()
		dict['form'] = form
		dict['action_slug'] = "addproduct"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editProduct(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# submitting the modification
				form = AddProductForm(request.POST)
				if form.is_valid():
					# process form data
					barcode = form.cleaned_data['barcode']
					name = form.cleaned_data['name']
					pk = form.cleaned_data['pk']
					type = form.cleaned_data['type']
					container = form.cleaned_data['container']
					active = form.cleaned_data['active']
					line = form.cleaned_data['line']
					owner = form.cleaned_data['owner']
					new = Product.objects.filter(pk=pk).get()
					new.name = name
					new.type = type
					new.container = container
					new.active = active
					new.line_id = line
					new.owner = owner
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Product.objects.filter(barcode__exact=selection).get()
				initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode, 'type': to_edit.type.pk, 'container': to_edit.container,'active': to_edit.active, 'owner':to_edit.owner}
				if not to_edit.line_id == None:
					initial['line'] = to_edit.line_id.pk
				form = AddProductForm(initial=initial)
		else:
			# choosing what object to edit
			form = EnterBarcodeForm()
		dict['form'] = form
		dict['action_slug'] = "editproduct"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def viewProduct(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		dict['qr_code'] = qrcode(id)
		obj = Product.objects.filter(barcode=id).get()
		dict['name'] = obj.name
		if obj.line_id == None:
			dict['line_id'] = "None"
		else: 
			dict['line_id'] = obj.line_id
		dict['type'] = obj.type
		dict['container'] = obj.container
		dict['active'] = obj.active
		dict['owner'] = obj.owner
		
		return render_to_response('viewproduct.html', dict, context_instance=RequestContext(request))

def addGenome(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddGenomeForm(request.POST)
			if form.is_valid():
				# process form data
				version = form.cleaned_data['version']
				chromosome = form.cleaned_data['chromosome']
				position = form.cleaned_data['position']
				insert_name = form.cleaned_data['insert_name']
				allele_type = form.cleaned_data['allele_type']
			
				newgenome = {}
				newgenome = GeneticElement(version=version, chromosome=chromosome, position=position, insert_name=insert_name, allele_type=allele_type)
				newgenome.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddGenomeForm()
		dict['form'] = form
		dict['action_slug'] = "addgenome"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editGenome(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# submitting the modification
				form = AddGenomeForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = GeneticElement.objects.filter(pk=pk).get()
					
					new.version = form.cleaned_data['version']
					new.chromosome = form.cleaned_data['chromosome']
					new.position = form.cleaned_data['position']
					new.insert_name = form.cleaned_data['insert_name']
					new.allele_type = form.cleaned_data['allele_type']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = GeneticElement.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'version': to_edit.version, 'chromosome': to_edit.chromosome,'position': to_edit.position,'insert_name': to_edit.insert_name, 'allele_type': to_edit.allele_type}
				form = AddGenomeForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectGenomeForm()
		dict['form'] = form
		dict['action_slug'] = "editgenome"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def viewGenome(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		obj = GeneticElement.objects.filter(pk=id).get()
		dict['version'] = obj.version
		dict['chromosome'] = obj.chromosome
		dict['position'] = obj.position
		dict['insert_name'] = obj.insert_name
		dict['allele_type'] = obj.allele_type
		dict['lines'] = Line.objects.filter(genomes=obj)
		
		return render_to_response('viewgenome.html', dict, context_instance=RequestContext(request))

def addGenomeVersion(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddGenomeVersionForm(request.POST)
			if form.is_valid():
				# process form data
				name = form.cleaned_data['name']
			
				newgenome = {}
				newgenome = Genome_version(name=name)
				newgenome.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddGenomeVersionForm()
		dict['form'] = form
		dict['action_slug'] = "addgenomeversion"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editGenomeVersion(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# submitting the modification
				form = AddGenomeVersionForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = Genome_version.objects.filter(pk=pk).get()
					
					new.name = form.cleaned_data['name']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Genome_version.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'name': to_edit.name}
				form = AddGenomeVersionForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectGenomeVersionForm()
		dict['form'] = form
		dict['action_slug'] = "editgenomeversion"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addGenomeAssociation(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddGenomeAssociationForm(request.POST)
			if form.is_valid():
				# process form data
				line = form.cleaned_data['line']
				genome = form.cleaned_data['genome']
			
				line.genomes.add(genome)
				line.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddGenomeAssociationForm()
		dict['form'] = form
		dict['action_slug'] = "addgenomeassociation"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def splitLine(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			selection = request.POST.get('selection')
			if selection is None:
				# A line is neccessary to split a line
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Genome_version.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'name': to_edit.name}
				form = AddGenomeVersionForm(initial=initial)
		else:
			# choosing what object to edit
			form = EnterBarcodeForm()
		dict['form'] = form
		dict['action_slug'] = "splitline"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

##############
#####
#####    Other Functions
#####
##############
def show_user_menu(request):
	if not request.user.is_authenticated():
		return render_to_response('homepage.html')
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		return render_to_response('homepage.html', dict)
		
def create_request(request):
	action_id = request.POST['action_id']
	reqd_by_id = request.POST['reqd_by_id']
	reqd_ins = request.POST['reqd_ins']
	p1 = request.POST['p1']
	p2 = reqest.POST['p2']
	p3 = request.POST['p3']
	p4 = reqest.POST['p4']
	p5 = request.POST['p5']
	p6 = reqest.POST['p6']
	a = Action.objects.get(id=action_id)
	rb = StaffMember.objects.get(id=reqd_by_id)
	h = HistoryItem(action=a, reqd_by=rb, reqd_instructions=reqd_ins, param_1=p1, param_2=p2, param_3=p3, param_4=p4, param_5=p5, param_6=p6)
	h.save()
	return render_to_response('login.html')
	
def get_user_allowed_actions(sm):
	# get all user specific permissions
	permissions = []
	permissions += sm.permissions.all()
	# get the permissions for all groups the user is in
	groups = sm.lab_groups.all()
	for group in groups:
		permissions += group.permissions.all()
	
	# get the actions associated with those permissions
	actions = []
	for permission in permissions:
		actions += permission.actions.all()
	actions = list(set(actions))
	return actions
	
register = template.Library()

@register.filter
@stringfilter
def qrcode(value, alt=None):
    
    url = conditional_escape("http://chart.apis.google.com/chart?%s" % \
            urllib.urlencode({'chs':'150x150', 'cht':'qr', 'chl':value, 'choe':'UTF-8'}))
    alt = conditional_escape(alt or value)
    
    return mark_safe(u"""<img class="qrcode" src="%s" width="150" height="150" alt="%s" />""" % (url, alt))
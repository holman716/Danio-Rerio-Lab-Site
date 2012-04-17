from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response
from django.http import *
from fish.labinterface.models import *
from fish.labinterface.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django import template
from django.db.models import Max

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
					new.location = form.cleaned_data['location']
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
		return HttpResponseRedirect('/login/?next=')
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
				type = form.cleaned_data['type']
				new = ProductType(type=type)
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
					type = form.cleaned_data['type']
					pk = form.cleaned_data['pk']
					new = ProductType.objects.filter(pk=pk).get()
					new.type = type
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = ProductType.objects.filter(pk=selection).get()
				initial = {'type': to_edit.type, 'pk': to_edit.pk}
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
				linecode = form.cleaned_data['line']
				line2code = form.cleaned_data['line2']
				line = Line.objects.filter(barcode__exact=linecode).get()
				line2 = Line.objects.filter(barcode__exact=line2code).get()
				type = form.cleaned_data['type']
				container = form.cleaned_data['container']
				active = form.cleaned_data['active']
				owner = form.cleaned_data['owner']
			
				new = {}
				if line == None:
					new = Product(barcode=barcode, name=name, type=type, container=container, active=active, owner=owner)
				elif line2 == None:
					new = Product(barcode=barcode, name=name, line_id=line, type=type, container=container, active=active, owner=owner)
				else:
					new = Product(barcode=barcode, name=name, line_id=line, line2_id=line2, type=type, container=container, active=active, owner=owner)
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
					linecode = form.cleaned_data['line']
					line2code = form.cleaned_data['line2']
					line = Line.objects.filter(barcode__exact=linecode).get()
					line2 = Line.objects.filter(barcode__exact=line2code).get()
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
					initial['line'] = to_edit.line_id.barcode
				if not to_edit.line2_id == None:
					initial['line2'] = to_edit.line2_id.barcode
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
			if obj.line2_id == None:
				dict['line2_id'] = "None"
			else: 
				dict['line2_id'] = obj.line2_id
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

def addContainerType(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddContainerTypeForm(request.POST)
			if form.is_valid():
				# process form data
				type = form.cleaned_data['type']
			
				newcontainer = {}
				newcontainer = Container_types(type=type)
				newcontainer.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddContainerTypeForm()
		dict['form'] = form
		dict['action_slug'] = "addcontainer"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editContainerType(request):
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
				form = AddContainerTypeForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = Container_types.objects.filter(pk=pk).get()
					
					new.type = form.cleaned_data['type']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Container_types.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'type': to_edit.type}
				form = AddContainerTypeForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectContainerTypeForm()
		dict['form'] = form
		dict['action_slug'] = "editcontainer"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addAlleleType(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddAlleleTypeForm(request.POST)
			if form.is_valid():
				# process form data
				type = form.cleaned_data['type']
				if (type == 'insertion' or type == 'deletion'):
					size = form.cleaned_data['size']
				else:
					size = 0
				orientation = form.cleaned_data['orientation']
			
				newallalle = {}
				newallalle = Allele_type(type=type, size=size, orientation=orientation)
				newallalle.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddAlleleTypeForm()
		dict['form'] = form
		dict['action_slug'] = "addalleletype"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editAlleleType(request):
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
				form = AddAlleleTypeForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = Allele_type.objects.filter(pk=pk).get()
					
					new.type = form.cleaned_data['type']
					if (new.type == 'insertion' or new.type == 'deletion'):
						new.size = form.cleaned_data['size']
					else:
						new.size = 0
					new.orientation = form.cleaned_data['orientation']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Allele_type.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'type': to_edit.type,'size': to_edit.size,'orientation': to_edit.orientation}
				form = AddAlleleTypeForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectAlleleTypeForm()
		dict['form'] = form
		dict['action_slug'] = "editalleletype"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addInsertName(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddInsertNameForm(request.POST)
			if form.is_valid():
				# process form data
				name = form.cleaned_data['name']
				creator = form.cleaned_data['creator']
				ref_number = form.cleaned_data['ref_number']
				sequence = form.cleaned_data['sequence']
			
				newname = {}
				newname = Insert_name(name=name, creator=creator, ref_number=ref_number, sequence=sequence)
				newname.save()
				
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddInsertNameForm()
		dict['form'] = form
		dict['action_slug'] = "addinsertname"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editInsertName(request):
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
				form = AddInsertNameForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					new = Insert_name.objects.filter(pk=pk).get()
					
					new.name = form.cleaned_data['name']
					new.creator = form.cleaned_data['creator']
					new.ref_number = form.cleaned_data['ref_number']
					new.sequence = form.cleaned_data['sequence']
					new.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Insert_name.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'name': to_edit.name,'creator': to_edit.creator,'ref_number': to_edit.ref_number,'sequence': to_edit.sequence}
				form = AddInsertNameForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectInsertNameForm()
		dict['form'] = form
		dict['action_slug'] = "editinsertname"
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

def splitLineInitial(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		dict['definesHeader'] = True
		dict['header'] = ""
		initial = {'lineBarcode': str(id), 'step' : 'First'}
		form = SplitLineInitialForm(initial = initial)
		dict['form'] = form
		dict['action_slug'] = "splitline"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))


def splitLine(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			step = request.POST.get('step')
			lineBarcode = request.POST.get('lineBarcode')
			if step <> 'Final':
				product_Type_Number = request.POST.get('product_Type')
				product_container_number = request.POST.get('product_container')
				product_Type = ProductType.objects.filter(pk=product_Type_Number).get()
				product_container = Container_types.objects.filter(pk=product_container_number).get()
			if step == 'First': #After initial set up is done this will run and direct to the right place
				type = request.POST.get('split_Type')
				if type == 'S': #User selected singles
					initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type_Number, 'product_container': product_container_number, 'step' : 'Singles'}
					form = SplitLineSinglesForm(initial = initial)
				elif type == 'G': #User selected groups
					initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type_Number, 'product_container': product_container_number, 'step' : 'Group', 'groupNum' : 1}
					dict['definesHeader'] = True
					dict['header'] = "Group split #" + str(1)
					form = SplitLineGroupsForm(initial = initial)
					dict['groupNum'] = 1
			elif step == 'Singles': #Singles information complete
				try:
					#check validity
					initialBarcode = int(request.POST.get('first_Barcode'))
					initialProductBarcode = int(request.POST.get('first_product_Barcode'))
					totalBarcodes = int(request.POST.get('quantity'))
					for x in range(initialBarcode,totalBarcodes+initialBarcode):
						try:
							barcodeFound = Barcode.objects.filter(pk=x).get()
						except:
							raise Exception, 'Not enough barcodes to facilitate split'
						if (barcodeFound.used):
							raise Exception, 'Not all barcodes are unused'
					for x in range(initialProductBarcode,totalBarcodes+initialProductBarcode):
						try:
							barcodeFound = Barcode.objects.filter(pk=x).get()
						except:
							raise Exception, 'Not enough barcodes to facilitate split'
						if (barcodeFound.used):
							raise Exception, 'Not all barcodes are unused'
					if ((initialBarcode <= initialProductBarcode and totalBarcodes+initialBarcode > initialProductBarcode) 
					or (initialProductBarcode <= initialBarcode and totalBarcodes+initialProductBarcode > initialBarcode)):
						raise Exception, 'Barcodes overlap'
					#create splits
					location = request.POST.get('location')
					containerNumber = request.POST.get('container')
					container = Container_types.objects.filter(pk=containerNumber).get()
					active = request.POST.get('active') == 'on'
					old = Line.objects.filter(barcode__exact=lineBarcode).get()
					for n in range(0,totalBarcodes):
						x = initialBarcode + n
						y = initialProductBarcode + n
						#Create Line
						newline = {}
						if old.parent == None:
							newline = Line(barcode=x ,name=old.name + ' : ' + str(x), IACUC_ID=old.IACUC_ID, raised=old.raised, original_quantity=1, current_quantity=1, container=container, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
						else:
							newline = Line(barcode=x ,name=old.name + ' : ' + str(x), IACUC_ID=old.IACUC_ID, raised=old.raised, parent=old.parent, original_quantity=1, current_quantity=1, container=container, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
						newline.save()
						#Create Product
						modelNewLine = Line.objects.filter(barcode__exact=x).get()
						newProduct = {}
						newProduct = Product(barcode=y, line_id=modelNewLine, type=product_Type, container=product_container, active=active, owner=sm)
						newProduct.save()

						barcodeObject = Barcode.objects.filter(pk=x).get()
						productBarcodeObject = Barcode.objects.filter(pk=y).get()
						barcodeObject.used = True
						barcodeObject.used = True
						productBarcodeObject.used = True
						barcodeObject.save()
						productBarcodeObject.save()
					#raise Exception, 'Test was successful (or failure, depending on your view)'
					initial = {'lineBarcode': lineBarcode, 'step' : 'Final'}
					form = SplitLineFinalForm(initial = initial)
				except Exception, ex:
					initial = {'selection' : ex}
					form = EnterBarcodeForm(initial=initial)
					#initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type, 'product_container': product_container, 'step' : 'Singles'}
					#form = SplitLineSinglesForm(initial = initial)
			elif step == 'Group': #Group information recieved
				try:
					#check validity
					newLineBarcode = int(request.POST.get('newLineBarcode'))
					productBarcode = int(request.POST.get('product_Barcode'))
					try:
						lineBarcodeFound = Barcode.objects.filter(pk=newLineBarcode).get()
					except:
						raise Exception, 'Not enough barcodes to facilitate split'
					if (lineBarcodeFound.used):
						raise Exception, 'Not all barcodes are unused'
					try:
						productBarcodeFound = Barcode.objects.filter(pk=productBarcode).get()
					except:
						raise Exception, 'Not enough barcodes to facilitate split'
					if (productBarcodeFound.used):
						raise Exception, 'Not all barcodes are unused'
					if (newLineBarcode == productBarcode):
						raise Exception, 'Barcodes overlap'
					#create splits
					location = request.POST.get('location')
					lineContainernumber = request.POST.get('container')
					lineContainer = Container_types.objects.filter(pk=lineContainernumber).get()
					active = request.POST.get('active') == 'on'
					old = Line.objects.filter(barcode__exact=lineBarcode).get()
					#Create Line
					newline = {}
					if old.parent == None:
						newline = Line(barcode=newLineBarcode ,name=old.name + ' : ' + str(newLineBarcode), IACUC_ID=old.IACUC_ID, raised=old.raised, original_quantity=1, current_quantity=1, container=lineContainer, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
					else:
						newline = Line(barcode=newLineBarcode ,name=old.name + ' : ' + str(newLineBarcode), IACUC_ID=old.IACUC_ID, raised=old.raised, parent=old.parent, original_quantity=1, current_quantity=1, container=lineContainer, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
					newline.save()
					#Create Product
					modelNewLine = Line.objects.filter(barcode__exact=newLineBarcode).get()
					newProduct = {}
					newProduct = Product(barcode=productBarcode, line_id=modelNewLine, type=product_Type, container=product_container, active=active, owner=sm)
					newProduct.save()

					#Indicate barcodes used
					barcodeObject = Barcode.objects.filter(pk=newLineBarcode).get()
					productBarcodeObject = Barcode.objects.filter(pk=productBarcode).get()
					barcodeObject.used = True
					barcodeObject.used = True
					productBarcodeObject.used = True
					barcodeObject.save()
					productBarcodeObject.save()

					final = request.POST.get('final')
					if final: #Last bit of group info recieved
						initial = {'lineBarcode': lineBarcode, 'step' : 'Final'}
						form = SplitLineFinalForm(initial = initial)
					else: #More group information to come 
						nextNum = str(int(request.POST.get('groupNum')) +1)
						dict['groupNum'] = nextNum
						dict['definesHeader'] = True
						dict['header'] = "Group split #" + str(nextNum)
						initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type_Number, 'product_container': product_container_number, 'step' : 'Group', 'groupNum' : nextNum}
						form = SplitLineGroupsForm(initial = initial)
				except Exception, ex:
					nextNum = str(int(request.POST.get('groupNum')))
					dict['groupNum'] = nextNum
					dict['definesHeader'] = True
					dict['header'] = "Group split #" + str(nextNum) + " --" + str(ex) + "-- "
					initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type_Number, 'product_container': product_container_number, 'step' : 'Group', 'groupNum' : nextNum}
					form = SplitLineGroupsForm(initial = initial)
			elif step == 'Final': #Final info recieved
				try:
					newQuantity = int(request.POST.get('current_quantity'))
					newLocation = request.POST.get('location')
					newContainerNumber = request.POST.get('container')
					newContainer = Container_types.objects.filter(pk=newContainerNumber).get()
					active = request.POST.get('active') == 'on'
					oldLine = Line.objects.filter(barcode__exact=lineBarcode).get()
					oldLine.current_quantity = newQuantity
					oldLine.container = newContainer
					oldLine.location = newLocation
					oldLine.active = active
					oldLine.save()
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
				except:
					initial = {'lineBarcode': lineBarcode, 'step' : 'Final'}
					form = SplitLineFinalForm(initial = initial)
			else: #Something went wrong here
				initial = {'selection' : step}
				form = EnterBarcodeForm(initial=initial)
			dict['form'] = form
			dict['action_slug'] = "splitline"
			return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addBarcodes(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			quantity = int(request.POST.get('quantity'))
			lastUsed = int(Barcode.objects.all().aggregate(Max('id'))['id__max'])
			for x in range(1,quantity+1):
				newBarcode = {}
				newBarcode = Barcode(id=lastUsed+x, used=False)
				newBarcode.save()
			dict['definesHeader'] = True
			dict['header'] = "Created " + str(quantity) + " barcodes starting at " + str(lastUsed+1) + " and ending at " + str(lastUsed+quantity)
			return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			# choosing what object to edit
			form = PrintBarcodeForm()
			dict['form'] = form
			dict['action_slug'] = "addbarcodes"
			return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addMating(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			# process form data
			typeM = request.POST.get('typeM')
			barcodeMale = request.POST.get('barcodeMale')
			if (typeM == 'Line'):
				line = Line.objects.filter(barcode__exact=barcodeMale).get()
			else:
				line = Product.objects.filter(barcode__exact=barcodeMale).get().line_id
			typeF = request.POST.get('typeF')
			barcodeFemale = request.POST.get('barcodeFemale')
			if (barcodeFemale == ''):
				line2 = None
			elif (typef == 'Line'):
				line2 = Line.objects.filter(barcode__exact=barcodeFemale).get()
			else:
				line2 = Product.objects.filter(barcode__exact=barcodeFemale).get().line_id
			quantity = request.POST.get('quantity')
			firstBarcode = request.POST.get('firstBarcode')
			#Get type info
			#get container info
			
			new = {}
			if line == None:
				new = Product(barcode=firstBarcode, type=type, container=container, active=False, owner=sm)
			elif line2 == None:
				new = Product(barcode=firstBarcode, line_id=line, type=type, container=container, active=False, owner=sm)
			else:
				new = Product(barcode=firstBarcode, line_id=line, line2_id=line2, type=type, container=container, active=False, owner=sm)
			new.save()
				
			return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			dict['action_slug'] = "addmating"
			return render_to_response('matingform.html', dict, context_instance=RequestContext(request))

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
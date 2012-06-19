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
import csv
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from datetime import date
from datetime import timedelta

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
				#validate barcodes
				barcode = form.cleaned_data['barcode']
				try:
						try:
							barcodeFound = Barcode.objects.filter(pk=barcode).get()
						except:
							raise Exception, 'Barcode has not been registered with database'
						if (barcodeFound.used):
							raise Exception, 'Barcode already in use'
				except Exception, ex:
						dict['definesHeader'] = True
						dict['header'] = "Error encountered: " + str(ex)
						initial = {'name': form.cleaned_data['name'], 'barcode': form.cleaned_data['barcode'],'IACUC_ID': form.cleaned_data['IACUC_ID'], 'raised': form.cleaned_data['raised'],'current_quantity': form.cleaned_data['current_quantity'],'original_quantity': form.cleaned_data['original_quantity'], 'container': form.cleaned_data['container'], 'sex': form.cleaned_data['sex'], 'active': form.cleaned_data['active'], 'strain': form.cleaned_data['strain'],'location': form.cleaned_data['location'],'birthdate': form.cleaned_data['birthdate']}
						dict['form'] = AddLineForm(initial=initial)
						dict['action_slug'] = "addline"
						return render_to_response('form.html', dict, context_instance=RequestContext(request))
				# process form data
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
				create_HistoryItem('Add Line', sm, False, '', True, [newline.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			initial = {'owner': sm}
			form = AddLineForm(initial=initial)
		dict['form'] = form
		dict['action_slug'] = "addline"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def editLineByBarcode(request,id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		try:
			to_edit = Line.objects.filter(barcode__exact=id).get()
			initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode,'IACUC_ID': to_edit.IACUC_ID, 'raised': to_edit.raised,'current_quantity': to_edit.current_quantity,'original_quantity': to_edit.original_quantity, 'container': to_edit.container, 'sex': to_edit.sex, 'active': to_edit.active, 'strain': to_edit.strain, 'location': to_edit.location, 'birthdate': to_edit.birthdate, 'owner': to_edit.owner}
			if not to_edit.parent == None:
				initial['parent'] = to_edit.parent.pk
		except Exception, ex:
			dict['definesHeader'] = True
			dict['header'] = "Error encountered: Barcode not valid"
			dict['form'] = EnterBarcodeForm()
			dict['action_slug'] = "editline"
			return render_to_response('form.html', dict, context_instance=RequestContext(request))
		form = AddLineForm(initial=initial)
		dict['form'] = form
		dict['action_slug'] = "editline"
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
					#validate barcodes
					pk = form.cleaned_data['pk']
					new = Line.objects.filter(pk=pk).get()
					barcode = form.cleaned_data['barcode']
					try:
						try:
							barcodeFound = Barcode.objects.filter(pk=barcode).get()
						except:
							raise Exception, 'Barcode has not been registered with database'
						if (barcodeFound.used and new.barcode <> barcodeFound.id):
							raise Exception, 'Cannot overwrite another barcode'
						elif(not barcodeFound.used):
							oldBarcode = Barcode.objects.filter(pk=new.barcode).get()
							oldBarcode.used = False
							oldBarcode.save()
							barcodeFound.used = True
							barcodeFound.save()
					except Exception, ex:
						dict['definesHeader'] = True
						dict['header'] = "Error encountered: " + str(ex)
						to_edit = Line.objects.filter(pk=pk).get()
						initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode,'IACUC_ID': to_edit.IACUC_ID, 'raised': to_edit.raised,'current_quantity': to_edit.current_quantity,'original_quantity': to_edit.original_quantity, 'container': to_edit.container, 'sex': to_edit.sex, 'active': to_edit.active, 'strain': to_edit.strain, 'owner': to_edit.owner}
						dict['form'] = AddLineForm(initial=initial)
						dict['action_slug'] = "editline"
						return render_to_response('form.html', dict, context_instance=RequestContext(request))
					# process form data					
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
					create_HistoryItem('Edit Line', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				try:
					to_edit = Line.objects.filter(barcode__exact=selection).get()
					initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode,'IACUC_ID': to_edit.IACUC_ID, 'raised': to_edit.raised,'current_quantity': to_edit.current_quantity,'original_quantity': to_edit.original_quantity, 'container': to_edit.container, 'sex': to_edit.sex, 'active': to_edit.active, 'strain': to_edit.strain, 'location': to_edit.location, 'birthdate': to_edit.birthdate, 'owner': to_edit.owner}
					if not to_edit.parent == None:
						initial['parent'] = to_edit.parent.pk
				except Exception, ex:
					dict['definesHeader'] = True
					dict['header'] = "Error encountered: Barcode not valid"
					dict['form'] = EnterBarcodeForm()
					dict['action_slug'] = "editline"
					return render_to_response('form.html', dict, context_instance=RequestContext(request))
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
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'GET':
			selection = request.GET.get('barcode')
			try:
				line = Line.objects.filter(barcode=selection).get()
				return HttpResponseRedirect('/action/viewline/%s' % line.barcode)
			except:
				try:
					product = Product.objects.filter(barcode=selection).get()
					return HttpResponseRedirect('/action/viewproduct/%s' % product.barcode)
				except:
					dict['definesHeader'] = True
					dict['header'] = "Error encountered: Barcode not valid"
					return render_to_response('homepage.html', dict, context_instance=RequestContext(request))


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
		dict['genomes'] = obj.genomes.all()
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
				create_HistoryItem('Add Product Type', sm, False, '', True, [new.id])
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
					oldType = new.type
					new.type = type
					new.save()
					create_HistoryItem('Edit Product Type', sm, False, oldType+' -> '+type, True, [new.id])
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
				line2code = form.cleaned_data['line2'] or None
				line = Line.objects.filter(barcode__exact=linecode).get()
				if (line2code):
					line2 = Line.objects.filter(barcode__exact=line2code).get()
				else:
					line2 = None
				type = form.cleaned_data['type']
				container = form.cleaned_data['container']
				active = form.cleaned_data['active']
				owner = form.cleaned_data['owner']
				
				#validate barcode
				barcode = form.cleaned_data['barcode']
				try:
					try:
						barcodeFound = Barcode.objects.filter(pk=barcode).get()
					except:
						raise Exception, 'Barcode has not been registered with database'
					if (barcodeFound.used):
						raise Exception, 'Barcode already in use'
				except Exception, ex:
					dict['definesHeader'] = True
					dict['header'] = "Error encountered: " + str(ex)
					initial = {'name': name, 'barcode': barcode, 'line': linecode, 'line2': line2code, 'type': type, 'container': container,'active': active, 'owner':owner}
					dict['form'] = AddProductForm(initial=initial)
					dict['action_slug'] = "addproduct"
					return render_to_response('form.html', dict, context_instance=RequestContext(request))

				# Save data
				new = {}
				if line == None:
					new = Product(barcode=barcode, name=name, type=type, container=container, active=active, owner=owner)
				elif line2 == None:
					new = Product(barcode=barcode, name=name, line_id=line, type=type, container=container, active=active, owner=owner)
				else:
					new = Product(barcode=barcode, name=name, line_id=line, line2_id=line2, type=type, container=container, active=active, owner=owner)
				new.save()
				barcodeFound.used=True
				barcodeFound.save()
				create_HistoryItem('Add Product', sm, False, '', True, [new.id])
				
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

					#validate barcode
					try:
						try:
							barcodeFound = Barcode.objects.filter(pk=barcode).get()
						except:
							raise Exception, 'Barcode has not been registered with database'
						if (barcodeFound.used and new.barcode <> barcodeFound.id):
							raise Exception, 'Cannot overwrite another barcode'
						elif(not barcodeFound.used):
							oldBarcode = Barcode.objects.filter(pk=new.barcode).get()
							oldBarcode.used = False
							oldBarcode.save()
							barcodeFound.used = True
							barcodeFound.save()
					except Exception, ex:
						dict['definesHeader'] = True
						dict['header'] = "Error encountered: " + str(ex)
						to_edit = Product.objects.filter(pk=new.id).get()
						initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode, 'type': to_edit.type.pk, 'container': to_edit.container,'active': to_edit.active, 'owner':to_edit.owner}
						if not to_edit.line_id == None:
							initial['line'] = to_edit.line_id.barcode
						if not to_edit.line2_id == None:
							initial['line2'] = to_edit.line2_id.barcode
						form = AddProductForm(initial=initial)
						dict['form'] = AddProductForm(initial=initial)
						dict['action_slug'] = "editproduct"
						return render_to_response('form.html', dict, context_instance=RequestContext(request))

					#Save Form Data
					new.name = name
					new.barcode = barcode
					new.type = type
					new.container = container
					new.active = active
					new.line_id = line
					new.owner = owner
					new.save()
					create_HistoryItem('Edit Product', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				try:
					to_edit = Product.objects.filter(barcode__exact=selection).get()
					initial = {'name': to_edit.name, 'pk': to_edit.pk, 'barcode': to_edit.barcode, 'type': to_edit.type.pk, 'container': to_edit.container,'active': to_edit.active, 'owner':to_edit.owner}
					if not to_edit.line_id == None:
						initial['line'] = to_edit.line_id.barcode
					if not to_edit.line2_id == None:
						initial['line2'] = to_edit.line2_id.barcode
				except Exception, ex:
					dict['definesHeader'] = True
					dict['header'] = "Error encountered: Barcode not valid"
					dict['form'] = EnterBarcodeForm()
					dict['action_slug'] = "editproduct"
					return render_to_response('form.html', dict, context_instance=RequestContext(request))
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
				name = form.cleaned_data['name']
				version = form.cleaned_data['version']
				chromosome = form.cleaned_data['chromosome']
				position = form.cleaned_data['position']
				allele_type = form.cleaned_data['allele_type']
			
				newgenome = {}
				newgenome = GeneticElement(name=name, version=version, chromosome=chromosome, position=position, allele_type=allele_type)
				newgenome.save()
				create_HistoryItem('Add Genome', sm, False, '', True, [newgenome.id])
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
					
					new.name = form.cleaned_data['name']
					new.version = form.cleaned_data['version']
					new.chromosome = form.cleaned_data['chromosome']
					new.position = form.cleaned_data['position']
					new.allele_type = form.cleaned_data['allele_type']
					new.save()
					create_HistoryItem('Edit Genome', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = GeneticElement.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'name': to_edit.name, 'version': to_edit.version, 'chromosome': to_edit.chromosome,'position': to_edit.position, 'allele_type': to_edit.allele_type}
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
				create_HistoryItem('Add Genome Version', sm, False, '', True, [newgenome.id])
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
					oldName = new.name
					new.name = form.cleaned_data['name']
					new.save()
					create_HistoryItem('Edit Genome Version', sm, False, oldName+' -> '+new.name, True, [new.id])
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

def addReagent(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddReagentForm(request.POST)
			if form.is_valid():
				# process form data
				description = form.cleaned_data['description']
				container = form.cleaned_data['container']
			
				newreagent = {}
				if container == None:
					newreagent = Reagent(description=description)
				else:
					newreagent = Reagent(description=description, container=container)
				newreagent.save()
				create_HistoryItem('Add Reagent', sm, False, '', True, [newreagent.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddReagentForm()
		dict['form'] = form
		dict['action_slug'] = "addreagent"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editReagent(request):
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
				form = AddReagentForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					description = form.cleaned_data['description']
					container = form.cleaned_data['container']

					new = Reagent.objects.filter(pk=pk).get()
					new.description = description
					new.container = container
					new.save()
					create_HistoryItem('Edit Reagent', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Reagent.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'description': to_edit.description,'container': to_edit.container}
				form = AddReagentForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectReagentForm()
		dict['form'] = form
		dict['action_slug'] = "editreagent"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def addContainer(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			form = AddContainerForm(request.POST)
			if form.is_valid():
				# process form data
				description = form.cleaned_data['description']
				type = form.cleaned_data['type']
				container = form.cleaned_data['container']
			
				newcontainer = {}
				if container == None:
					newcontainer = Container(description=description, type=type)
				else:
					newcontainer = Container(description=description, type=type, containedIn=container)
				newcontainer.save()
				create_HistoryItem('Add Container', sm, False, '', True, [newcontainer.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddContainerForm()
		dict['form'] = form
		dict['action_slug'] = "addcontainer"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))
		
def editContainer(request):
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
				form = AddContainerForm(request.POST)
				if form.is_valid():
					# process form data
					pk = form.cleaned_data['pk']
					description = form.cleaned_data['description']
					type = form.cleaned_data['type']
					container = form.cleaned_data['container']

					new = Container.objects.filter(pk=pk).get()
					new.description = description
					new.type = type
					new.containedIn = container
					new.save()
					create_HistoryItem('Edit Container', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Container.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk,'description': to_edit.description,'type': to_edit.type,'container': to_edit.containedIn}
				form = AddContainerForm(initial=initial)
		else:
			# choosing what object to edit
			form = SelectContainerForm()
		dict['form'] = form
		dict['action_slug'] = "editcontainer"
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
				create_HistoryItem('Add Container Type', sm, False, '', True, [newcontainer.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddContainerTypeForm()
		dict['form'] = form
		dict['action_slug'] = "addcontainertype"
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
					oldType = new.type
					new.type = form.cleaned_data['type']
					new.save()
					create_HistoryItem('Edit Container Type', sm, False, oldType+' -> '+new.type, True, [new.id])
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
		dict['action_slug'] = "editcontainertype"
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
				description = form.cleaned_data['description']
				if (type == 'deletion'):
					size = form.cleaned_data['size']
					orientation = form.cleaned_data['orientation']
				else:
					size = None
					orientation = None
				if (type == 'insertion'):
					insert_name = form.cleaned_data['insert_name']
				else:
					insert_name = None
			
				newallalle = {}
				newallalle = Allele_type(description=description, type=type, size=size, orientation=orientation, insert_name=insert_name)
				newallalle.save()
				create_HistoryItem('Add Allele Type', sm, False, '', True, [newallalle.id])
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
					
					new.description = form.cleaned_data['description']
					new.type = form.cleaned_data['type']
					if (new.type == 'insertion' or new.type == 'deletion'):
						new.size = form.cleaned_data['size']
					else:
						new.size = 0
					new.orientation = form.cleaned_data['orientation']
					new.save()
					create_HistoryItem('Edit Allele Type', sm, False, '', True, [new.id])
					return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				# bringing up the edit page
				to_edit = Allele_type.objects.filter(pk=selection).get()
				initial = {'pk': to_edit.pk, 'description': to_edit.description,'type': to_edit.type,'size': to_edit.size,'orientation': to_edit.orientation,'insert_name': to_edit.insert_name}
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
				create_HistoryItem('Add Insert Name', sm, False, '', True, [newname.id])
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
					oldName = new.name
					new.name = form.cleaned_data['name']
					new.creator = form.cleaned_data['creator']
					new.ref_number = form.cleaned_data['ref_number']
					new.sequence = form.cleaned_data['sequence']
					new.save()
					create_HistoryItem('Edit Insert Name', sm, False, oldName+' -> '+new.name, True, [new.id])
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
				create_HistoryItem('Add Genome Association', sm, False, '', True, [line.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			form = AddGenomeAssociationForm()
		dict['form'] = form
		dict['action_slug'] = "addgenomeassociation"
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def removeGenomeAssociation(request, line, genome):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			# process form data
			confirmed = request.POST.get('selection') == 'on'
			if confirmed:
				lineObject = Line.objects.filter(barcode__exact=line).get()
				for x in lineObject.genomes.all():
					if str(x.id) == str(genome):
						genomeObject=x
				lineObject.genomes.remove(genomeObject)
				lineObject.save()
				create_HistoryItem('Remove Genome Association', sm, False, '', True, [lineObject.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				dict['definesHeader'] = True
				dict['header'] = "Genome not removed"
				return render_to_response('message.html', dict, context_instance=RequestContext(request))
		else:
			try:
				valid = False
				lineObject = Line.objects.filter(barcode__exact=line).get()
				for x in lineObject.genomes.all():
					if str(x.id) == str(genome):
						genomeObject=x
						valid = True
			except:
				valid = False
			if valid:
				dict['definesHeader'] = True
				dict['header'] = "Removing \"" + str(genomeObject) + "\" from \"" + lineObject.name + "\"?"
				form = ConfirmActionForm()
			else:
				dict['definesHeader'] = True
				dict['header'] = "Invalid line/genome pair"
				return render_to_response('message.html', dict, context_instance=RequestContext(request))
		dict['form'] = form
		dict['action_slug'] = "removegenomeassociation/" + str(line) + "&" + str(genome)
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
					initial = {'lineBarcode': request.POST.get('lineBarcode'), 'product_Type': request.POST.get('product_Type'), 'product_container': request.POST.get('product_container'), 'first_Barcode': request.POST.get('first_Barcode'), 'first_product_Barcode': request.POST.get('first_product_Barcode'), 'quantity': request.POST.get('quantity'), 'location': request.POST.get('location'), 'container': request.POST.get('container'), 'active': request.POST.get('active'), 'step' : 'Singles'}
					dict['definesHeader'] = True
					dict['header'] = "Error: " + str(ex)
					form = SplitLineSinglesForm(initial = initial)
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
					quantity = request.POST.get('quantity')
					location = request.POST.get('location')
					lineContainernumber = request.POST.get('container')
					lineContainer = Container_types.objects.filter(pk=lineContainernumber).get()
					active = request.POST.get('active') == 'on'
					old = Line.objects.filter(barcode__exact=lineBarcode).get()
					#Create Line
					newline = {}
					if old.parent == None:
						newline = Line(barcode=newLineBarcode ,name=old.name + ' : ' + str(newLineBarcode), IACUC_ID=old.IACUC_ID, raised=old.raised, original_quantity=quantity, current_quantity=quantity, container=lineContainer, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
					else:
						newline = Line(barcode=newLineBarcode ,name=old.name + ' : ' + str(newLineBarcode), IACUC_ID=old.IACUC_ID, raised=old.raised, parent=old.parent, original_quantity=quantity, current_quantity=quantity, container=lineContainer, location=location, sex=old.sex, active=active, strain=old.strain, birthdate=old.birthdate, owner=old.owner)
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
					dict['header'] = "Group split #" + str(nextNum) + " --- Error:" + str(ex)
					initial = {'lineBarcode': lineBarcode, 'product_Type': product_Type_Number, 'product_container': product_container_number, 'quantity': request.POST.get('quantity'), 'newLineBarcode': request.POST.get('newLineBarcode'), 'product_Barcode': request.POST.get('product_Barcode'), 'location': request.POST.get('location'), 'container': request.POST.get('container'), 'active': request.POST.get('active'),  'step' : 'Group', 'groupNum' : nextNum}
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
					create_HistoryItem('Split Line', sm, False, '', True, [oldLine.id])
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
			try:
				lastUsed = int(Barcode.objects.all().aggregate(Max('id'))['id__max'])
			except:
				lastUsed = 0
			for x in range(1,quantity+1):
				newBarcode = {}
				newBarcode = Barcode(id=lastUsed+x, used=False)
				newBarcode.save()
			create_HistoryItem('Add Barcodes', sm, False, '', True, [quantity])
			dict['definesHeader'] = True
			dict['header'] = "Created " + str(quantity) + " barcodes starting at " + str(lastUsed+1) + " and ending at " + str(lastUsed+quantity)
			return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			# choosing what object to edit
			form = PrintBarcodeForm()
			barcodes = Barcode.objects.filter(used__exact=False).all()
			available = []
			for x in barcodes:
				available.append(x.id)
			available.sort
			dict['available'] = available
			if available.count > 0:
				dict['number'] = len(available)
				dict['minimum'] = available[0]
				dict['maximum'] = available[len(available)-1]
			else:
				dict['number'] = 0
				dict['minimum'] = 0
				dict['maximum'] = 0
			dict['form'] = form
			dict['action_slug'] = "addbarcodes"
			return render_to_response('barcodeform.html', dict, context_instance=RequestContext(request))

def addMating(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		if request.method == 'POST':
			##Validate barcodes
			#quantity = int(request.POST.get('quantity'))
			#firstBarcode = int(request.POST.get('firstBarcode'))
			#try:
			#	for x in range(firstBarcode,quantity+firstBarcode):
			#			try:
			#				barcodeFound = Barcode.objects.filter(pk=x).get()
			#			except:
			#				raise Exception, 'Barcode has not been registered with database'
			#			if (barcodeFound.used):
			#				raise Exception, 'Barcode already in use'
			#except Exception, ex:
			#		dict['definesHeader'] = True
			#		dict['header'] = "Error encountered: " + str(ex)
			#		dict['form'] = AddMatingForm()
			#		dict['action_slug'] = "addmating"
			#		return render_to_response('matingform.html', dict, context_instance=RequestContext(request))

			# process form data
			matingType = typeM = request.POST.get('matingType')
			typeM = request.POST.get('typeM')
			barcodeMale = request.POST.get('barcodeMale')
			if (typeM == 'Line'):
				line = Line.objects.filter(barcode__exact=barcodeMale).get()
			else:
				line = Product.objects.filter(barcode__exact=barcodeMale).get().line_id
			typeF = request.POST.get('typeF')
			barcodeFemale = request.POST.get('barcodeFemale')
			if (barcodeFemale == '' or matingType == 'in'):
				line2 = None
			elif (typeF == 'Line'):
				line2 = Line.objects.filter(barcode__exact=barcodeFemale).get()
			else:
				line2 = Product.objects.filter(barcode__exact=barcodeFemale).get().line_id
			#type =  ProductType.objects.filter(type__exact='Mating').get()
			#containerID = request.POST.get('container')
			#container = Container_types.objects.filter(pk=containerID).get()
			#get container info
			
			#for x in range(firstBarcode,quantity+firstBarcode):
				#new = {}
				#if line == None:
				#	new = Product(barcode=str(x), type=type, container=container, active=False, owner=sm)
				#elif line2 == None:
				#	new = Product(barcode=str(x), line_id=line, type=type, container=container, active=False, owner=sm)
				#else:
				#	new = Product(barcode=str(x), line_id=line, line2_id=line2, type=type, container=container, active=False, owner=sm)
				#new.save()
				#barcode = Barcode.objects.filter(pk=x).get()
				#barcode.used = True
				#barcode.save()
			dueDate = date.today() + timedelta(days=1)

			if (line2 == None):
				create_HistoryItem('Add Mating', sm, False, 'Added in-cross; '+line.name, True, [line.id])
				create_HistoryItem('Take Down Mating', sm, dueDate, 'Take down mating; '+line.name, False, [line.id])
			else:
				create_HistoryItem('Add Mating', sm, False, 'Added out-cross; '+line.name+' x '+line2.name, True, [line.id,line2.id])
				create_HistoryItem('Take Down Mating', sm, dueDate, 'Take down mating; '+line.name+' x '+line2.name, False, [line.id,line2.id])
			return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			dict['action_slug'] = "addmating"
			return render_to_response('matingform.html', dict, context_instance=RequestContext(request))

def historyTable(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		todoHistory = []
		todoHistory += HistoryItem.objects.filter(finished__exact=False).all()
		todoHistory.sort(key=lambda x: x.reqd_date)
		finishedHistory = []
		finishedHistory += HistoryItem.objects.filter(finished__exact=True).all()
		finishedHistory.sort(key=lambda x: x.reqd_date, reverse=True)

		dict['todo_table'] = todoHistory
		dict['finished_table'] = finishedHistory
		
		return render_to_response('history.html', dict, context_instance=RequestContext(request))

def reagentTable(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		reagents = []
		reagents += Reagent.objects.all()
		containers = []
		containers += Container.objects.all()

		dict['reagent_table'] = reagents
		dict['container_table'] = containers
		
		return render_to_response('reagents.html', dict, context_instance=RequestContext(request))

###### TODO ######
def processHistory(request,id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		hi = HistoryItem.objects.filter(id=id).get()

		if hi.action == 'Take Down Mating':
			return takeDownMating(request,id)
		else:
			dict['definesHeader'] = True
			dict['header'] = "Error encountered: History item not valid"
			return render_to_response('homepage.html', dict, context_instance=RequestContext(request))

def takeDownMating(request,id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name
		if request.method == 'POST':
			step = request.POST.get('step')
			hi = HistoryItem.objects.filter(id=id).get()
			outCross = True
			try:
				if (hi.param_2 == ''):
					outCross = False
			except:
				outCross = False
			if step == 'Confirmed':
				# submitting the modification
				line1barcode = request.POST.get('line1')
				line2barcode = request.POST.get('line2')
				barcodeNeeded = request.POST.get('barcode')
				try:
					line1 = Line.objects.filter(barcode__exact=line1barcode).get()
					if (outCross):
						line2 = Line.objects.filter(barcode__exact=line2barcode).get()
				except:
					dict['definesHeader'] = True
					dict['header'] = "Warning: Line barcode/barcodes not valid"
					initial = {'step' : 'Confirmed'}
					dict['form'] = ConfirmLineForm(initial=initial)
					dict['action_slug'] = "processitem/" + str(id)
					return render_to_response('form.html', dict, context_instance=RequestContext(request))
				if (str(line1.id) == str(hi.param_1) and (not outCross or str(line2.id) == str(hi.param_2))):
					if barcodeNeeded == 'on':
						initial = {'step' : 'productBarcodeNeeded'}
						form = EnterBarcodeForm(initial=initial)
					else:
						hi.finished = True
						hi.save()
						if (outCross):
							create_HistoryItem('Promote to Euthinize', sm, date.today() + timedelta(days=7), '', False, [line1.id,line2.id])
						else:
							create_HistoryItem('Promote to Euthinize', sm, date.today() + timedelta(days=7), '', False, [line1.id])
						return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
				elif (str(line1.id) == str(hi.param_2) and str(line2.id) == str(hi.param_1)):
					dict['definesHeader'] = True
					dict['header'] = "Warning: Lines were entered into field in reverse order, please re-enter information"
					initial = {'step' : 'Confirmed'}
					form = ConfirmLineForm(initial=initial)
				else:
					dict['definesHeader'] = True
					dict['header'] = "Warning: Line barcode/barcodes do not match record"
					initial = {'step' : 'Confirmed'}
					form = ConfirmLineForm(initial=initial)
			elif step == 'productBarcodeNeeded':
				line1 = Line.objects.filter(pk=hi.param_1).get()
				if (outCross):
					line2 = Line.objects.filter(pk=hi.param_2).get()
				barcodeFound = request.POST.get('selection')
				product_Type = ProductType.objects.filter(type__exact='Mating').get()
				#validate barcodes
				try:
						try:
							barcodeFound = Barcode.objects.filter(pk=barcodeFound).get()
						except:
							raise Exception, 'Barcode has not been registered with database'
						if (barcodeFound.used):
							raise Exception, 'Barcode already in use'
				except Exception, ex:
						dict['definesHeader'] = True
						dict['header'] = "Error encountered: " + str(ex)
						initial = {'step' : 'productBarcodeNeeded'}
						dict['form'] = EnterBarcodeForm(initial=initial)
						dict['action_slug'] = "processitem/" + str(id)
						return render_to_response('form.html', dict, context_instance=RequestContext(request))
				if (outCross):
					new = Product(barcode=barcodeFound.id, name=line1.name + " : " + line2.name, line_id=line1, line2_id=line2, type=product_Type, active=True, owner=sm)
				else:
					new = Product(barcode=barcodeFound.id, name=line1.name + " in-cross", line_id=line1, type=product_Type, active=True, owner=sm)
				new.save()
				barcodeFound.used=True
				barcodeFound.save()
				hi.finished = True
				hi.save()
				create_HistoryItem('Promote to Line', sm, date.today() + timedelta(days=5), '', False, [new.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				initial = {'step' : 'Confirmed'}
				form = ConfirmLineForm(initial=initial)
		else:
			# choosing what object to edit	
			initial = {'step' : 'Confirmed'}
			form = ConfirmLineForm(initial=initial)
		dict['form'] = form
		dict['action_slug'] = "processitem/" + str(id)
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def viewMyLines(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		active_fish = []
		active_fish += Line.objects.filter(owner__exact=sm).all()
		active_fish.sort(key=lambda x: x.barcode)

		dict['definesHeader'] = True
		dict['activeOny'] = True
		dict['header'] = str(sm) + "'s lines"
		dict['active_fish'] = active_fish
		
		return render_to_response('activelines.html', dict, context_instance=RequestContext(request))

def viewActiveLines(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		active_fish = []
		active_fish += Line.objects.filter(active__exact=True).all()
		active_fish.sort(key=lambda x: x.barcode)

		dict['definesHeader'] = True
		dict['activeOny'] = True
		dict['header'] = "Currently active lines"
		dict['active_fish'] = active_fish
		
		return render_to_response('activelines.html', dict, context_instance=RequestContext(request))

def findLine(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		active_fish = []
		if request.method == 'POST':
			filterString = request.POST.get('filterString')
			active_fish += Line.objects.filter(name__contains=str(filterString)).all()
			active_fish.sort(key=lambda x: x.barcode)
			if (filterString == ''):
				dict['header'] = "No input given: All lines shown"
			else:
				dict['header'] = "All lines containing the string '"+filterString + "'"
		else:
			dict['header'] = "No input given: All lines shown"

		dict['definesHeader'] = True
		dict['activeOny'] = True
		
		dict['active_fish'] = active_fish
		
		return render_to_response('activelines.html', dict, context_instance=RequestContext(request))

def viewActiveProducts(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name

		active_products = []
		active_products += Product.objects.filter(active__exact=True).all()
		active_products.sort(key=lambda x: x.barcode)

		dict['active_products'] = active_products
		
		return render_to_response('activeproducts.html', dict, context_instance=RequestContext(request))

def viewUsers(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name
		if (not userAllowedHere(sm,'viewusers')):
			dict['definesHeader'] = True
			dict['header'] = "I dont think you were supposed to be there"
			return render_to_response('homepage.html', dict, context_instance=RequestContext(request))

		active_users = []
		active_users += StaffMember.objects.all()
		active_users.sort(key=lambda x: x.last_name)

		dict['active_users'] = active_users
		
		return render_to_response('userlist.html', dict, context_instance=RequestContext(request))

def editUser(request,id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['actions'] = get_user_allowed_actions(sm)
		dict['first_name'] = sm.first_name
		if (not userAllowedHere(sm,'editusers')):
			dict['definesHeader'] = True
			dict['header'] = "I dont think you were supposed to be there"
			return render_to_response('homepage.html', dict, context_instance=RequestContext(request))

		try:
			to_edit = StaffMember.objects.filter(pk=id).get()
		except:
			dict['definesHeader'] = True
			dict['header'] = "That person doesn't seem to exist"
			return render_to_response('homepage.html', dict, context_instance=RequestContext(request))
		if request.method == 'POST':
			# submitting the modification
			form = EditUserForm(request.POST)
			if form.is_valid():
				# process form data					
				to_edit.first_name = form.cleaned_data['first']
				to_edit.last_name = form.cleaned_data['last']
				to_edit.position = form.cleaned_data['position']
				to_edit.lab_group = form.cleaned_data['lab_group']
				to_edit.save()
				to_edit.user.username = form.cleaned_data['user']
				to_edit.user.save()
				create_HistoryItem('Edit User', sm, False, '', True, [to_edit.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
		else:
			# bringing up the edit page
			initial = {'user': to_edit.user.username, 'first': to_edit.first_name,'last': to_edit.last_name, 'position': to_edit.position,'lab_group': to_edit.lab_group}
			dict['action_slug'] = "edituser/"+str(id)
			dict['form'] = EditUserForm(initial=initial)		
			return render_to_response('form.html', dict, context_instance=RequestContext(request))

def euthanizeLine(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['id'] = id
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		obj = Line.objects.filter(barcode__exact=id).get()
		if request.method == 'POST':
			barcode = request.POST.get('selection')
			if (str(barcode) == str(id)):
				new = Line.objects.filter(barcode__exact=barcode).get()
				new.active = False
				new.save()
				create_HistoryItem('Euthinize Line', sm, False, '', True, [new.id])
				return render_to_response('success.html', dict, context_instance=RequestContext(request)) # redirect after successful POST
			else:
				dict['definesHeader'] = True
				dict['header'] = "Error encountered: Barcode not valid"
				dict['form'] = EnterBarcodeForm()
				dict['action_slug'] = "euthanizeline/"+ str(id)
				return render_to_response('form.html', dict, context_instance=RequestContext(request))
		else:
			dict['definesHeader'] = True
			dict['header'] = "Enter barcode of fish to be euthanized"
			dict['definesSubButton'] = True
			dict['subButton'] = "Confirm"
			form = EnterBarcodeForm()
		dict['form'] = form
		dict['action_slug'] = "euthanizeline/"+ str(id)
		return render_to_response('form.html', dict, context_instance=RequestContext(request))

def returnLineCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=All_Lines.csv'
	allFish = Line.objects.all()
	writer = csv.writer(response)
	writer.writerow(['Name', 'Barcode', 'LineID', 'Current Quantity', 'Original Quantity', 'Parent', 'Container', 'Location', 'Strain', 'Gender', 'Active', 'Birthdate', 'Owner'])
	for fish in allFish:
		if (fish.parent == None):
			writer.writerow([fish.name, fish.barcode, fish.IACUC_ID, fish.current_quantity, fish.original_quantity, ' ', fish.container, fish.location, fish.strain, fish.sex, fish.active, fish.birthdate, fish.owner])
		else:
			writer.writerow([fish.name, fish.barcode, fish.IACUC_ID, fish.current_quantity, fish.original_quantity, fish.parent, fish.container, fish.location, fish.strain, fish.sex, fish.active, fish.birthdate, fish.owner])
	return response

def returnProductCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=All_Products.csv'
	allProducts = Product.objects.all()
	writer = csv.writer(response)
	writer.writerow(['Name', 'Barcode', 'Parent 1', 'Parent 2', 'Type', 'Container', 'Active', 'Owner'])
	for product in allProducts:
		parent1 = product.line_id.barcode if product.line_id is not None else ''
		parent2 = product.line2_id.barcode if product.line2_id is not None else ''
		writer.writerow([product.name, product.barcode, parent1, parent2, product.type, product.container, product.active, product.owner])
	return response

def returnAlleleCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=All_Products.csv'
	allAllele = GeneticElement.objects.all()
	writer = csv.writer(response)
	writer.writerow(['Name', 'Version', 'Chromosome', 'Position', 'Description', 'Type', 'Size', 'Orientation', 'Insert Name', 'RefNumber'])
	for allele in allAllele:
		Description = allele.allele_type.description
		Type = allele.allele_type.type
		Size = allele.allele_type.size if allele.allele_type.size is not None else ''
		Orientation = allele.allele_type.orientation if allele.allele_type.orientation is not None else ''
		InsertName = allele.allele_type.insert_name.name if allele.allele_type.insert_name is not None else ''
		RefNumber = allele.allele_type.insert_name.ref_number if (allele.allele_type.insert_name is not None and allele.allele_type.insert_name.ref_number is not None) else ''
		writer.writerow([allele.name, allele.version, allele.chromosome, allele.position, Description, Type, Size, Orientation, InsertName, RefNumber])
	return response

def returnAssociationsCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=All_Lines.csv'
	allFish = Line.objects.all()
	writer = csv.writer(response)
	writer.writerow(['Line Barcode','Allele Name', 'Version', 'Chromosome', 'Position', 'Description', 'Allele Type', 'Size', 'Orientation', 'Insert Name', 'RefNumber'])
	for fish in allFish:
		associatedGenomes = fish.genomes.all()
		for allele in associatedGenomes:
			Description = allele.allele_type.description
		Type = allele.allele_type.type
		Size = allele.allele_type.size if allele.allele_type.size is not None else ''
		Orientation = allele.allele_type.orientation if allele.allele_type.orientation is not None else ''
		InsertName = allele.allele_type.insert_name.name if allele.allele_type.insert_name is not None else ''
		RefNumber = allele.allele_type.insert_name.ref_number if (allele.allele_type.insert_name is not None and allele.allele_type.insert_name.ref_number is not None) else ''
		writer.writerow([fish.barcode, allele.name, allele.version, allele.chromosome, allele.position, Description, Type, Size, Orientation, InsertName, RefNumber])
	return response

##############
#####
#####    Other Functions
#####
##############
def show_user_menu(request):
	if not request.user.is_authenticated():
		dict = locals()
		return render_to_response('homepage.html', dict, context_instance=RequestContext(request))
	else:
		dict = locals()
		sm = StaffMember.objects.get(user=dict['request'].user)
		dict['first_name'] = sm.first_name
		dict['actions'] = get_user_allowed_actions(sm)
		return render_to_response('homepage.html', dict, context_instance=RequestContext(request))

def create_HistoryItem(action, user, due, instructions, finished, params):
	dict = locals()
	sm = user
	actionObject = str(action)
	now = date.today()
	if (due == False):
		dueDate = date.today()
	else:
		dueDate = due
	reqd_ins = instructions
	isComplete = finished
	if (len(params) == 0):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete)
	if (len(params) == 1):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]))
	if (len(params) == 2):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]), param_2=int(params[1]))
	if (len(params) ==3):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]), param_2=int(params[1]), param_3=int(params[2]))
	if (len(params) == 4):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]), param_2=int(params[1]), param_3=int(params[2]), param_4=int(params[3]))
	if (len(params) == 5):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]), param_2=int(params[1]), param_3=int(params[2]), param_4=int(params[3]), param_5=int(params[4]))
	if (len(params) == 6):
		h = HistoryItem(action=actionObject, who=sm, date=now, reqd_date=dueDate, reqd_instructions=reqd_ins, finished=isComplete, param_1=int(params[0]), param_2=int(params[1]), param_3=int(params[2]), param_4=int(params[3]), param_5=int(params[4]), param_6=int(params[5]))
	h.save()
		
def create_request(request):
	action_id = request.POST['action']
	reqd_by_id = request.POST['reqd_by_id']
	reqd_ins = request.POST['reqd_ins']
	p1 = request.POST['p1']
	p2 = reqest.POST['p2']
	p3 = request.POST['p3']
	p4 = reqest.POST['p4']
	p5 = request.POST['p5']
	p6 = reqest.POST['p6']
	a = action_id
	rb = StaffMember.objects.get(id=reqd_by_id)
	h = HistoryItem(action=a, reqd_by=rb, reqd_instructions=reqd_ins, param_1=p1, param_2=p2, param_3=p3, param_4=p4, param_5=p5, param_6=p6)
	h.save()
	return render_to_response('login.html')

def get_flat_user_allowed_actions(sm):
	# get all user specific permissions
	permissions = []
	permissions += sm.permissions.all()
	# get the permissions for all groups the user is in
	group = sm.lab_group
	permissions += group.permissions.all()
	
	# get the actions associated with those permissions
	actions = []
	for permission in permissions:
		actions += permission.actions.all()
	actions = list(set(actions))
	return actions
	
def get_user_allowed_actions(sm):
	actions = get_flat_user_allowed_actions(sm)
	categories = []
	lineActions = []
	productActions = []
	genomeActions = []
	generalActions = []
	adminActions = []
	for x in actions:
		if (x.type == 'Line'):
			lineActions += [x]
		if (x.type == 'Product'):
			productActions += [x]
		if (x.type == 'Genome'):
			genomeActions += [x]
		if (x.type == 'General'):
			generalActions += [x]
		if (x.type == 'Admin'):
			adminActions += [x]
	categories = {'01Line':lineActions,'02Product':productActions,'03Genome':genomeActions,'04General':generalActions,'05Admin':adminActions}

	return categories

def userAllowedHere(sm, action):
	actions = get_flat_user_allowed_actions(sm)
	for x in actions:
		if (x.slug == action):
			return True
	return False
	
register = template.Library()

@register.filter
@stringfilter
def qrcode(value, alt=None):
    
    url = conditional_escape("http://chart.apis.google.com/chart?%s" % \
            urllib.urlencode({'chs':'150x150', 'cht':'qr', 'chl':value, 'choe':'UTF-8'}))
    alt = conditional_escape(alt or value)
    
    return mark_safe(u"""<img class="qrcode" src="%s" width="150" height="150" alt="%s" />""" % (url, alt))
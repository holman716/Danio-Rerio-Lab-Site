from django.conf.urls.defaults import *
from views import *

from registration.views import activate
from registration.views import register
from django.contrib.auth import views as auth_views
from labinterface.forms import *

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
	# Base menu
	
	url(r'^$',  show_user_menu, name="index"),
	
	url(r'^action/addline/$', addLine, name="addline"),
	url(r'^action/editline/$', editLine, name="editline"),
	url(r'^action/viewitem/$', viewItemRedirect, name="viewitem"),
	url(r'^action/viewline/(?P<id>\w+)/$', viewLine, name="viewline"),
	
	url(r'^action/addproducttype/$', addProductType, name="addproducttype"),
	url(r'^action/editproducttype/$', editProductType, name="editproducttype"),
	url(r'^action/viewproduct/(?P<id>\w+)/$', viewProduct, name="viewproduct"),
	
	url(r'^action/addproduct/$', addProduct, name="addproduct"),
	url(r'^action/editproduct/$', editProduct, name="editproduct"),

	url(r'^action/addgenome/$', addGenome, name="addgenome"),
	url(r'^action/editgenome/$', editGenome, name="editgenome"),
	url(r'^action/viewgenome/(?P<id>\w+)/$', viewGenome, name="viewgenome"),

	url(r'^action/addgenomeassociation/$', addGenomeAssociation, name="addgenomeassociation"),

	url(r'^action/addgenomeversion/$', addGenomeVersion, name="addgenome"),
	url(r'^action/editgenomeversion/$', editGenomeVersion, name="editgenome"),

	url(r'^action/splitline/(?P<id>\w+)/$', splitLineInitial, name="splitline"),
	url(r'^action/splitline/$', splitLine, name="splitline"),
	
	
	# Activation keys get matched by w+ instead of the more specific
	# [a-fA-F0-9]{40} because a bad activation key should still get to the view;
	# that way it can return a sensible "invalid key" message instead of a
	# confusing 404.
	
	url(r'^login/$',auth_views.login,{'template_name': 'registration/login.html'},name='auth_login'),
	url(r'^activate/(?P<activation_key>\w+)/$',activate, {'backend':'labinterface.regbackend.CustomRegistrationBackend'},name='registration_activate'),
	url(r'^logout/$',auth_views.logout,{'template_name': 'registration/logout.html'},name='auth_logout'),
	url(r'^password/change/$',auth_views.password_change,name='auth_password_change'),
	url(r'^password/change/done/$',auth_views.password_change_done,name='auth_password_change_done'),
	url(r'^password/reset/$',auth_views.password_reset,name='auth_password_reset'),
	url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',auth_views.password_reset_confirm,name='auth_password_reset_confirm'),
	url(r'^password/reset/complete/$',auth_views.password_reset_complete,name='auth_password_reset_complete'),
	url(r'^password/reset/done/$',auth_views.password_reset_done,name='auth_password_reset_done'),
    url(r'^register/$',register,{'form_class' : MyRegistrationForm, 'backend':'labinterface.regbackend.CustomRegistrationBackend'},name='registration_register'),
    #url(r'^register/$',register,{'form_class' : MyRegistrationForm},name='registration_register'),
	url(r'^register/complete/$',direct_to_template,{'template': 'registration/registration_complete.html'},name='registration_complete'),
    url(r'^user_activated/$',direct_to_template,{'template': 'registration/activation_complete.html'},name='registration_activation_complete'),
	
)
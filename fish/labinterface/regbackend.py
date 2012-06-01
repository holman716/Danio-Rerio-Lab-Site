from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from fish.labinterface.models import *

from registration import signals
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from labinterface.models import StaffMember


class CustomRegistrationBackend(object):
	def register(self, request, **kwargs):
		username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
		if Site._meta.installed:
			site = Site.objects.get_current()
		else:
			site = RequestSite(request)
		new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site)
		signals.user_registered.send(sender=self.__class__, user=new_user, request=request)
		new_profile = StaffMember.objects.get(user=new_user)
		new_profile.first_name=kwargs['first_name']
		new_profile.last_name=kwargs['last_name']
		new_profile.position=kwargs['position']
		new_profile.save()
		return new_user
	def activate(self, request, activation_key):
		activated = RegistrationProfile.objects.activate_user(activation_key)
		if activated:
			signals.user_activated.send(sender=self.__class__,
										user=activated,
										request=request)
		return activated

	def registration_allowed(self, request):
		"""
		Indicate whether account registration is currently permitted,
		based on the value of the setting ``REGISTRATION_OPEN``. This
		is determined as follows:

		* If ``REGISTRATION_OPEN`` is not specified in settings, or is
		set to ``True``, registration is permitted.

		* If ``REGISTRATION_OPEN`` is both specified and set to
		``False``, registration is not permitted.
		
		"""
		return getattr(settings, 'REGISTRATION_OPEN', True)

	def get_form_class(self, request):
		"""
		Return the default form class used for user registration.
		
		"""
		return RegistrationForm

	def post_registration_redirect(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		user registration.
		
		"""
		return ('registration_complete', (), {})

	def post_activation_redirect(self, request, user):
		"""
		Return the name of the URL to redirect to after successful
		account activation.
		
		"""
		newMember = StaffMember.objects.filter(pk=user.pk).get()
		labGroup = LabGroup.objects.filter(pk=1).get()
		newMember.lab_group = labGroup
		return ('registration_activation_complete', (), {})
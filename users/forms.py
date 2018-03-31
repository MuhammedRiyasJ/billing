from django import forms
from users.models import Profile
from django.forms.widgets import TextInput, Select, PasswordInput, Textarea, SelectMultiple,CheckboxInput
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    
    username = forms.CharField(label=_("Username"), 
                               max_length=254,
                               widget=forms.TextInput(
                                    attrs={'placeholder': 'Enter Username','class':'required form-control'})
                               )

    password1 = forms.CharField(label=_("Password"), 
                               widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Enter password','class':'required form-control'})
                               )

    password2 = forms.CharField(label=_("Repeat Password"), 
                               widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Enter password again','class':'required form-control'})
                               )

    class Meta:
        model = User
        fields = ('username',)


    min_password_length = 6

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        if len(password1) < self.min_password_length:
            raise forms.ValidationError("Password must have at least %i characters" % self.min_password_length)
        else:
            return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
        
    min_username_length = 6

    def clean_username(self):
        username = self.cleaned_data['username']
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        elif len(username) < self.min_username_length:
            raise forms.ValidationError("Username must have at least %i characters" % self.min_password_length)
        else:
            return self.cleaned_data['username']
   
    def save(self,commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class EditUserForm(UserCreationForm):
    
    
    username = forms.CharField(label=_("Username"), 
                               max_length=254,
                               widget=forms.TextInput(
                                    attrs={'placeholder': 'Enter Username','class':'required form-control'})
                               )
    
    class Meta:
        model = User
        fields = ('username',)

    
    min_username_length = 6

    def clean_username(self):
        username = self.cleaned_data['username']
        
        if len(username) < self.min_username_length:
            raise forms.ValidationError("Username must have at least %i characters" % self.min_password_length)
        else:
            return self.cleaned_data['username']
        
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields.pop('password1')
        self.fields.pop('password2')
   
    def save(self,commit=True):
        return super(UserCreationForm, self).save()
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):

	class Meta:
		model = Profile
		exclude = ['id','creator','updater','date_added','date_updated','user','current_shop','is_deleted']
		widgets ={
			'user_type': Select(attrs={'placeholder':'Select User Type','class':'required form-control'}),
			'shops': SelectMultiple(attrs={'placeholder':'Select Shops','class':'form-control'}),
            'tax_only':CheckboxInput()
		}
        error_messages = {
            'shops' : {
                'required' : _("Shop Field is required"),
            },
        }

        def clean_shops(self):

            try:
                shops = self.cleaned_data['shops']
            except:
                raise forms.ValidationError("No shop found for user.")

            if not shops:
                print "form validation error"
                raise forms.ValidationError("No shop found for user.")

            return shops


class ChangeShopForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['current_shop']
        widgets ={
            'current_shop': Select(attrs={'placeholder':'Select Shops','class':'form-control required'}),
        }
from users.models import Profile
from app.models import Notification


def get_current_shop(request):
	if request.user.is_authenticated():
		current_user = request.user
		shop = Profile.objects.get(user=current_user,is_deleted=False,).current_shop

		return shop


def generate_form_errors(args,formset=False):
    message = ''
    if not formset:
        for field in args:
            if field.errors:
                message += str(field.errors)
        for err in args.non_field_errors():
            message += str(err)
                
    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message += str(field.errors)
            for err in form.non_field_errors():
                message += str(err)
    return message


def create_notification(product,shop):
    message = "%s is out of stock" % (product)

    Notification(    
        shop = shop,
        message = message,
    ).save()


def create_cheque_notification(cheque,shop):
    message = "<p>Cheque processing date of %s is %s.Please Maintain Account Balance %s. <a href='/cheque-details/view-cheque-details/%s/' >click here for details</a></p> " % (cheque.name,cheque.date.strftime("%d-%m-%y"),cheque.amount,cheque.pk)

    Notification(    
        shop = shop,
        message = message,
        is_cheque = True
    ).save()

from dal import autocomplete
from customers.models import Customer
from app.functions import get_current_shop


class CustomerAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

    	current_shop = get_current_shop(self.request)

        if not self.request.user.is_authenticated():
            return Customer.objects.none()

        qs = Customer.objects.filter(is_deleted=False,shop=current_shop)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
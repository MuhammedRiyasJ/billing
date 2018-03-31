from dal import autocomplete
from vendors.models import Vendor
from app.functions import get_current_shop


class VendorAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):

    	current_shop = get_current_shop(self.request)
    	
        if not self.request.user.is_authenticated():
            return Vendor.objects.none()

        qs = Vendor.objects.filter(is_deleted=False,shop=current_shop)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

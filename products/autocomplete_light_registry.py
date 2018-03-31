from dal import autocomplete
from products.models import Product
from app.functions import get_current_shop
from users.models import Profile


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):

    	current_shop = get_current_shop(self.request)
    	user_profile = Profile.objects.get(user=self.request.user)
    	
        if not self.request.user.is_authenticated():
            return Product.objects.none()

        if user_profile.tax_only:
        	qs = Product.objects.filter(is_deleted=False,shop=current_shop,untaxed=False)
        else:
        	qs = Product.objects.filter(is_deleted=False,shop=current_shop)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

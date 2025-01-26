from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from .models import Order
from .forms import CardForm
from bank.models import Transaction, Visa, MasterCard
from oauth2_provider.models import Application
import requests


def payment_card(request, order_id, link_uuid): 
    """
    Process payment for an order using a credit card.

    Parameters:
    - request (HttpRequest): The HTTP request object.
    - order_id (int): The ID of the order to process payment for.
    - link_uuid (str): The UUID associated with the payment link.

    Returns:
    - HttpResponse: Rendered HTML page.

    This function processes payment for an order using a credit card. If the order has already been paid for,
    it displays the payment confirmation page. If the request method is POST, it processes the credit card
    data form submitted by the user. If the form is valid, it marks the order as paid. If the request method
    is not POST, it generates an empty form for entering credit card details.

    If the order does not exist, a 404 error page is returned.
    """

    # Retrieve the order or return a 404 error if the order doesn't exist
    order = get_object_or_404(Order, id=order_id,)

    if request.method == 'POST':
        # If the request is a POST, process the credit card data form
        form = CardForm(request.POST)
        if form.is_valid():
            if order.is_paid:
                return render(request, 'payments/created_payment.html', {'order': order})
            # If the form is valid, mark the order as paid
            cd = form.cleaned_data
                
            if cd['id_card'][0]=='4':
                card_model = Visa
            elif cd['id_card'][0]=='5':     
                card_model = MasterCard
            else:
                return render(request, 'payments/error.html', {'error_message': "Unsupported card type"})
                
            try:
                card = get_object_or_404(card_model, id_card=cd.get('id_card'))
                # Create new transaction
                Transaction.objects.create(
                        bank = card.bank,
                        first_name = order.client.name,
                        last_name = order.client.surname,
                        transaction_type = 'TRANSFER',
                        amount = order.total,
                        iban = order.profile.iban
                    )
                app = Application.objects.get(user=order.profile)     
                order.mark_as_paid()    
                # Sending information to the application about payment for a given order
                payment_data = {
                        'order_id': order.order_id,
                        'is_paid': order.is_paid  
                    }
                headers = {
                            'Content-Type': 'application/json'
                        }
                # Verify only dev mode 
                response = requests.post(app.redirect_uris, json=payment_data, headers=headers, verify=False)
                if response.status_code == 200:
                    order.redirect_link = response.json().get("redirect_link")
                    order.save()
                    return render(request, 'payments/created_payment.html', {'order': order})
                else:
                    return render(request, 'payments/error.html', {"Error HTTP:", response.status_code})
                     
            except requests.HTTPError as e:
                return render(request, 'payments/error.html', {"Error HTTP:", e})
            except card_model.DoesNotExist:
                return render(request, 'payments/error.html', {'error_message': "Card not found"})
            except ValidationError as e:
                return render(request, 'payments/error.html', {'error_message': str(e)})
            except Exception as e:
                return render(request, 'payments/error.html', {'error_message':e })
        else:
            
            return render(request, 'payments/card.html', {
                'form': form, 
                'order': order, 
                'order_id': order_id, 
                'link_uuid': link_uuid
            })
                      
    else:
        if order.is_paid:
             # If the order is paid, display the payment confirmation page
            return render(request, 'payments/created_payment.html', {'order': order})
        else:
            # Render the page for entering credit card details
            return render(request, 'payments/card.html', {'order': order, 
                                                        'order_id': order_id, 
                                                        'link_uuid': link_uuid,
                                                        'form': CardForm()})
    
def payment_method(request):
    pass

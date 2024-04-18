from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from .models import Order
from .forms import CardForm
from bank.models import Transaction, Visa, MasterCard


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

    if order.is_paid:
        # If the order is paid, display the payment confirmation page
        return render(request, 'payments/created_payment.html', {'order': order})
    else:
        if request.method == 'POST':
            # If the request is a POST, process the credit card data form
            form = CardForm(request.POST)
            if form.is_valid():
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
                    Transaction.objects.create(
                        bank = card.bank,
                        first_name = order.client.name,
                        last_name = order.client.surname,
                        transaction_type = 'TRANSFER',
                        amount = order.total,
                        iban = order.profile.iban
                    )
                    order.mark_as_paid()
                    
                    return render(request, 'payments/created_payment.html', {'order': order}) 
                except card_model.DoesNotExist:
                    return render(request, 'payments/error.html', {'error_message': "Card not found"})
                except ValidationError as e:
                    return render(request, 'payments/error.html', {'error_message': str(e)})
                except Exception as e:
                    return render(request, 'payments/error.html', {'error_message': "An error occurred during payment"})
                       
        else:
            # If the request is not a POST, generate an empty form
            form = CardForm()

        # Render the page for entering credit card details
        return render(request, 'payments/card.html', {'order': order, 
                                                        'order_id': order_id, 
                                                        'link_uuid': link_uuid,
                                                        'form': form})
    
def payment_method(request):
    pass

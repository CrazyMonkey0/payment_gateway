from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from .forms import CardForm


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
    order = get_object_or_404(Order, id=order_id)

    if order.is_paid:
        # If the order is paid, display the payment confirmation page
        return render(request, 'payments/created_payment.html', {'order': order})
    else:
        if request.method == 'POST':
            # If the request is a POST, process the credit card data form
            form = CardForm(request.POST)
            if form.is_valid():
                # If the form is valid, mark the order as paid
                order.mark_as_paid()
                return render(request, 'payments/created_payment.html', {'order': order}) 
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

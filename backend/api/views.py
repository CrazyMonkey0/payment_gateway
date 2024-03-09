from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from payments.models import Order
from .serializers import OrderSerializer
import secrets
import uuid
import hashlib
import time

def generate_payment_token(profile, client, products, total):
    # Generujemy unikalny token na podstawie danych płatności i bieżącego czasu
    token_data = f"{profile}-{client}-{products}-{total}-{time.time()}"
    # Tworzymy skrót SHA256 jako token płatności
    payment_token = hashlib.sha256(token_data.encode()).hexdigest()
    return payment_token

class OrderAPIView(APIView):
    """
    API view for managing orders.

    Attributes:
    - queryset (QuerySet): The queryset containing all orders.
    """

    def get(self, request):
        """
        Method for retrieving all orders of a given user.

        Arguments:
        - request (HttpRequest): HTTP request object.

        Returns:
        - response (Response): HTTP response containing all the orders of a given user.
        """
        queryset = Order.objects.filter(profile=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Handle POST requests to create a new order.

        Parameters:
        - request (HttpRequest): The HTTP request object containing order data.

        Returns:
        - Response: JSON response containing the ID of the created order and a link to the payment page,
                    or error messages if the provided data is invalid.
        """
        serializer = OrderSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'order_id': serializer.data['id'], 
                             'order_link': f"http://127.0.0.1:8000/payments/{serializer.data['id']}/{serializer.data['link']}"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

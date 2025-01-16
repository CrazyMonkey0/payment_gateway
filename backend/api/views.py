from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from payments.models import Order
from .serializers import OrderSerializer
from .toolkit import get_user_profile

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
        queryset = Order.objects.filter(profile=get_user_profile(request, True))
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
            return Response({'payment_id': serializer.data['id'], 
                             'payment_link': f"https://127.0.0.1:8000/payment/card/{serializer.data['id']}/{serializer.data['link']}"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, payment_id):
        try:
            # Próbujemy pobrać zamówienie na podstawie order_id
            order = Order.objects.get(id=payment_id)
        except Order.DoesNotExist:
            # Jeśli zamówienie nie istnieje, zwróć błąd
            raise NotFound(detail="Order not found.")
        
        # Tworzymy serializer z danymi requestu, kontekstem (w tym przypadku ID zamówienia)
        serializer = OrderSerializer(order, data=request.data, context={'request': request}, partial=True)
        
        # Jeśli dane są prawidłowe, zapisujemy zmiany
        if serializer.is_valid():
            serializer.save()
            return Response({
                'payment_id': serializer.data['id'],
                'payment_link': f"https://127.0.0.1:8000/payment/card/{serializer.data['id']}/{serializer.data['link']}"
            }, status=status.HTTP_200_OK)
        
        # Jeśli dane są nieprawidłowe, zwróć błędy
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

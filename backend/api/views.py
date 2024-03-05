from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from payments.models import Order
from .serializers import OrderSerializer


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
        Method to create a new order.

        Args:
        - request (HttpRequest): The HTTP request object containing order data.

        Returns:
        - response (Response): The HTTP response containing the created order or validation errors.
        """
        serializer = OrderSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

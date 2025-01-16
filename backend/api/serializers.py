from os import name
from rest_framework import serializers
from payments.models import Client, Product, Order
from accounts.models import Profile
from .toolkit import get_user_profile
import uuid


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Attributes:
    - first_name (str): The first name of the profile.
    - last_name (str): The last name of the profile.
    - email (str): The email address of the profile.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email']


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Client model.

    Attributes:
    - name (str): The client's first name.
    - surname (str): The client's last name.
    - email (str): The client's email address.
    """
    class Meta:
        model = Client
        fields = ['name', 'surname', 'email']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    Attributes:
    - name (str): The name of the product.
    - quantity (int): The quantity of the product.
    """
    class Meta:
        model = Product
        fields = ['name', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Attributes:
    - profile (ProfileSerializer): The profile associated with the order (optional).
    - client (ClientSerializer): The client associated with the order.
    - products (list of ProductSerializer): The list of products included in the order.
    - total (decimal): The total amount of the order.
    - is_paid (bool): The payment status of the order.
    """
    profile = ProfileSerializer(required=False)
    client = ClientSerializer()
    products = ProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'link', 'profile', 'client', 'products', 'order_id', 'total', 'is_paid']

    def create(self, validated_data):
        """
        Method to create a new order.

        Args:
        - validated_data (dict): The validated data for the order.

        Returns:
        - order (Order): The newly created order object.

        Raises:
        - ValidationError: If the user is not logged in or no profile is found.
        """
        client_data = validated_data.pop('client')
        products_data = validated_data.pop('products')

        client = Client.objects.create(**client_data)
        products = [Product.objects.create(**product_data) for product_data in products_data]

        request = self.context.get('request', None)

        # Check if the request contains information about the logged-in user
        if request:
            # Get the user's profile
            profile = get_user_profile(request)
    
            # Create a new order, assign client, user profile, unique link and other data
            order = Order.objects.create(client=client, profile=profile, link=str(uuid.uuid4()), **validated_data)

            # Add products to the order
            for product in products:
                order.products.add(product)

            return order

        # If no logged-in user is found, raise an error
        raise serializers.ValidationError("User not logged in or no profile found.")
    
    def update(self, instance, validated_data):
        """
        Method to update an existing order.
        """
        # Update the client
        client_data = validated_data.pop('client', None)
        if client_data:
            for attr, value in client_data.items():
                setattr(instance.client, attr, value)
            instance.client.save()

        # Update the profile if provided
        profile_data = validated_data.pop('profile', None)
        if profile_data and instance.profile:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()

        # Update the products
        products_data = validated_data.pop('products', None)
        if products_data:
            # Clear existing products
            instance.products.clear()
            for product_data in products_data:
                # Check if product exists with the same name and quantity
                product = Product.objects.filter(
                    name=product_data['name'],
                    quantity=product_data['quantity']
                ).first()

                # Create product if it doesn't exist
                if not product:
                    product = Product.objects.create(**product_data)

                # Add the product to the order
                instance.products.add(product)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
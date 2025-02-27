# Payment Gateway

This project is a robust payment gateway application built with Django and Django REST Framework. It enables businesses to manage orders, process payments securely, and interact with customers via a WebSocket-based support chat. The application supports multiple payment providers and is designed to be easily integrated with external systems.

## Table of Contents

- [Technologies](#technologies)
- [Requirements](#requirements)
- [Installation](#installation)
- [Docker](#docker)
- [Token Acquisition](#token-acquisition)
- [Client Application Configuration](#client-application-configuration)
- [Docker](#docker)
- [API Endpoints](#api-endpoints)
- [WebSocket Endpoints](#websocket-endpoints)
- [License](#license)

## Technologies

This project utilizes the following technologies:

- **Backend:** Django, Django REST Framework, Django Channels  
- **Database:** PostgreSQL / SQLite  
- **WebSockets:** Django Channels, Redis  
- **Containerization:** Docker, Docker Compose  
- **Authentication:** OAuth2  
- **Other:** Celery, Daphne, RabbitMQ,  

### Source of the base template
[https://html.design/download/finexo-crypto-currency-website-template/]

## Requirements

- Python 3.8+
- Git 
- PostgreSQL or SQLite (default for development)
- Docker & Docker Compose (optional for containerized deployment)
- Redis (for WebSocket support if using Django Channels)
- RabbitMQ (For clelery)

### Security Requirements

To ensure the security of user sessions, the application requires the use of SSL. Use a self-signed certificate that is intended **only for development purposes**. Please note that browsers are configured in such a way that without an SSL connection, they may lose sessions, leading to issues with user login and interaction with the application. Make sure to use an SSL certificate from a trusted provider in a production environment.


## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/CrazyMonkey0/payment_gateway.git
   cd payment_gateway
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Loading sample data
    
    ```bash
    python manage.py loaddata ./backend/data.json
    ```

6. Create a superuser (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

7. Collect static files:

   ```bash
   python manage.py collectstatic
   ```

8. Run the development server:

   ```bash
   daphne -e ssl:8000:privateKey=key.pem:certKey=cert.pem payment_gateway.asgi:application
   ```

9. Access the application at `https://127.0.0.1:8000`.


## Docker

### Running with Docker

1. Before launching the application, create a shared_network

    ```bash
   docker network create shared_network
    ```

2. Build and run the Docker containers:

   ```bash
   docker-compose up --build
   ```

3. Admin - Login: demo  Password: demo

4. Access the application at `https://127.0.0.1:8000`.

## Token Acquisition

To communicate with the application, you need to acquire an authentication token. You can obtain the token by making a POST request to the following endpoint:

### Token Endpoint

    ```
    POST https://127.0.0.1:8000/o/token/
    ```
**Request Body**:
```json
{
    "username": "your_username",
    "password": "your_password",
    "grant_type": "password",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
}
```

**Response**:

```json
{
    "access_token": "your_access_token",
    "token_type": "Bearer",
    "expires_in": 3600
}
```

## Client Application Configuration

To configure your application and get the client_id and client_secret, you need to create a client application. This can be done at the following endpoint:
Application Management Endpoint

    ```
    GET https://127.0.0.1:8000/application/manage/
    ```

### Redirect URI

When creating the client application, you should specify a redirect URI. This URI should point to the client application's API, which, upon receiving the ID of a given order and payment information, will send a link to the payment gateway. The gateway will then redirect the user after a successful payment.
Example of POST Endpoint for Client Application

```python
def post(self, request):
    try:
        order = Order.objects.get(pk=request.data.get('order_id'))
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if order.paid:
        return Response({'detail': 'Order is already paid.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = OrderSerializer(order, data=request.data)

    if serializer.is_valid():
        order.paid = request.data.get('is_paid', False)
        serializer.save()
        return Response({
            'detail': 'Successful payment',
            'redirect_link': f"https://kowalskidev.pl/shop/orders/paid/{request.data.get('order_id')}/"
        }, status=status.HTTP_200_OK)
       
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```
### Example of a Redirect URI
```bash
https://your-shop.com/api/paid/
```

## API Endpoints

### Orders

- `GET /api/orders/`

  - **Description:** Retrieve all orders for the authenticated user.
  - **Authorization:** Requires authentication token.
  - **Response:**
    ```json
    {
            "id": 1,
            "link": "583221d1-7e12-4622-8e11-38b2ca5839d2",
            "profile": {
                "first_name": "demo",
                "last_name": "demo",
                "email": ""
            },
            "client": {
                "name": "fds",
                "surname": "sdf",
                "email": "xxx@xx.sa"
            },
            "products": [
                {
                    "name": "Jordan Flight Court",
                    "quantity": 2
                }
            ],
            "order_id": "282",
            "total": "140.00",
            "is_paid": true
        }
    ```

- `POST /api/orders/`

  - **Description:** Create a new order.
  - **Authorization:** Requires authentication token.
  - **Request Body:**
    ```json
    {
            "client": {
                "name": "fds",
                "surname": "sdf",
                "email": "xxx@xx.sa"
            },
            "products": [
                {
                    "name": "Jordan Flight Court",
                    "quantity": 2
                }
            ],
            "order_id": "283",
            "total": "140.00"
    }
    ```

- `PUT /api/orders/<int:id>/`

  - **Description:** Update an existing order.
  - **Authorization:** Requires authentication token.
  - **Request Body:**
    ```json
    {
            "client": {
                "name": "fds",
                "surname": "sdf",
                "email": "xxx@xx.sa"
            },
            "products": [
                {
                    "name": "Jordan Flight Court",
                    "quantity": 2
                }
            ],
            "order_id": "283",
            "total": "140.00"
    }
    ```

## WebSocket Endpoints

### Chat Support

- **Endpoint:** `ws://<your-domain>/ws/chat/<room_uuid>/`
- **Description:** WebSocket endpoint for real-time chat support.

#### Example WebSocket Client (JavaScript)

```javascript
const socket = new WebSocket("ws://your-domain/ws/chat/room_uuid/");

socket.onopen = function(event) {
    console.log("Connected to chat room.");
};

socket.onmessage = function(event) {
    console.log("Received message:", event.data);
};

socket.onclose = function(event) {
    console.log("Chat connection closed.");
};
```

## License

This project is licensed under the [MIT License](LICENSE.txt).


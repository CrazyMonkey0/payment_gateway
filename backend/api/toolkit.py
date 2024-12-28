from oauth2_provider.models import AccessToken
import hashlib
import time

# def generate_payment_token(profile, client, products, total):
#     # Generate a unique token based on payment data and the current time
#     token_data = f"{profile}-{client}-{products}-{total}-{time.time()}"
#     # Create an SHA256 hash as the payment token
#     payment_token = hashlib.sha256(token_data.encode()).hexdigest()
#     return payment_token

def get_user_profile(request, profile_id=False):
    # Retrieve the 'Authorization' header from the request
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        # Split the header into parts
        parts = auth_header.split()

        # Check if the header contains a valid 'Bearer' token
        if len(parts) == 2 and parts[0] == 'Bearer':
            token = parts[1]
            
            # If profile_id is True, return the user's ID
            if profile_id is True:
                try:
                    # Retrieve the access token from the database and return the user's ID
                    user_token = AccessToken.objects.get(token=token)
                    return user_token.application.user.id
                except AccessToken.DoesNotExist:
                    # Return None if the token does not exist
                    raise ValueError("Invalid token")
            else:
                try:
                    # Retrieve the access token from the database and return the user object
                    user_token = AccessToken.objects.get(token=token)
                    return user_token.application.user
                except AccessToken.DoesNotExist:
                    # Return None if the token does not exist
                    raise ValueError("Invalid token")
    # Raise an error if the 'Authorization' header is not provided
    raise ValueError("Authorization header not provided")

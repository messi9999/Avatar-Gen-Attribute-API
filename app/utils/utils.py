import secrets

def generate_secure_random_image_name(extension='.jpg'):
    random_name = secrets.token_hex(8)  # Generates a secure random hex string.
    return f"{random_name}{extension}"

def hex_to_rgb(hex_color):
    # Remove the '#' character if present
    hex_color = hex_color.lstrip('#')
    
    # Convert the string from hex to integer, using base 16 for hexadecimal
    rgb = list(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    return rgb

from pyngrok import ngrok

# Set your authtoken
ngrok.set_auth_token("34ERvdIqHrZjGGRZMe7IuNVZ5qH_4DfLTU1A9APkYDkGygNpQ")

# Expose local Vite server
public_url = ngrok.connect(5000)
print("Ngrok public URL:", public_url)

input("Press Enter to exit...\n")


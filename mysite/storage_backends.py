# from storages.backends.azure_storage import AzureStorage
# import os

# class CustomAzureStaticStorage(AzureStorage):
#     account_name = os.getenv('AZURE_ACCOUNT_NAME') 
#     account_key = os.getenv('AZURE_ACCOUNT_KEY')    
#     azure_container = os.getenv('AZURE_STATIC_CONTAINER', 'static') 
#     expiration_secs = None  

# class CustomAzureMediaStorage(AzureStorage):
#     account_name = os.getenv('AZURE_ACCOUNT_NAME')  
#     account_key = os.getenv('AZURE_ACCOUNT_KEY')    
#     azure_container = os.getenv('AZURE_MEDIA_CONTAINER', 'media')  
#     expiration_secs = None  

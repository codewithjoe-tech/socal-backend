import base64
from django.utils.crypto import get_random_string

def generate_chatroom_name(users, chat_type='dm'):
    try:
        if chat_type == 'dm':
            user_ids = sorted([str(user.id) for user in users])
            user_id_str = "-".join(user_ids)

            encoded_name = base64.urlsafe_b64encode(user_id_str.encode()).decode()
            return encoded_name

        elif chat_type == 'group':
            return f"GroupChat-{base64.urlsafe_b64encode(get_random_string(8).encode()).decode()[:16]}"

        else:
            return "UnnamedChatroom"
        
    except Exception as e:
        print(f"Error generating chatroom name: {e}")
        return "UnnamedChatroom"  

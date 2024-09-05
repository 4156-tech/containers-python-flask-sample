import scratchattach as scratch3

# In-memory storage for map data, update status, rooms, and registered users
map_data = {}
map_update_status = {}
rooms = {}  # Room management
registered_users = {}  # Store registered usernames and passwords
next_room_id = 1  # Initialize the next room ID

# Session and connection setup
session_id = ".eJxVj8FugzAQRP-Fc0ttbAeTWxoqtYdQiaqVckJrewkuYCMwitSq_14j5ZLbat7MaOc3WRecHYyY7JNzfajKt_cqeUgaWEPXbKyxJqKCZlwSQSMKuATtfW-3yNXPPZr7gALdo9tSm4YuWA3BepfewJLWOA038flmjr0-HjFEQGvKOANJgEsApZEXqpVaGpaDyvev8HUsjx_tMM2numD69DKS0n8Ksi6xZvAX6x7tFJsoYSkVeUpJnuYkMvMN7uKbYEf88W77_zDiHD95qvDanOOW-yUdLF00qW05U8QQhrIQXIlsxzCTaCTnu7ZQucmo4Dr5-wc1e2r9:1sllY9:Rbd9wOcaVek0VnxeU4xYRERJYq0"
username = "YRANDION"
session = scratch3.Session(session_id, username=username)
conn = session.connect_cloud("1063141008")  # Your project ID

client = scratch3.CloudRequests(conn)

# Register a new user
@client.request
def register(username, password, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    if username in registered_users:
        return "User already registered"
    
    registered_users[username] = password
    print(f"Register request received for user: {username}")
    return "Registration successful"

# Login a user
@client.request
def login(username, password, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    if username in registered_users and registered_users[username] == password:
        print(f"Login request received for user: {username}")
        return "Login successful"
    else:
        return "Login failed"

# Check if an account is registered
@client.request
def is_registered(username, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    if username in registered_users:
        return "User is registered"
    else:
        return "User is not registered"

# Join the server (room)
@client.request
def join_server(username, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    global next_room_id
    
    print("join_server request received")
    
    # Find an available room
    available_room = None
    for room_id in rooms:
        if len(rooms[room_id]) < 2:
            available_room = room_id
            break
    
    if available_room is None:
        available_room = next_room_id
        next_room_id += 1
        rooms[available_room] = {}
    
    player_id = 1 if len(rooms[available_room]) == 0 else 2
    rooms[available_room][player_id] = {'username': username}
    
    response = f"Joined room {available_room} with player ID {player_id}"
    print("join_server response:", response)
    return response

# Send map data (from Player 1)
@client.request
def send_map_data(room_id, map_data_chunk, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    print("send_map_data request received")
    room_id = int(room_id)
    
    if room_id in rooms and 1 in rooms[room_id]:  # Only PID 1 can send map data
        if room_id not in map_data:
            map_data[room_id] = ""
        map_data[room_id] += map_data_chunk
        response = "Map data received"
    else:
        response = "Invalid room ID"
    
    print("send_map_data response:", response)
    return response

# Request map data (by Player 2)
@client.request
def request_map_data(room_id, player_id, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    print("request_map_data request received")
    room_id = int(room_id)
    player_id = int(player_id)
    
    if player_id == 2 and room_id in map_data:
        response = map_data[room_id]
    elif player_id == 2:
        response = "Waiting for map data from PID 1"
    else:
        response = "Invalid request"
    
    print("request_map_data response:", response)
    return response

# Set player location
@client.request
def set_location(room_id, location, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    print("set_location request received")
    room_id = int(room_id)
    player_id = 1 if 'location' not in rooms[room_id][1] else 2
    
    if room_id in rooms and player_id in rooms[room_id]:
        rooms[room_id][player_id]['location'] = location
        other_player_id = 2 if player_id == 1 else 1
        other_player_location = rooms[room_id].get(other_player_id, {}).get('location', None)
        response = {"status": "Location updated", "other_player_location": other_player_location}
    else:
        response = "Invalid room ID or player ID"
    
    print("set_location response:", response)
    return response

# Start a new round
@client.request
def new_round(room_id, extra_arg=None, *args):
    if len(args) != 0:
        return "Invalid arguments"
    
    print("new_round request received")
    room_id = int(room_id)
    
    if room_id in rooms:
        map_data[room_id] = ""
        map_update_status[room_id] = "Pending"
        response = "New round started. Map data reset."
    else:
        response = "Invalid room ID"
    
    print("new_round response:", response)
    return response

@client.event
def on_ready():
    print("Request handler is running")

client.run()

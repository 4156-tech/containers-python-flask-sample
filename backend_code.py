import scratchattach as scratch3

# In-memory storage for map data, update status, and rooms
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

@client.request
def register(username, password, *args):
    if len(args) != 0:
        return "Invalid arguments"
    if username in registered_users:
        return "Username already exists"
    registered_users[username] = password
    return "Registration successful"

@client.request
def login(username, password, *args):
    if len(args) != 0:
        return "Invalid arguments"
    if username in registered_users and registered_users[username] == password:
        return "Login successful"
    return "Login failed"

@client.request
def join_server(*args):
    print("join_server request received")
    try:
        global next_room_id
        room_id = next_room_id
        next_room_id += 1
        if len(rooms.get(room_id, {})) < 2:
            player_id = len(rooms.get(room_id, {})) + 1
            rooms.setdefault(room_id, {})[player_id] = {}
            response = f"Joined room {room_id} with player ID {player_id}"
        else:
            response = "No available rooms"
        print("join_server response:", response)
        return response
    except Exception as e:
        print("Error in join_server:", e)
        return "Error processing request"

@client.request
def send_map_data(room_id, player_id, map_data_chunk, *args):
    print("send_map_data request received")
    try:
        room_id = int(room_id)
        player_id = int(player_id)
        if player_id != 1:
            return "Only PID 1 can send map data"
        if room_id in rooms:
            if room_id not in map_data:
                map_data[room_id] = ""
            map_data[room_id] += map_data_chunk
            response = "Map data received"
        else:
            response = "Invalid room ID"
        print("send_map_data response:", response)
        return response
    except Exception as e:
        print("Error in send_map_data:", e)
        return "Error processing request"

@client.request
def request_map_data(room_id, player_id, *args):
    print("request_map_data request received")
    try:
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
    except Exception as e:
        print("Error in request_map_data:", e)
        return "Error processing request"

@client.request
def set_location(room_id, player_id, location, *args):
    print("set_location request received")
    try:
        room_id = int(room_id)
        player_id = int(player_id)
        if room_id in rooms and player_id in rooms[room_id]:
            rooms[room_id][player_id]['location'] = location
            other_player_id = 2 if player_id == 1 else 1
            other_player_location = rooms[room_id].get(other_player_id, {}).get('location', None)
            response = {"status": "Location updated", "other_player_location": other_player_location}
        else:
            response = "Invalid room ID or player ID"
        print("set_location response:", response)
        return response
    except Exception as e:
        print("Error in set_location:", e)
        return "Error processing request"

@client.request
def new_round(room_id, *args):
    print("new_round request received")
    try:
        room_id = int(room_id)
        if room_id in rooms:
            map_data[room_id] = ""
            map_update_status[room_id] = "Pending"
            response = "New round started. Map data reset."
        else:
            response = "Invalid room ID"
        print("new_round response:", response)
        return response
    except Exception as e:
        print("Error in new_round:", e)
        return "Error processing request"

def run():
    client.run()

if __name__ == '__main__':
    run()

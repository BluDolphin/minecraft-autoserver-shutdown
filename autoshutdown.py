#!/usr/bin/env python3
"""mc_user_count.py

Simple script to get the number of players on a Minecraft server and output the count to stdout.

Usage:
  python autoshutdown.py --host example.com --port 25565

Dependencies:
  pip install mcstatus

Behavior:
  - Prints a single integer (number of online players) to stdout.
  - On error (server down / network error), prints 0 to stdout and exits with status 1.
"""

from __future__ import annotations

import sys
import time
from mcstatus import JavaServer

GRACE_PERIOD_SECONDS = 600  # 10 minutes
INTERVAL_SECONDS = 900  # 15 minutes
TERMINATE = False

SERVERS = {"minecraft":["35.214.110.227:25565", False]} # Dictionary of servers with address and trigger

    
def shutdown_server(tmux_session):
    """Attempt to stop the Minecraft server.

    - If a tmux session named 'minecraft' exists, send "/stop" to it and follow up
      with an extra Enter to close the session. If the session persists, kill it.

    Returns True if a stop action was attempted, False otherwise.
    """
    import subprocess
    import time

    # Prefer tmux if present and the session exists
    # Check for session
    res = subprocess.run(["tmux", "has-session", "-t", tmux_session], capture_output=True)
    if res.returncode == 0:
        # send /stop and Enter
        subprocess.run(["tmux", "send-keys", "-t", tmux_session, "/stop", "C-m"])
        print(f"Sent '/stop' to tmux session '{tmux_session}'")

        # Give the server a few seconds to shut down and print the 'Server stopped' message
        for _ in range(15):
            time.sleep(1)

        # Send an extra Enter to close the session prompt if present
        subprocess.run(["tmux", "send-keys", "-t", tmux_session, "C-m"])
        print(f"Sent extra Enter to tmux session '{tmux_session}' to close the prompt")

        # If the session still exists, kill it
        res2 = subprocess.run(["tmux", "has-session", "-t", tmux_session], capture_output=True)
        if res2.returncode == 0:
            subprocess.run(["tmux", "kill-session", "-t", tmux_session])
            print(f"Killed tmux session '{tmux_session}'")

        # Procesed to shutdown system
        subprocess.run(["sudo", "shutdown"], check=False)

    return False


def get_player_count(server_address):
    """Query the Minecraft server and print the number of online players.

    Returns a tuple: (exit_code, count). exit_code: 0 on success, 1 on query failure, 2 if dependency missing.
    """
    # Handle import of mcstatus
    try:
        server = JavaServer.lookup(server_address)
        status = server.status() # Only works for version 1.7+ 
        #print(status) 
        
        if status.players.online == 0:
            print("0 players online.")
            return True # Return server shutdown trigger
        else:
            print(f"{status.players.online} players online.")
            return False # Clear server shutdown trigger
        
    except Exception as e:
        print(f"Error querying server {server_address}: {e}", file=sys.stderr)
        return False # On error, do not trigger shutdown (prevents false positives or mid game shutdowns)
    
    
def main(): # timer segment
    global SERVERS
    
    while True:
        print(f"Currently active servers {SERVERS}")
        
        for server in list(SERVERS): # Get list snapshot
            server_trigger = get_player_count(SERVERS[server][0]) # Check player count and get shutdown trigger
            
            if server_trigger == False: # Reset shutdown trigger if players are online
                SERVERS[server][1] = False 
                
            elif SERVERS[server][1] == server_trigger: # If trigger is already set, shutdown server
                shutdown_server(server)
                # Remove server from server list 
                SERVERS.pop(server)
                
            else: # If not reset or already set, set the trigger
                SERVERS[server][1] = server_trigger# Update server shutdown trigger
        
        
        if len(SERVERS) == 0:
            print("No more servers running, ending program")
            return 
        
        # Wait for next check
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    time.sleep(GRACE_PERIOD_SECONDS) # Wait for 
    main()

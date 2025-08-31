# server.py
import socket
from _thread import *
import pickle
from game import Game

server = "127.0.0.1"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((server, port))
s.listen()
print("Waiting for a connection, Server Started")

games = {}            
players_in_game = {}   
idCount = 0

def threaded_client(conn, p, gameId):
    global idCount
    try:
        conn.send(str(p).encode())   
    except Exception as e:
        print("Send player id error:", e)
        conn.close()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print("Client closed socket")
                break

            msg = data.decode(errors="ignore")

            if gameId not in games:
               
                try:
                    conn.sendall(pickle.dumps({"status":"closed"}))
                except Exception:
                    pass
                break

            game = games[gameId]

            if msg == "get":
                pass 
            elif msg == "reset":
                game.resetWent()
            else:
               
                try:
                    game.play(p, msg)
                except Exception as e:
                    print("game.play error:", e)

            
            try:
                conn.sendall(pickle.dumps(game))
            except Exception as e:
                print("send game error:", e)
                break

        except Exception as e:
            print("Server thread error:", e)
            
            try:
                conn.sendall(pickle.dumps({"status":"error", "detail": str(e)}))
            except Exception:
                pass
            break

    print("Lost connection from player", p, "game", gameId)
   
    try:
        players_in_game[gameId] -= 1
        if players_in_game[gameId] <= 0:
            print("Closing Game", gameId)
            games.pop(gameId, None)
            players_in_game.pop(gameId, None)
    except Exception:
        pass

    idCount -= 1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1) // 2

    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        players_in_game[gameId] = 1
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        players_in_game[gameId] = players_in_game.get(gameId, 1) + 1
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))

import socket
import pickle

class Network:
    def __init__(self, server_ip: str, server_port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip              
        self.port = int(server_port)
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
           
            return self.client.recv(2048).decode()
        except Exception as e:
            print("Connect error:", e)
            return None

    def _recvall(self, timeout=2.0, bufsize=4096) -> bytes:
        """Nhận đủ bytes của 1 đối tượng pickle. Thử unpickle dần; nếu chưa đủ thì recv tiếp."""
        self.client.settimeout(timeout)
        chunks = bytearray()
        while True:
            try:
                part = self.client.recv(bufsize)
                if not part:
                    
                    break
                chunks += part
               
                try:
                    pickle.loads(chunks)
                    return bytes(chunks)
                except Exception:
                    continue
            except socket.timeout:
                
                break
        return bytes(chunks)

    def send(self, data):
        try:
            
            if isinstance(data, str):
                self.client.send(data.encode())
            else:
                self.client.send(pickle.dumps(data))

            raw = self._recvall()
            if not raw:
                raise ConnectionError("Empty response from server (socket closed?)")
            return pickle.loads(raw)
        except Exception as e:
            print("Send error:", e)
            raise

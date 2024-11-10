import socket
import threading

class ChatClient:
    """Klientens Klass"""

    def __init__(self, host: str = '127.0.0.1', port: int = 12345):
        """ Initierar värden för serverns adress och port, samt skapar en TCP-klient"""
        self.host: str = host
        self.port: int = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alias: str = ""  # alias för användaren
        self.connected: bool = False  # Håller reda på om klienten är ansluten till servern

    def enter_alias(self) -> None:
        """Användaren anger sitt namn och det sparas som alias."""
        while True:
            alias: str = input("Your name: ")
            if alias.isdigit():  # Kontrollerar att alias inte är enbart siffror
                print('Please enter a valid name.')
            else:
                self.alias = alias
                break
        print("Write 'exit' if you want to terminate your connection.")  # Klienten kan avsluta anslutningen med ordet 'exit'.

    def connect_to_server(self) -> None:
        """Ansluter till servern och skickar användarens alias."""
        try:
            self.client_socket.connect((self.host, self.port))  # Försöker ansluta till servern
            self.client_socket.send(self.alias.encode('utf-8'))  # Skickar alias till servern
            self.connected = True
        except Exception as e:
            print(f"Connection error: {e}")
            self.client_socket.close()  # Stänger anslutningen om det finns ett fel

    def receive_messages(self) -> None:
        """Tar emot meddelanden från servern och visar dem på terminalen."""
        while self.connected==True:
            try:
                message: str = self.client_socket.recv(1024).decode('utf-8')  # Tar emot meddelande från servern
                if not message:
                    print("Server disconnected.")
                    self.client_socket.close()
                    self.connected = False
                    break
                else:
                    print(f"{message}")
            except:
                print("Connection closed.")
                self.client_socket.close()
                self.connected = False
                break

    def send_messages(self) -> None:
        """Skickar meddelanden till servern som klienten skriver"""
        while self.connected==True:
            try:
                message: str = input()
                if message.lower() == 'exit':  # Kontrollerar om användaren vill avsluta anslutningen
                    self.client_socket.close()
                    self.connected = False
                    break
                else:
                    self.client_socket.send(message.encode('utf-8'))  # Skickar meddelandet till servern
            except:
                print("Connection closed.")
                self.client_socket.close()
                self.connected = False
                break

    def main(self) -> None:
        """Startar klienten med trådar för att ta emot och skicka meddelanden."""
        self.enter_alias()  # Användaren anger sitt namn
        self.connect_to_server()  # Försöker ansluta till servern

        if self.connected:
            """Skapar och startar trådar för att ta emot och skicka meddelanden"""
            receive_thread = threading.Thread(target=self.receive_messages)
            send_thread = threading.Thread(target=self.send_messages)
            receive_thread.start()
            send_thread.start()

            """Väntar på att trådarna ska avslutas"""
            receive_thread.join()
            send_thread.join()
        else:
            print("Failed to connect to the server.")


if __name__ == "__main__":
    client = ChatClient()
    client.main()

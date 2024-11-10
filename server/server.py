import asyncio
from datetime import datetime

class ChatServer:
    """Serverns klass"""

    def __init__(self, host: str = '0.0.0.0', port: int = 12345):
        """Initierar värden för serverns IP-adress och port, samt en dictionary för anslutna klienter"""
        self.host: str = host
        self.port: int = port
        self.clients: dict = {}  # key:writer, value:tuple(alias,tuple(ip, port))

    async def manage_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Hanterar anslutningen för varje klient"""
        try:
            alias: str = (await reader.read(512)).decode('utf-8')  # Tar emot användarens alias från klienten
            addr:tuple[str,int] = writer.get_extra_info('peername')  # Hämtar klientens adressinfo
            self.clients[writer] = (alias, addr)  # Lägger till klienten i dictionary
            print(f"{alias} connected from IP {addr[0]} on port {addr[1]} ")

            # Loop för att ta emot och befordra meddelanden vidare till alla klienter
            while True:
                data: bytes = await reader.read(1024)
                if not data:
                    break  # Om ingen data tas emot, avslutas while-loopen
                dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                message: str = f"[{dt}]{alias}:{data.decode('utf-8')}" # skriva ut date och time
                print(f'Forward message: {message}')
                await self.send_to_all_clients(message, writer)  # Skickar meddelande till alla klienter utom avsändaren
        
        except Exception as e:
            print(f' Error with {alias}: {e}')
        finally: # Körs oavsett om ett undantag inträffade i try-except eller inte
            await self.disconnect_client(writer)  # Kopplar från klienten

    async def send_to_all_clients(self, message: str, sender=None) -> None:
        """Skickar ett meddelande till alla klienter förutom avsändaren"""
        for connected_client in self.clients:
            if connected_client != sender:  # Skickar inte meddelandet tillbaka till avsändaren
                try:
                    connected_client.write(message.encode('utf-8'))
                    await connected_client.drain()  # Väntar tills meddelandet har skickats helt
                except Exception as e:
                    print(f"Error message : {e}")

    async def disconnect_client(self, writer) -> None:
        """Hanterar klientens frånkoppling och meddelar de andra"""
        if writer in self.clients:
            alias, _ = self.clients[writer]
            print(f' {alias} disconnected.')
            disconnect_message: str = f'{alias} has left the chat.'
            
            await self.send_to_all_clients(disconnect_message)  # Skickar frånkopplingsmeddelandet till andra klienter
            del self.clients[writer]  # Tar bort klienten från dictionary
        
        writer.close()  # Startar stängningen av anslutningen för denna klient
        await writer.wait_closed()  # Väntar tills anslutningen är helt stängd för att frigöra resurser

    async def run_server(self) -> None:
        """Startar en server som lyssnar på anslutningar från klienter"""
        server = await asyncio.start_server(self.manage_client_connection, self.host, self.port)
        address = server.sockets[0].getsockname()  #Hämtar det första socket-objektet som servern använder för anslutningar för att hämta IP och port där servern lyssnar
        print(f'Server starts at adress {address}')

        async with server: #Säkerställer att servern stängs av korrekt vid avslutning eller fel
            await server.serve_forever()  # Håller servern igång för att ta emot anslutningar kontinuerligt

if __name__ == "__main__":
    chat_server = ChatServer()  # Skapar ett ChatServer-objekt
    asyncio.run(chat_server.run_server())  # Kör servern asynkront

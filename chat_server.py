#!/usr/bin/env python3
"""Script Python per la realizzazione di un Server multithread
per connessioni CHAT asincrone.
Corso di Programmazione di Reti - Università di Bologna"""

from socket import AF_INET, socket, SOCK_STREAM  #modulo socket necessario per le comunicazioni di rete
from threading import Thread  #Thread per gestire le connessioni client in un contesto multithreading
import logging  #logging per la gestione e registrazione degli eventi e degli errori

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def accetta_connessioni_in_entrata():
    """Accetta le connessioni dei client in entrata."""
    while True:
        try:
            client, client_address = SERVER.accept()  # Accetta la connessione del client in entrata
        except OSError:
            logging.warning("Server chiuso.")
            break
        except Exception as e:
            logging.error(f"Errore durante l'accettazione della connessione: {e}")
            continue
        logging.info(f"Connessione da {client_address}")
        client.send(bytes("Salve! Digita il tuo Nome seguito dal tasto Invio!", "utf8"))  # Invia un messaggio di benvenuto al client
        indirizzi[client] = client_address  # Registra l'indirizzo del client in un dizionario
        Thread(target=gestione_client, args=(client,)).start()  # Avvia un nuovo thread per gestire la connessione del client

def gestione_client(client):
    """Gestisce la connessione di un singolo client."""
    nome = None
    try:
        nome = client.recv(BUFSIZ).decode("utf8")  # Riceve il nome del client
        benvenuto = f'Benvenuto {nome}! Se vuoi lasciare la Chat, scrivi {{quit}}.'  # Messaggio di benvenuto per il client
        client.send(bytes(benvenuto, "utf8"))  # Invia il messaggio di benvenuto al client
        msg = f"{nome} si è unito alla chat!"  # Messaggio broadcast per avvisare tutti i client della nuova connessione
        broadcast(bytes(msg, "utf8"))  # Invia il messaggio di nuovo utente in broadcast a tutti i client connessi
        clients[client] = nome  # Registra il client nel dizionario dei client connessi
        while True:
            try:
                msg = client.recv(BUFSIZ)  # Riceve i messaggi dal client
                if msg == bytes("{quit}", "utf8"):  # Se il client invia '{quit}', esce dalla chat
                    client.send(bytes("{quit}", "utf8"))  # Invia al client un messaggio di conferma di disconnessione
                    client.close()  # Chiude la connessione del client
                    del clients[client]  # Rimuove il client dal dizionario dei client connessi
                    broadcast(bytes(f"{nome} ha abbandonato la Chat.", "utf8"))  # Avvisa tutti i client che l'utente ha abbandonato la chat
                    break
                else:
                    broadcast(msg, nome + ": ")  # Invia il messaggio a tutti i client connessi con il prefisso del nome
            except (OSError, ConnectionResetError):
                break  # Se si verifica un errore di connessione, esce dal ciclo
    except Exception as e:
        logging.error(f"Errore durante la gestione del client: {e}")  # Gestisce gli errori durante la gestione del client
    finally:
        if client in clients:
            if nome:
                broadcast(bytes(f"{nome} ha abbandonato la Chat.", "utf8"))  # Invia un messaggio broadcast che il client ha lasciato la chat
            del clients[client]  # Rimuove il client dal dizionario dei client connessi
        client.close()  # Chiude la connessione del client

def broadcast(msg, prefisso=""):
    """Invia un messaggio in broadcast a tutti i client."""
    for utente in clients:
        try:
            utente.send(bytes(prefisso, "utf8") + msg)  # Invia il messaggio in broadcast a tutti i client connessi
        except (BrokenPipeError, ConnectionResetError) as e:
            logging.error(f"Errore durante l'invio del messaggio in broadcast: {e}")  # Gestisce gli errori durante l'invio del messaggio in broadcast
            utente.close()  
clients = {}  # Dizionario per registrare i client connessi
indirizzi = {}  # Dizionario per memorizzare gli indirizzi dei client connessi

HOST = ''  # Indirizzo IP del server
PORT = 53000  # Porta del server
BUFSIZ = 1024  # Dimensione del buffer per la ricezione dei messaggi
ADDR = (HOST, PORT)  # Coppia indirizzo IP e porta del server

SERVER = socket(AF_INET, SOCK_STREAM)  # Crea il server socket
SERVER.bind(ADDR)  # Collega il server all'indirizzo e alla porta specificati

if __name__ == "__main__":
    try:
        SERVER.listen(5)  # Mette il server in ascolto per accettare un massimo di 5 connessioni in coda
        print("In attesa di connessioni...")  # Stampa un messaggio per indicare che il server è in attesa di connessioni
        ACCEPT_THREAD = Thread(target=accetta_connessioni_in_entrata)  # Crea un thread per gestire l'accettazione delle connessioni in entrata
        ACCEPT_THREAD.start()  # Avvia il thread per gestire l'accettazione delle connessioni in entrata
        ACCEPT_THREAD.join()  # Attende che il thread di gestione delle connessioni in entrata finisca
        SERVER.close()  # Chiude il socket del server una volta che il thread di gestione delle connessioni in entrata è terminato
    except  Exception as e:
        print("Errore generale:", e )  # Gestisce eventuali errori generici durante l'esecuzione del server
    finally:
       SERVER.close()  # Chiude il socket del server una volta che il thread di gestione delle connessioni in entrata è terminato
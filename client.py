# -*- coding: utf-8 -*-
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
from datetime import datetime

def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Imposta anno-mese-giorno e l'ora di invio del messaggio
                formatted_msg = f"{timestamp} - {msg}"
                msg_list.insert(tk.END, formatted_msg)
            else:
                break  # Interrompe il ciclo se il server si è disconnesso
        except OSError as e:
            if str(e) == "[Errno 9] Bad file descriptor":
                break  # Socket chiuso, termina il ciclo
            else:
                print(f"Errore di ricezione: {e}")
                break  # Qualsiasi altro errore, termina il ciclo

def send(event=None):
    """Sends messages."""
    msg = my_msg.get()  # Ottiene il testo dall'entry field
    my_msg.set("")  # Resetta l'entry field dopo l'invio del messaggio
    try:
        client_socket.send(bytes(msg, "utf8"))  # Invia il messaggio al server
        if msg == "{quit}":  # Se il messaggio è '{quit}', chiude la connessione e la finestra
            client_socket.close()
            finestra.quit()
    except OSError:
        pass  # Gestisce eventuali errori durante l'invio del messaggio

def on_closing(event=None):
    my_msg.set("{quit}")  # Imposta il messaggio di uscita
    send()  # Chiama la funzione send per inviare il messaggio di uscita
    try:
        client_socket.close()  # Chiude il socket
    except OSError:
        pass
    finestra.quit()  # Chiude la finestra
    finestra.destroy()

def show_chat_window():
    global finestra, my_msg, msg_list
    finestra = tk.Tk()
    finestra.title("Chat Client")  # Imposta il titolo della finestra

    # Creazione del frame per i messaggi
    messages_frame = tk.Frame(finestra)  # Crea un frame per contenere i messaggi
    my_msg = tk.StringVar()  # Variabile per memorizzare l'input dell'utente
    my_msg.set("Scrivi qui i tuoi messaggi.")  # Imposta il testo predefinito nel campo di input
    scrollbar = tk.Scrollbar(messages_frame)  # Crea una barra di scorrimento
    msg_list = tk.Listbox(messages_frame, height=15, width=75, yscrollcommand=scrollbar.set)  # Crea una lista per i messaggi
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Posiziona la barra di scorrimento a destra del frame
    msg_list.pack(side=tk.LEFT, fill=tk.BOTH)  # Posiziona la lista dei messaggi a sinistra del frame
    msg_list.pack()  # Configura la barra di scorrimento per scorrere la lista dei messaggi
    messages_frame.pack()  # Mostra il frame dei messaggi nella finestra principale

    # Creazione del campo di input per i messaggi
    entry_field = tk.Entry(finestra, textvariable=my_msg)  # Crea un campo di input per i messaggi
    entry_field.bind("<Return>", send)  # Lega la pressione del tasto Invio alla funzione send
    entry_field.pack()  # Mostra il campo di input nella finestra principale

    # Creazione del pulsante di invio
    send_button = tk.Button(finestra, text="Invio", command=send)  # Crea un pulsante per inviare i messaggi
    send_button.pack()  # Mostra il pulsante nella finestra principale

    finestra.protocol("WM_DELETE_WINDOW", on_closing)  # Associa la funzione on_closing alla chiusura della finestra

    receive_thread = Thread(target=receive)  # Crea un thread per gestire la ricezione dei messaggi
    receive_thread.start()  # Avvia il thread per la ricezione dei messaggi

    tk.mainloop()  # Avvia il ciclo principale di Tkinter per gestire gli eventi

def connect_to_server():
    global client_socket, BUFSIZ, login_window
    HOST = host_entry.get()
    PORT = port_entry.get()
    if not PORT:
        PORT = 53000  # Imposta la porta predefinita se l'utente non fornisce alcun input
    else:
        PORT = int(PORT)  # Converte la porta in un intero (se l'utente fornisce un input)
    BUFSIZ = 1024  # Dimensione del buffer per la ricezione dei messaggi
    ADDR = (HOST, PORT)  # Coppia indirizzo IP e porta del server

    client_socket = socket(AF_INET, SOCK_STREAM)  # Crea un socket utilizzando IPv4 e TCP
    try:
        client_socket.connect(ADDR)  # Si connette all'indirizzo del server definito da ADDR
        login_window.destroy()  # Chiude la finestra di login
        show_chat_window()  # Mostra la finestra della chat
    except Exception as e:
        error_label.config(text=f"Errore di connessione: {e}")

# Creazione della finestra di login
login_window = tk.Tk()
login_window.title("Login Chat Client")  # Imposta il titolo della finestra di login

# Creazione e posizionamento degli elementi della GUI di login
tk.Label(login_window, text="Inserisci Server Host:").pack(pady=10)  # Etichetta per l'host del server
host_entry = tk.Entry(login_window)  # Campo di input per l'host del server
host_entry.pack(pady=10)  # Posiziona il campo di input con un padding verticale

tk.Label(login_window, text="Inserisci Porta del server:").pack(pady=10)  # Etichetta per la porta del server
port_entry = tk.Entry(login_window)  # Campo di input per la porta del server
port_entry.pack(pady=10)  # Posiziona il campo di input con un padding verticale

error_label = tk.Label(login_window, text="", fg="red")  # Etichetta per mostrare errori di connessione
error_label.pack(pady=10)  # Posiziona l'etichetta con un padding verticale

connect_button = tk.Button(login_window, text="Connetti", command=connect_to_server)  # Pulsante per connettersi al server
connect_button.pack(pady=20)  # Posiziona il pulsante con un padding verticale

login_window.mainloop()  # Avvia il ciclo principale di Tkinter per gestire gli eventi

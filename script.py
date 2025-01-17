from selenium import webdriver
from selenium.webdriver.common.by import By
import pytchat
import time
import tkinter as tk
from tkinter import simpledialog, ttk
import threading

# Variáveis globais
driver = None
continue_running = True
youtube_live_url = "https://www.youtube.com/watch?v=bS31P1JA0dY"
chat = None

def update_status(message):
    status_label.config(text=message)
    status_label.update_idletasks()
    print(message)  # Adiciona um log para debug

def start_automation():
    global driver
    global continue_running
    global youtube_live_url

    # Verificar se a automação já está em execução
    if driver:
        update_status("Automação já está em execução.")
        return

    # Pedir o input do nome de usuário
    username = username_entry.get()
    if not username:
        update_status("Por favor, digite o nome de usuário.")
        return

    # Pedir o URL da live no YouTube
    youtube_live_url = simpledialog.askstring("URL da Live no YouTube", "Digite o URL da live no YouTube:")
    if not youtube_live_url or "youtube.com" not in youtube_live_url:
        update_status("Por favor, digite um URL válido do YouTube.")
        return

    # Iniciar thread para automação
    update_status("Iniciando automação...")
    threading.Thread(target=automation_thread, args=(username,), daemon=True).start()

def automation_thread(username):
    global driver
    global chat
    global continue_running

    try:
        if not driver:
            driver = webdriver.Chrome()

        update_status("Acessando a live no YouTube...")
        driver.get(youtube_live_url)

        update_status("Esperando o chat carregar...")
        time.sleep(10)

        video_id = youtube_live_url.split('v=')[-1]
        chat = pytchat.create(video_id=video_id)

        if not chat.is_alive():
            update_status("Falha ao conectar com o chat ao vivo.")
            return

        # Iniciar uma thread separada para monitorar o chat
        threading.Thread(target=monitor_chat, args=(username,), daemon=True).start()

    except Exception as e:
        update_status(f"Erro na automação: {e}")

    update_status("Automação encerrada.")

def monitor_chat(username):
    global chat
    global continue_running

    while continue_running:
        try:
            for c in chat.get().sync_items():
                author_type = c.author.type  # owner, moderator, member, etc.
                if author_type == "owner":
                    update_status(f"Mensagem de {c.author.name}: {c.message}")
                    if "forms.gle" in c.message:
                        update_status("Abrindo o link do formulário em uma nova aba...")
                        link = c.message.split(' ')[-1]  # Supondo que o link seja a última parte da mensagem
                        open_form(driver, link, username)
                    else:
                        update_status("Abrindo o formulário de teste.")
                        open_test_form(driver, username)
            time.sleep(2)
        except Exception as e:
            update_status(f"Erro ao monitorar o chat: {e}")

def open_form(driver, link, username):
    try:
        driver.execute_script(f"window.open('{link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        update_status("Esperando o formulário carregar...")
        time.sleep(5)

        update_status("Preenchendo o formulário...")
        form_field = driver.find_element(By.XPATH, "//input[@type='text']")
        form_field.send_keys(username)

        update_status("Enviando o formulário...")
        submit_button = driver.find_element(By.XPATH, "//span[text()='Enviar']")
        submit_button.click()

        update_status("Formulário preenchido com sucesso!")

    except Exception as e:
        update_status(f"Erro ao abrir o formulário: {e}")

def open_test_form(driver, username):
    try:
        update_status("Abrindo formulário de teste em uma nova aba...")
        test_form_url = "https://forms.gle/NQHW5SXKNwX4V4iRA"
        driver.execute_script(f"window.open('{test_form_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        update_status("Esperando o formulário de teste carregar...")
        time.sleep(5)

        update_status("Preenchendo o formulário de teste...")
        form_field = driver.find_element(By.XPATH, "//input[@type='text']")
        form_field.send_keys(username)

        update_status("Enviando o formulário de teste...")
        submit_button = driver.find_element(By.XPATH, "//span[text()='Enviar']")
        submit_button.click()

        update_status("Formulário de teste preenchido com sucesso!")

    except Exception as e:
        update_status(f"Erro ao abrir o formulário de teste: {e}")

def close_application():
    global continue_running
    continue_running = False

    global driver
    if driver:
        driver.quit()
        update_status("Navegador fechado.")
    root.destroy()

# Criar a interface gráfica
root = tk.Tk()
root.title("Automação de Preenchimento de Formulário")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

username_label = ttk.Label(frame, text="Nome de usuário:")
username_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

username_entry = ttk.Entry(frame, width=25)
username_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

start_button = ttk.Button(frame, text="Iniciar Automação", command=start_automation)
start_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

close_button = ttk.Button(frame, text="Encerrar Aplicação", command=close_application)
close_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

status_label = ttk.Label(frame, text="Status: Aguardando início", relief="sunken", anchor=tk.W)
status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

root.mainloop()

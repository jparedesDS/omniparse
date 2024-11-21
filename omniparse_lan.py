import os
import subprocess
import threading
import time
import socket
import urllib.request
import torch

# Clonar el repositorio
def clone_repo():
    subprocess.run(["git", "clone", "https://github.com/adithya-s-k/omniparse.git"])
    os.chdir("omniparse")

# Instalar dependencias del repositorio omniparse
def install_dependencies():
    subprocess.run(["pip", "install", "-e", "."])
    subprocess.run(["pip", "install", "transformers==4.41.2"])

# Actualizar e instalar paquetes necesarios
def install_system_packages():
    subprocess.run([
        "apt-get", "update", "&&", "apt-get", "install", "-y", "--no-install-recommends",
        "wget", "curl", "unzip", "git", "libgl1", "libglib2.0-0", "gnupg2", "ca-certificates",
        "apt-transport-https", "software-properties-common", "libreoffice", "ffmpeg", "git-lfs",
        "xvfb", "&&", "ln", "-s", "/usr/bin/python3", "/usr/bin/python", "&&",
        "curl", "-s", "https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh", "|", "bash",
        "&&", "wget", "-q", "-O", "-", "https://dl.google.com/linux/linux_signing_key.pub", "|", "apt-key", "add", "-",
        "&&", "echo", "deb http://dl.google.com/linux/chrome/deb/ stable main", ">", "/etc/apt/sources.list.d/google-chrome.list",
        "&&", "apt-get", "update", "&&", "apt", "install", "-y", "python3-packaging", "google-chrome-stable",
        "&&", "rm", "-rf", "/var/lib/apt/lists/*"
    ], shell=True)

# Descargar e instalar ChromeDriver
def install_chromedriver():
    chromedriver_version = subprocess.check_output("curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE", shell=True).decode("utf-8").strip()
    subprocess.run([
        "wget", "-q", "-N", f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip", "-P", "/tmp"
    ])
    subprocess.run(["unzip", "-o", "/tmp/chromedriver_linux64.zip", "-d", "/tmp"])
    subprocess.run(["mv", "/tmp/chromedriver", "/usr/local/bin/chromedriver"])
    subprocess.run(["chmod", "+x", "/usr/local/bin/chromedriver"])
    subprocess.run(["rm", "/tmp/chromedriver_linux64.zip"])


# Establecer variables de entorno
def set_environment_variables():
    os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
    os.environ['CHROMEDRIVER'] = '/usr/local/bin/chromedriver'
    os.environ['DISPLAY'] = ':99'
    os.environ['DBUS_SESSION_BUS_ADDRESS'] = '/dev/null'
    os.environ['PYTHONUNBUFFERED'] = '1'

# Descargar e instalar Cloudflare
def install_cloudflared():
    subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"])
    subprocess.run(["dpkg", "-i", "cloudflared-linux-amd64.deb"])

# Función para iniciar Cloudflare tunnel
def start_cloudflare_thread(port):
    def cloudflare_thread():
        while True:
            time.sleep(0.5)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                break
            sock.close()
        print("\nOmniparse API loaded, launching cloudflared (if it gets stuck, cloudflared may have issues)\n")

        p = subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in p.stderr:
            l = line.decode()
            if "trycloudflare.com" in l:
                print("URL to access Omniparse:", l[l.find("http"):], end='')

    threading.Thread(target=cloudflare_thread, daemon=True).start()

# Instalar localtunnel
def install_localtunnel():
    subprocess.run(["npm", "install", "-g", "localtunnel"])

# Función para iniciar Localtunnel
def start_localtunnel_thread(port):
    def localtunnel_thread():
        while True:
            time.sleep(0.5)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                break
            sock.close()
        print("\nOmniparse loaded, launching localtunnel (if it gets stuck, localtunnel may have issues)\n")

        ip_address = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip()
        print("Localtunnel access IP:", ip_address)
        p = subprocess.Popen(["lt", "--port", str(port)], stdout=subprocess.PIPE)
        for line in p.stdout:
            print(line.decode(), end='')

    threading.Thread(target=localtunnel_thread, daemon=True).start()

# Iniciar el servidor de Omniparse
def start_server():
    subprocess.run(["python", "server.py", "--host", "127.0.0.1", "--port", "8000", "--documents", "--media", "--web"])

# Ejecución del setup completo
if __name__ == "__main__":
    print("Iniciando configuración de Omniparse...")
    clone_repo()
    install_dependencies()
    install_system_packages()
    #install_chromedriver()
    set_environment_variables()
    install_cloudflared()
    install_localtunnel()
    start_cloudflare_thread(8000)
    start_localtunnel_thread(8000)
    start_server()
    print("✅ Configuración completa")

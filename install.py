from __future__ import print_function
from os import system


def prompt(tool_name, command):
    r = input("[%s] %s (Yes/no): " % (tool_name, command))
    if r in ["", "y", "Y", "yes"]:
        system(command)
    elif r in ["n", "N", "no"]:
        return
    else:
        print("exit!")
        exit(1)


def main():
    print("Configure installation scripts\n")
    r = input(
        "Choose install method [Ask before each installation/istall immmediately] :")
    if r in ["I", "i", "Install", "install"]:
        def prompt(_, command): return system(command)

    print("[DIR]")
    prompt("mkdir", "mkdir ~/coding ~/tmp ~/tools && mkdir ~/coding/golang ~/coding/java ~/coding/nodejs ~/coding/python")

    print("\n\n[PROGRAMING LANGUAGE]")
    prompt("go", "wget -c https://dl.google.com/go/go1.17.6.linux-amd64.tar.gz -O - | sudo tar -xz -C /usr/local")

    print("\n\n[TOOL]")
    prompt("apt update", "apt update")
    prompt("git", "sudo apt-get install -qq -y git")
    prompt("vim-gtk", "sudo apt-get install -qq -y vim-gtk")
    prompt("gitclone", 'git config --global url."https://github.com.cnpmjs.org/".insteadOf https://github.com/')
    prompt("zsh", "sudo apt-get install -qq -y zsh && chsh -s $(which zsh)")
    prompt("bat", "sudo apt-get install -qq -y bat")
    prompt("fzf", "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install")
    prompt("lsd", "wget https://github.91chi.fun//https://github.com//Peltoche/lsd/releases/download/0.20.1/lsd_0.20.1_amd64.deb && sudo dpkg -i lsd_0.20.1_amd64.deb && rm lsd_0.20.1_amd64.deb")
    prompt("fd", "sudo apt-get install -qq -y fd-find")
    prompt("ag", "sudo apt-get install -qq -y silversearcher-ag")
    prompt("docker", "curl -fsSL https://get.docker.com | sudo bash -s docker --mirror Aliyun")
    prompt("pipx", "apt-get install -qq -y python3.8-venv && sudo pip3 install pipx")
    prompt("pdm", "sudo pipx install pdm")
    prompt("python tools", "sudo pip3 install ctfbox pyperclip")
    prompt("ptipython", "sudo pip3 install ptipython")
    prompt("docker-compose", "sudo pipx install docker-compose")

    print("\n\n[XCLIP]")
    prompt("xclip", "apt-get install -qq -y xclip")
    prompt("write sshd_config",
           "sudo echo X11Forwarding yes >> /etc/ssh/sshd_config")
    prompt("restart sshd", "service sshd restart")

    print("\n\n[INIT]")
    prompt("init config",
           "git clone https://github.com/WAY29/remote_dev_config ~/config && mv ~/config/tmux.sh ~/tmux.sh && mv ~/config/.[^.]* ~")
    prompt("remove config dir", "rm -rf ~/config")
    prompt("chmod", "chmod +x ~/tmux.sh")
    prompt("remove myself", "rm " + __file__)
    prompt("init zsh", "zsh")


main()

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

    print("[DIR]")
    prompt("mkdir", "mkdir ~/coding ~/tmp ~/tools && mkdir ~/coding/golang ~/coding/java ~/coding/nodejs ~/coding/python")

    print("\n\n[PROGRAMING LANGUAGE]")
    prompt("go", "wget https://dl.google.com/go/go1.17.6.linux-amd64.tar.gz && sudo tar -xzf go1.17.6.linux-amd64.tar.gz -C /usr/local && rm go1.17.6.linux-amd64.tar.gz")
    prompt("go proxy", "/usr/local/go/bin/go env -w GOPROXY=https://goproxy.cn,direct")
    print("\n\n[TOOL]")
    prompt("apt update", "sudo apt update")
    prompt("git", "sudo apt-get install -qq -y git")
    prompt("vim-gtk", "sudo apt-get install -qq -y vim-gtk")
    prompt("gitclone in china", 'git config --global url."https://github.91chi.fun//https://github.com/".insteadOf https://github.com/')
    prompt("zsh", "sudo apt-get install -qq -y zsh && chsh -s $(which zsh)")
    prompt("zoxide", "curl -sS https://webinstall.dev/zoxide | bash")
    prompt("bat", "curl -sS https://webinstall.dev/bat | bash")
    prompt("fzf", "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && cd ~/.fzf && FZF_VERSION=0.27.2 make install && sudo mv bin/fzf /usr/local/bin/fzf")
    prompt("lsd", "curl -sS https://webinstall.dev/lsd | bash")
    prompt("ag", "sudo apt-get install -qq -y silversearcher-ag")
    prompt("fd", "curl -sS https://webinstall.dev/fd | bash")
    prompt("docker", "curl -fsSL https://get.docker.com | sudo bash -s docker --mirror Aliyun")
    prompt("kubectl", '''curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && install kubectl /usr/local/bin/kubectl && rm kubectl''')
    prompt("minikube", '''curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64''')
    prompt("pipx", "apt-get install -qq -y python3-venv && sudo pip3 install pipx")
    prompt("pdm", "sudo pipx install pdm")
    prompt("python tools", "sudo python3.8 -m pip install ctfbox pyperclip")
    prompt("ptipython", "sudo pip3 install ptipython")
    prompt("docker-compose", "sudo pipx install docker-compose")

    # print("\n\n[XCLIP]")
    # prompt("xclip", "apt-get install -qq -y xclip")
    # prompt("write sshd_config",
    #        "sudo echo X11Forwarding yes >> /etc/ssh/sshd_config")
    # prompt("restart sshd", "service sshd restart")

    print("\n\n[INIT]")
    prompt("init config",
           "git clone https://github.com/WAY29/remote_dev_config ~/config && mv ~/config/tmux.sh ~/tmux.sh && mv ~/config/.[^.]* ~")
    prompt("remove config dir", "rm -rf ~/config")
    prompt("chmod", "chmod +x ~/tmux.sh")
    prompt("remove myself", "rm " + __file__)
    prompt("init zsh", "zsh")


main()

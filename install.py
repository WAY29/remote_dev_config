from os import system


def prompt(tool_name, command):
    r = input("[%s] %s (Yes/no): " % (tool_name, command))
    if r in ["", "y", "Y", "yes"]:
        system(command)
    else:
        print("exit!")
        exit(1)


def main():
    print("[DIR]")
    prompt("mkdir", "mkdir coding tmp tools && mkdir coding/golang coding/java coding/nodejs coding/python")

    print("\n\n[PROGRAMING LANGUAGE]")
    prompt("go", "wget -c https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz -O - | sudo tar -xz -C /usr/local")

    print("\n\n[TOOL]")
    prompt("git", "sudo apt install git")
    prompt("zsh", "sudo apt install zsh && chsh -s $(which zsh)")
    prompt("bat", "sudo apt install bat")
    prompt("fzf", "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install")
    prompt("lsd", "wget https://github.91chi.fun//https://github.com//Peltoche/lsd/releases/download/0.20.1/lsd_0.20.1_amd64.deb && sudo dpkg -i lsd_0.20.1_amd64.deb && rm lsd_0.20.1_amd64.deb")
    prompt("fd", "sudo apt install fd-find")
    prompt("ag", "sudo apt install silversearcher-ag")
    prompt("docker", "curl -fsSL https://get.docker.com | sudo bash -s docker --mirror Aliyun")
    prompt("pipx", "apt install python3.8-venv && sudo pip3 install pipx")
    prompt("pdm", "sudo pipx install pdm")

    print("\n\n[OTHER]")
    prompt("gitclone", 'git config --global url."https://gitclone.com/".insteadOf https://')

    print("\n\n[INIT]")
    prompt("init config", "git clone https://github.com/WAY29/remote_dev_config ~/config && mv ~/config/* ~ && mv ~/config/.[^.]* ~ && rm -rf ~/config")
    prompt("chmod", "chmod +x ~/tmux.sh")
    prompt("init zsh", "zsh")

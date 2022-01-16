### Added by Zinit's installer
if [[ ! -f $HOME/.zinit/bin/zinit.zsh ]]; then
    print -P "%F{33}▓▒░ %F{220}Installing %F{33}DHARMA%F{220} Initiative Plugin Manager (%F{33}zdharma/zinit%F{220})…%f"
    command mkdir -p "$HOME/.zinit" && command chmod g-rwX "$HOME/.zinit"
    command git clone https://github.com.cnpmjs.org/zdharma-continuum/zinit "$HOME/.zinit/bin" && \
        print -P "%F{33}▓▒░ %F{34}Installation successful.%f%b" || \
        print -P "%F{160}▓▒░ The clone has failed.%f%b"
fi

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# load zinit
source "$HOME/.zinit/bin/zinit.zsh"


# plugins
zinit ice lucid wait='0' atload='_zsh_autosuggest_start'
zinit light zsh-users/zsh-autosuggestions
zinit ice lucid wait='0'
zinit light zdharma-continuum/fast-syntax-highlighting
zinit ice lucid wait='0'
zinit light Aloxaf/fzf-tab
zinit ice lucid wait='0'
zinit snippet OMZ::plugins/sudo/sudo.plugin.zsh
zinit ice lucid wait='0'
zinit snippet OMZ::plugins/extract/extract.plugin.zsh
zinit light zsh-users/zsh-completions
zinit ice depth=1; zinit light romkatv/powerlevel10k
zinit ice lucid wait='0'
zinit light djui/alias-tips

# set list-colors to enable filename colorizing
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

# zinit config
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

# Load a few important annexes, without Turbo
# (this is currently required for annexes)
zinit light-mode for \
    zinit-zsh/z-a-rust \
    zinit-zsh/z-a-as-monitor \
    zinit-zsh/z-a-patch-dl \
    zinit-zsh/z-a-bin-gem-node

### End of Zinit's installer chunk

# p10k
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# my_cd
function my_cd() {
    \cd $1 && lsd
}

# my b for back number dirs
function my_b() {
j=${1-1}
depth=''
p='../'
for (( i = 0; i < $j; i++  ))
do
    depth+=$p
done
my_cd $depth
}

# fzf 
# command for listing path candidates.
# - The first argument to the function ($1) is the base path to start traversal
# - See the source code (completion.{bash,zsh}) for the details.
_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}

# Use fd to generate the list for directory completion
_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}

## -------------------------------------------

# my v for preview
function my_v() {
fdfind -E .git -H -I | fzf --bind 'ctrl-e:execute(vim {})' \
                           --bind 'ctrl-b:execute(bat {})' \
                           --preview '[[ $(file --mime {}) =~ binary ]] &&
                 echo {} is a binary file ||
                 (bat --style=numbers --color=always {} ||
                  highlight -O ansi -l {} ||
                  coderay {} ||
                  rougify {} ||
                  cat {}) 2> /dev/null | head -500'
}

# command not found
source /etc/zsh_command_not_found


# PATH
export PATH=$PATH":$HOME/.local/bin:$HOME/tools"

# WORK
# python
export pywork="$HOME/coding/python"
# go
export GOPATH="$HOME/coding/golang"
export PATH="$PATH:/usr/local/go/bin:$GOPATH/bin"

# url function
alias urlencode='python3 -c "import sys; import urllib.parse as up; del sys.path[0]; text = sys.argv[1] if len(sys.argv) >= 2 else \"\".join(sys.stdin.readlines()); print(up.quote_plus(text).strip())"'
alias urldecode='python3 -c "import sys; import urllib.parse as up; del sys.path[0]; text = sys.argv[1] if len(sys.argv) >= 2 else \"\".join(sys.stdin.readlines()); print(up.unquote_plus(text).strip())"'



# PYTHONSTARTUP
export PYTHONSTARTUP="$HOME/.config/ptpython/startup.py"


# history
export HISTFILE=~/.zsh_history
export HISTSIZE=10000
export SAVEHIST=10000
setopt SHARE_HISTORY

# alias tools
alias reload_config='source ~/.zshrc'
alias edit_config='vi ~/.zshrc'
alias ag='ag --hidden -a'
alias o='open'
alias d='docker'
alias dirmap='cd /home/longlone/tools/dirmap && python3 dirmap.py'
alias check_port='test() {lsof -i:$1}; test'
alias http_server='python3 -m http.server'
alias ipy='ptipython'
alias ipython='ptipython'
alias ls='lsd'
alias sqlmap='python3 /home/longlone/tools/sqlmap/sqlmap.py'
# sudo for me
alias openvpn='sudo openvpn'
alias thm='sudo openvpn /home/longlone/tryhackme/Mimei.ovpn &'
alias sd='sudo service docker start'
alias bak='test() { cp $1 $1".bak";}; test'
alias attach='test() { sudo docker attach dwn_$1;}; test'
alias ds='docker start'
alias dins='docker inspect'
alias dimg='docker images'
alias dsh='test() { docker exec --user root -it $1 sh;}; test'
alias dbash='test() { docker exec --user root -it $1 bash;}; test'
alias dcbash='test() { docker-compose exec --user root $1 bash;}; test'
alias dmicro='test() {docker cp /usr/bin/micro.tiny $1:/usr/bin/micro}; test'
alias dclean='docker system prune'
alias ddown='docker-compose down -v'
alias dip='test() {docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" $1;}; test'
alias dlog='test() {docker logs $1;}; test'
alias dps='docker ps'
alias drm='test() {docker stop $1 && docker rm $1;}; test'
alias drun='test() {docker run -itd -p $1:80 $2;}; test'
alias dup='docker-compose up -d --build'
# other alias
alias ll='ls -al'
alias grep='grep --color=auto'
alias rm='rm -I --preserve-root'
alias cp='cp -i'
alias mv='mv -i'
alias c=my_cd
alias cd=my_cd
alias b=my_b
alias v=my_v
alias q=exit
alias fd='fdfind -E .git -H -I'
alias ..='my_cd ..'
alias ...='my_cd ../..'
alias ....='my_cd ../../..'
alias mt='~/tmux.sh'
alias no_history='unset HISTORY HISTFILE HISTSAVE HISTZONE HISTORY HISTLOG'
alias uptty='stty raw -echo;fg'
alias cat='batcat -n --theme=OneHalfDark'
alias copy='clip.exe'
alias vi='stty -ixon; vim'
alias vim='stty -ixon; vim'

# tldr colors
export TLDR_HEADER='magenta bold underline'
export TLDR_QUOTE='bold'
export TLDR_DESCRIPTION='yellow'
export TLDR_CODE='green'
export TLDR_PARAM='blue'

# dircolors
export LS_COLORS='rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=33;33:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:'

# grep colors
export GREP_COLOR='1;35'

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# FZF
export FZF_DEFAULT_COMMAND="ag -g ''"
export FZF_ALT_C_COMMAND="echo .. & fdfind -H --type d --color=never"

#C-R C-L
bindkey ";5C" forward-word
bindkey ";5D" backward-word

# with
with() {
    TOPCMD=$@ bash -c 'while read -p "${TOPCMD##*/}> " -ra sub; do
        case ${sub[0]:-} in
        "") continue;;
        exit) exit;;
        escape) (set -x; ${sub[@]:1});;
        *) (set -x; ${TOPCMD} ${sub[@]});;
        esac
        done'
}

# pdm 582
if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH='/usr/local/lib/python3.8/dist-packages/pdm/pep582':$PYTHONPATH
else
    export PYTHONPATH='/usr/local/lib/python3.8/dist-packages/pdm/pep582'
fi

# Generated for envman. Do not edit.
[ -s "$HOME/.config/envman/load.sh" ] && source "$HOME/.config/envman/load.sh"

# zoxide
eval "$(zoxide init --cmd c zsh)"
alias cl='cq -l'

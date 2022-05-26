# /bin/sh

session="sh"
tmux has-session -t $session 2>/dev/null
if [ $? != 0 ]
then
	tmux new-session -s $session -d
	tmux split-window -h -t $session:1.1
	tmux new-window -n zsh
	tmux split-window -h -t $session:2.1
    tmux new-window -n zsh
	tmux split-window -h -t $session:3.1
fi
tmux select-window -t $session:1
tmux select-pane -t $session:1.1 2>/dev/null
tmux attach -t $session 2>/dev/null



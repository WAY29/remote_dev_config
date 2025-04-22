set nocompatible
filetype off
set history=1000
set mouse=a
syntax enable
"使用空格来替换Tab"
set expandtab
"删除行
set backspace=2

"设置所有的Tab和缩进为4个空格"
set tabstop=4

"设定<<和>>命令移动时的宽度为4"
set shiftwidth=4

"设置软宽度"
set sw=4

"增强模式中的命令行自动完成操作"
set wildmenu

"显示行数"
set nu

"显示相对行号"
set relativenumber

"光标线"
set cursorline

"当搜索到结尾时会从开头寻找"
set wrapscan

"搜索高亮"
set hlsearch

"设置paste键"
set pastetoggle=<F9>

"设置文件编码"
set fileencodings=utf-8

"设置终端编码"
set termencoding=utf-8

"设置语言编码"
set langmenu=zh_CN.UTF-8
set helplang=cn

"设置背景颜色"
set background=dark

"保存"
nnoremap <c-s> :<c-u>update<cr>
vnoremap <c-s> <c-c>:update<cr>gv
inoremap <c-s> <c-o>:update<cr>
"退出"
nnoremap <c-w> :<c-u>:q<cr>
vnoremap <c-w> <c-c>:q<cr>gv
inoremap <c-w> <c-o>:q<cr>

"移动行"
execute "set <M-j>=\ej"
execute "set <M-k>=\ek"
nnoremap <M-j> mz:m+<cr>`z
nnoremap <M-k> mz:m-2<cr>`z
vnoremap <M-j> :m'>+<cr>`<my`>mzgv`yo`z
vnoremap <M-k> :m'<-2<cr>`>my`<mzgv`yo`z
"快进和后退
noremap <silent> J 5j
noremap <silent> K 5k
"行内移动
nnoremap H ^
nnoremap L $
nnoremap <tab> w
nnoremap <S-tab> b

"leader键"
let mapleader = "\<space>"
nnoremap <Leader>d  <C-d>
nnoremap <Leader>u  <C-u>
nnoremap <Leader>f  <C-f>
nnoremap <Leader>b  <C-b>
nnoremap <leader><leader> ``
nnoremap <leader>; $a;<ESC>

"vim-hardtime设置"
let g:hardtime_default_on = 0
let g:hardtime_timeout = 500 

"插入时光标改变
let &t_SI = "\e[6 q"
let &t_EI = "\e[2 q"
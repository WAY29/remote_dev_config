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

"复制黏贴"
let g:max_osc52_sequence=1000000
function! SendViaOSC52(str)
  if get(g:, 'osc52_term', 'tmux') == 'tmux'
    let osc52 = s:get_OSC52_tmux(a:str)
  elseif get(g:, 'osc52_term', 'tmux') == 'screen'
    let osc52 = s:get_OSC52_DCS(a:str)
  elseif !empty($TMUX)
    let osc52 = s:get_OSC52_tmux(a:str)
  elseif match($TERM, 'screen') > -1
    let osc52 = s:get_OSC52_DCS(a:str)
  else
    let osc52 = s:get_OSC52(a:str)
  endif

  let len = strlen(osc52)
  if len < g:max_osc52_sequence
    call s:rawecho(osc52)
  else
    echo "Selection too long to send to terminal: " . len
  endif
endfun

function! s:get_OSC52(str)
  let b64 = s:b64encode(a:str, 0)
  let rv = "\e]52;c;" . b64 . "\x07"
  return rv
endfun

function! s:get_OSC52_tmux(str)
  let b64 = s:b64encode(a:str, 0)
  let rv = "\ePtmux;\e\e]52;c;" . b64 . "\x07\e\\"
  return rv
endfun

function! s:get_OSC52_DCS(str)
  let b64 = s:b64encode(a:str, 76)
  let b64 = substitute(b64, '\n*$', '', '')
  let b64 = substitute(b64, '\n', "\e/\eP", "g")
  let b64 = substitute(b64, '/', '\', 'g')
  let b64 = "\eP\e]52;c;" . b64 . "\x07\e\x5c"

  return b64
endfun

function! s:rawecho(str)
  let redraw = get(g:, 'osc52_redraw', 2)
  let print  = get(g:, 'osc52_print', 'echo')
  if print == 'echo'
    exe "silent! !echo" shellescape(a:str)
  elseif print == 'printf'
    exe "silent! !printf \\%s" shellescape(a:str)
  else
    exe print shellescape(a:str)
  endif
  if redraw == 2
    redraw!
  elseif redraw == 1
    redraw
  endif
endfun

let s:b64_table = [
      \ "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P",
      \ "Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f",
      \ "g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v",
      \ "w","x","y","z","0","1","2","3","4","5","6","7","8","9","+","/"]

function! s:b64encode(str, size)
  let bytes = s:str2bytes(a:str)
  let b64 = []

  for i in range(0, len(bytes) - 1, 3)
    let n = bytes[i] * 0x10000
          \ + get(bytes, i + 1, 0) * 0x100
          \ + get(bytes, i + 2, 0)
    call add(b64, s:b64_table[n / 0x40000])
    call add(b64, s:b64_table[n / 0x1000 % 0x40])
    call add(b64, s:b64_table[n / 0x40 % 0x40])
    call add(b64, s:b64_table[n % 0x40])
  endfor

  if len(bytes) % 3 == 1
    let b64[-1] = '='
    let b64[-2] = '='
  endif

  if len(bytes) % 3 == 2
    let b64[-1] = '='
  endif

  let b64 = join(b64, '')
  if a:size <= 0
    return b64
  endif

  let chunked = ''
  while strlen(b64) > 0
    let chunked .= strpart(b64, 0, a:size) . "\n"
    let b64 = strpart(b64, a:size)
  endwhile
  return chunked
endfun

function! s:str2bytes(str)
  return map(range(len(a:str)), 'char2nr(a:str[v:val])')
endfun

command! Oscyank call SendViaOSC52(getreg('"'))
set clipboard+=unnamedplus
vmap <C-c> y:Oscyank<cr>
vmap y y:Oscyank<cr>


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

augroup myCmds
au!
autocmd VimEnter * silent !echo -ne "\e[2 q"
augroup END

"sudo"
cnoremap w!! execute 'silent! write !sudo tee % >/dev/null' <bar> edit!

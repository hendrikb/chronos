if !has('python')
    echo "Error: Chronos needs vim compiled with python support."
    finish
endif

pyfile chronos.py

function! StartTimer()
    py chronos.startTimer()
endfunction

function! StopTimer()
    py chronos.stopTimer()
endfunction

function! PrintStats()
    py chronos.showStats()
endfunction

augroup Chronos
    autocmd!
    autocmd Chronos BufEnter,FocusGained * silent! call StartTimer()
    autocmd Chronos BufLeave,FocusLost * silent! call StopTimer()
augroup END

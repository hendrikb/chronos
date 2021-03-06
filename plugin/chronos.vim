if !has('python')
    echo "Error: Chronos needs vim compiled with python support."
    finish
endif

execute 'pyfile ' . expand('<sfile>:p:h') . '/../chronos.py'

function! StartTimer()
    py chronos.startTimer()
endfunction

function! StopTimer()
    py chronos.stopTimer()
endfunction

function! ShowStats()
    py chronos.showStats()
endfunction

function! ClearStats()
    py chronos.clearStats()
endfunction

function! AddSaved()
    py chronos.addSaved()
endfunction

augroup Chronos
    autocmd!
    autocmd Chronos BufEnter,FocusGained * call StartTimer()
    autocmd Chronos BufLeave,FocusLost * call StopTimer()
augroup END

command! ChronosShowStats call ShowStats()
command! ChronosClearStats call ClearStats()
command! ChronosAddAnyway call AddSaved()

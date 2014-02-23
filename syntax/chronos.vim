if exists("b:current_syntax")
    finish
endif


let b:current_syntax = "chronos"

syntax match ChronosHeader   /^[A-Z].*$/
syntax match ChronosExt      /^  [^ ]*$/
syntax match ChronosTime     /^    [0-9].*$/
" syntax match   Chronos
highlight ChronosHeader   gui=bold guifg=cyan
highlight link ChronosExt Keyword

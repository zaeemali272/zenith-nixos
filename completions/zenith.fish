# Fish completions for zenith

# Global
complete -c zenith -s v -l version -d "Print current version"
complete -c zenith -s h -l help -d "Print help"

# Subcommands
complete -c zenith -n "__fish_use_subcommand" -a shell -d "Manage desktop shell"
complete -c zenith -n "__fish_use_subcommand" -a toggle -d "Toggle a special workspace"
complete -c zenith -n "__fish_use_subcommand" -a screenshot -d "Take a screenshot"
complete -c zenith -n "__fish_use_subcommand" -a record -d "Screen recording"
complete -c zenith -n "__fish_use_subcommand" -a clipboard -d "Clipboard history"
complete -c zenith -n "__fish_use_subcommand" -a emoji -d "Emoji and glyph picker"
complete -c zenith -n "__fish_use_subcommand" -a wallpaper -d "Wallpaper manager"
complete -c zenith -n "__fish_use_subcommand" -a scheme -d "Color scheme manager"
complete -c zenith -n "__fish_use_subcommand" -a resizer -d "Window resizer"
complete -c zenith -n "__fish_use_subcommand" -a rebuild -d "Rebuild system"
complete -c zenith -n "__fish_use_subcommand" -a update -d "Update and rebuild"
complete -c zenith -n "__fish_use_subcommand" -a rollback -d "Rollback generation"
complete -c zenith -n "__fish_use_subcommand" -a gc -d "Garbage collect"
complete -c zenith -n "__fish_use_subcommand" -a clean -d "Deep disk clean"
complete -c zenith -n "__fish_use_subcommand" -a doctor -d "System health check"
complete -c zenith -n "__fish_use_subcommand" -a where -d "Print config location"

# shell subcommands
complete -c zenith -n "__fish_seen_subcommand_from shell" -a "start restart switch list kill show log"
complete -c zenith -n "__fish_seen_subcommand_from shell; and __fish_prev_arg_in switch use" -a "zenith caelestia end-4"

# toggle subcommands
complete -c zenith -n "__fish_seen_subcommand_from toggle" -a "sysmon communication music todo"

# screenshot flags
complete -c zenith -n "__fish_seen_subcommand_from screenshot" -s r -l region -d "Select region"
complete -c zenith -n "__fish_seen_subcommand_from screenshot" -s f -l freeze -d "Freeze screen"

# record flags
complete -c zenith -n "__fish_seen_subcommand_from record" -s r -l region -d "Record region"
complete -c zenith -n "__fish_seen_subcommand_from record" -s s -l sound -d "Record sound"
complete -c zenith -n "__fish_seen_subcommand_from record" -s p -l pause -d "Pause recording"

# wallpaper flags
complete -c zenith -n "__fish_seen_subcommand_from wallpaper" -s f -l file -d "Wallpaper file"
complete -c zenith -n "__fish_seen_subcommand_from wallpaper" -s r -l random -d "Random wallpaper"
complete -c zenith -n "__fish_seen_subcommand_from wallpaper" -s p -l print -d "Print current wallpaper"

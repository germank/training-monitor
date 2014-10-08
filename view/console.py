import cmd
import logging
from signalslot import Signal


class CommandConsole(cmd.Cmd):
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.save_command = Signal(['output_dir'])
        self.quit_command = Signal()
        
    def do_save(self, line):
        self.save_command.emit(output_dir=line)
        
    def do_EOF(self, line):
        return self.do_quit(line)

    def do_quit(self, line):
        self.quit_command.emit()
        return True
        

import os

import datetime

class logtxt():
    def __init__(self, folder, code) -> None:
        self.folder = folder
        self.code = code
        self.log_path = os.path.join(folder, '{}_log.txt'.format(code))
        self.file = self.log_path
        if not os.path.exists(self.log_path):
            self.createFile()
    def __repr__(self) -> str:
        return 'log file object for {} in {}'.format(self.code, self.folder)
    
    
    def _timestring(self, string, printing = True):
        if printing:
            print('{}\t\t{}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), string))
        return '{}\t\t{}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), string)

    def createFile(self):
        with open(self.log_path, 'w+') as f:
            f.write(self._timestring('Log file created ({})'.format(self.log_path)))
            f.close()
    
    def add(self, string, printing = True):
        with open(self.log_path, 'a+') as f:
            f.write(self._timestring(string,printing = printing))
            f.close()
        
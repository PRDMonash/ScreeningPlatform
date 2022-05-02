import os

class SoftwareDetails():
    def __init__(self, folder) -> None:
        if not os.path.exists(folder):
            raise FileNotFoundError('Software Details folder {} not found...'.format(folder))

        print('{} found... IN PROGRESS.'.format(folder))
        pass

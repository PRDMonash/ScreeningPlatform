import pandas as pd
from pandas.io.parsers import read_csv

class solution_csv():
    def __init__(self, csv) -> None:
        self.__file = csv
    
    def __repr__(self) -> str:
        return 'Solution csv object: {}'.format(self.getFile())
        
    def getFile(self):
        return self.__file
    
    def getDF(self):
        return pd.read_csv(self.getFile())
    
    def _getListChemicals(self):
        df = self.getDF()
        return list(df['class'])

    def _getColumns(self):
        return list(self.getDF().columns)

    def getChemical(self, type = 'monomer'):
        if not type in self._getListChemicals():
            print('{} not in solution. Choose: {}'.format(type, self._getListChemicals()))
            return None
        
        df = self.getDF()

        return df.loc[df['class']==type]
        
    def getChemicalInfo(self, type = 'monomer', info = 'eq'):
        chemical = self.getChemical(type = type)

        if not info in self._getColumns():
            print('{} not in columns. Choose: {}'.format(info, self._getColumns()))
            return None

        chemInfo = chemical[info].values[0] # values, will give the series object otherwise

        if info in ['name', 'abbreviation']:
            return str(chemInfo)
        
        else:
            return float(chemInfo)

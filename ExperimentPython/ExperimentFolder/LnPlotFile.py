
import numpy as np


class LnPlotFile():
    
    def __init__(self, file) -> None:
        self.file = file

        print(self.file)
    
    def getContent(self):
        with open(self.file, '+r') as f:
            content = f.readlines()
            f.close()
        return content
    
    def getMovingAverageFit(self, start_with = 'Moving Averge fit values: '):
        content = self.getContent()
        for line in content:
            if line.startswith(start_with):
                values = line.split(start_with)[-1].split('\n')[0].strip('[').strip(']')
                values = [float(i) for i in values.split(' ')]
                return values

    def getMovingAverageFitData(self):
        ''''
        Returns:
        --------
        x: list
            tres list
        y: list
            ln list
        '''
        x, y = [],[]

        searchquery3 = '{}'.format('MovingAverageFitSTART')
        searchquery4 = '{}'.format('MovingAverageFitSTOP')
        content = self.getContent()
        
        index_start_summary = np.array([x.startswith(searchquery3) for x in np.array(content)], dtype=bool)
        index_stop_summary = np.array([x.startswith(searchquery4) for x in np.array(content)], dtype=bool)
                
        lines4 =(content[(np.array(range(len(content)))[index_start_summary][0]+1):np.array(range(len(content)))[index_stop_summary][0]])
        lines5 =[ x.replace('\t\n', '\n').replace('\t ', ',').strip() for x in lines4]
        
        for line in lines5[:-1]:
            x.append(float(line.split(',')[0]))
            y.append(float((line.split(',')[1]).strip()))
        return x, y

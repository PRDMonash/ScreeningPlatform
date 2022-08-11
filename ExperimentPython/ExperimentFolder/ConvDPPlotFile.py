import numpy as np

class ConvDPplotFile():

    def __init__(self, file) -> None:
        self.file = file

        print(self.file)
    
    def getContent(self):
        with open(self.file, '+r') as f:
            content = f.readlines()
            f.close()
        return content
    
    def getData(self, searchquery):
        '''
        searchquery: "AllData", "CorrectedData", ZeroInterceptFit", "Fit"

        Returns:
        ---------
        x: list
            list of conversions
        y: list
            list of DP values
        
        '''
        x, y = [],[]

        searchquery3 = '{}START'.format(searchquery)
        searchquery4 = '{}STOP'.format(searchquery)
        content = self.getContent()
        
        index_start_summary = np.array([x.startswith(searchquery3) for x in np.array(content)], dtype=bool)
        index_stop_summary = np.array([x.startswith(searchquery4) for x in np.array(content)], dtype=bool)
                
        lines4 =(content[(np.array(range(len(content)))[index_start_summary][0]+1):np.array(range(len(content)))[index_stop_summary][0]])
        lines5 =[ x.replace('\t\n', '\n').replace('\t ', ',').strip() for x in lines4]
        
        for line in lines5[:-1]:
            x.append(float(line.split(',')[0]))
            y.append(float((line.split(',')[1]).strip()))
        return x, y
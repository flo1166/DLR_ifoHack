# import libraries
import pandas as pd
import os
import glob
import geopandas as gpd

# dictionary with file locations
csv_files = {'Land': 'PATH/1 Land Prices', 
             'Zensus': 'PATH/2 Zensus',
            }

def csv_binder(path: str, key: str):
    '''
    This functions binds togheter CSV files

    Variables:
    path : str is the location were files are saved
    
    Returns: combined data
    '''
    os.chdir(path)
    csv = pd.DataFrame()
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    csv_files = [word for word in csv_files if key in word]
    
    for f in csv_files:
        csv = pd.concat([csv, pd.read_csv(f, sep=';', index_col=0)])

    return csv

def merge_tables(table_list: list, key: str):
    '''
    This functions merges a list of tables via outer join
    
    Variables:
    table_list: list of tables to join
    key: the key to join on

    Return: merged table
    '''
    new = []
    for k in table_list:
        k[key] = k[key].astype(str)
        new.append(k)

    new2 = new[0]
    
    for i in range(len(new[1:])):
        new2 = new2.merge(new[i+1], on = key, how = 'inner')

    return new2

# CSV reading
buildings = csv_binder(csv_files['Zensus'], 'Buildings')
families = csv_binder(csv_files['Zensus'], 'Families')
households = csv_binder(csv_files['Zensus'], 'Households')
population = csv_binder(csv_files['Zensus'], 'Population')

# CSV merge
dataframe_grid = [buildings, families, households, population]
df_census = merge_tables(dataframe_grid, 'Grid_Code')





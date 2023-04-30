# import libraries
import pandas as pd
import geopandas as gpd
import random 
import os
import glob
import geopandas as gpd

# dictionary with file locations
csv_files = {'Land': 'PATH', 
             'Zensus': 'PATH',
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
#land = csv_binder(csv_files['Land'], 'Land_Prices')
buildings = csv_binder(csv_files['Zensus'], 'Buildings')
families = csv_binder(csv_files['Zensus'], 'Families')
households = csv_binder(csv_files['Zensus'], 'Households')
population = csv_binder(csv_files['Zensus'], 'Population')

# CSV merge
dataframe_grid = [buildings, families, households, population]
census = merge_tables(dataframe_grid, 'Grid_Code')

# load of grid and neighborhood data
neigh_ber = gpd.read_file('PATH/1 Land Prices/Land_Prices_Neighborhood_Berlin.gpkg')
neigh_bre = gpd.read_file("PATH1 Land Prices/Land_Prices_Neighborhood_Bremen.gpkg")
neigh_dre = gpd.read_file("PATH/1 Land Prices/Land_Prices_Neighborhood_Dresden.gpkg")
neigh_fra = gpd.read_file("PATH/1 Land Prices/Land_Prices_Neighborhood_Frankfurt_am_Main.gpkg")
neigh_koe = gpd.read_file("PATH/1 Land Prices/Land_Prices_Neighborhood_Köln.gpkg")
grid_ber = gpd.read_file('PATH/2 Zensus/Zensus_Berlin_Grid_100m.gpkg')
grid_bre = gpd.read_file('PATH/2 Zensus/Zensus_Bremen_Grid_100m.gpkg')
grid_dre = gpd.read_file('PATH/2 Zensus/Zensus_Dresden_Grid_100m.gpkg')
grid_fra = gpd.read_file('PATH/2 Zensus/Zensus_Frankfurt_am_Main_Grid_100m.gpkg')
grid_koe = gpd.read_file('PATH/2 Zensus/Zensus_Köln_Grid_100m.gpkg')

neighbor = [neigh_ber, neigh_bre, neigh_dre, neigh_fra, neigh_koe]
grids = [grid_ber, grid_bre, grid_dre, grid_fra, grid_koe]

def centroid_poly(df: list):
    '''
    This funciton calculates the centroid of a column in a dataframe
    
    Variables:
    df: dataframe to work with
    
    Returns:
    Dataframe with centroids in the centroid column
    '''
    for i in range(len(df)):
        df[i]['centroid'] = df[i]['geometry'].centroid
        if i == 0:
            df[i]['City'] = 'Berlin'
        elif i == 1:
            df[i]['City'] = 'Bremen'
        elif i == 2:
            df[i]['City'] = 'Dresden'
        elif i == 3:
            df[i]['City'] = 'Frankfurt'
        elif i == 4: 
            df[i]['City'] = 'Köln'
    return df

grids_centroid = centroid_poly(grids)

# matching of neighborhoods with grids
list_neigh = []
list_val = []
rand_val = random.randint(0, len(neighbor) - 1)
for i in range(len(neighbor)):
    for j in range(len(grids_centroid[i])):
        bool_neigh = neighbor[i]['geometry'].overlaps(grids_centroid[i]['geometry'][j])
        if sum(bool_neigh) == 0:
            if list_neigh == []:
                list_neigh.append(neighbor[i]['Neighborhood_FID'][rand_val])
                list_val.append(int(neighbor[i]['Land_Value'][rand_val].mean()))
            else:
                list_neigh.append(list_neigh[-1])
                list_val.append(list_val[-1])
        else:
            list_neigh.append(neighbor[i]['Neighborhood_FID'][bool_neigh])
            list_val.append(int(neighbor[i]['Land_Value'][bool_neigh].mean()))

    grids_centroid[i]['neighbor'] = list_neigh
    grids_centroid[i]['land_value'] = list_val

    list_neigh = []
    list_val = []

# build df with grid centroid values
feature_enginereed_df = census[['Grid_Code', 'buildings_total_units', 'population_total_units', 'families_total_units']]

feature_enginereed_final = []
for i in range(len(grids_centroid)):
    feature_enginereed_final.append(grids_centroid[i].merge(feature_enginereed_df, on = 'Grid_Code', how = 'left'))

feature_enginereed = pd.DataFrame()
for k in range(len(feature_enginereed_final)):
    feature_enginereed = pd.concat([feature_enginereed, feature_enginereed_final[k]])
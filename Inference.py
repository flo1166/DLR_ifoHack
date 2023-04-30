from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
import statsmodels.regression.linear_model as sm
from mlxtend.feature_selection import SequentialFeatureSelector as SFS

def recode_cat(feature_series):
	'''
	This functions recodes true and false values from dummy generation to numbers
	
	Variables:
	feature_series: a pd.Series to iterate over

	Return: pd.Series with recoded values
	'''
	return feature_series.apply(lambda x: 1 if x == True else 0)

def model_fit(X_train, y_train):
	'This is the judges function'
	regr = LinearRegression()
	regr.fit(X_train, y_train)
	return regr

def model_predict(regr, X_test):
	'This is the judges function'
	y_pred = regr.predict(X_test)
	return y_pred

# Data load
feature_enginereed = pd.read_csv('PATH', sep=';')
feature_enginereed = feature_enginereed.dropna()

# recode categorial
feature_enginereed = pd.get_dummies(feature_enginereed, columns = ['City'])
feature_enginereed['City_Berlin'] = recode_cat(feature_enginereed['City_Berlin'])
feature_enginereed['City_Dresden'] = recode_cat(feature_enginereed['City_Dresden'])
feature_enginereed['City_Frankfurt'] = recode_cat(feature_enginereed['City_Frankfurt'])
feature_enginereed['City_Köln'] = recode_cat(feature_enginereed['City_Köln'])
feature_enginereed['City_Bremen'] = recode_cat(feature_enginereed['City_Bremen'])

# dependendt and independent variable
x = feature_enginereed.iloc[:, 7:]
x = np.append(arr = np.ones((len(feature_enginereed), 1)).astype(int), values = x, axis = 1)
y = feature_enginereed['land_value']

x_opt = x

# Split Train and Test
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# backward feature search and fitting of model
regression_model_backward = SFS(LinearRegression(),
          forward = False,
	  	  floating = False,
		  verbose = 2,
          scoring='r2',
          cv=10,
          n_jobs=-1)
regression_model_backward = regression_model_backward.fit(X_train, y_train)

# evaluate model and select features
scores_backward = pd.DataFrame.from_dict(regression_model_backward.get_metric_dict()).T
print('Best option: ' , scores_backward.sort_values('avg_score', ascending = False).iloc[0, :])

# get columns of selected features
features_selected = list(scores_backward.sort_values('avg_score', ascending = False).iloc[0, :]['feature_names'])

for i in range(len(features_selected)):
	features_selected[i] = int(features_selected[i]) + 6

x_neu = feature_enginereed.iloc[:, features_selected]
x_neu = np.append(arr = np.ones((len(feature_enginereed), 1)).astype(int), values = x, axis = 1)
X_train_fin, X_test_fin, y_train_fin, y_test_fin = train_test_split(x_neu, y, test_size=0.3, random_state=42)

# Fit the estimator using the new feature subset
# and make a prediction on the test data
final_model = sm.OLS(y, x_neu).fit()
predictions_from_model = model_predict(final_model, X_test_fin)
print(final_model.summary())

# evaluieren
r2 = r2_score(y_test_fin, predictions_from_model)
print('R^2 is:', r2)



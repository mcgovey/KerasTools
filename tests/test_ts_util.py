from .context import KerasTools

import pandas as pd
import numpy as np
from math import floor, ceil
import pytest
from tensorflow.keras import models, layers, callbacks, Input # keras for model building

from sklearn.preprocessing import MinMaxScaler, StandardScaler # scalers for passed scalers

class TestRNN:
	def setup(self):
		self.sales_df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv').iloc[:100,:]
		# self.df = pd.read_csv('https://github.com/nytimes/covid-19-data/raw/master/us-states.csv', nrows=1000) #use for multiple features, will need to be pivoted
		
		self.helper = ""
		self.y_steps = 5
	
	
	@pytest.mark.parametrize("feature_list", [[1, 2], ['cases', 'deaths']])
	@pytest.mark.parametrize("y_steps", [1, 3, 5])
	
	def test_ts_setup_types(self, feature_list, y_steps):
		self.helper = KerasTools.keras_tools(self.sales_df,
                                    features = feature_list, 
                                    index = 0,  ts_n_y_vals = y_steps, debug=False)
		# different features
		# different y vals
		# different indices
		# different feature columns
		pass
	
	# @pytest.mark.parametrize("split_type", ['sequential', 'sample', 'overlap'])
	def test_split(self):
		"""Test different split types"""
		
		
		self.helper = KerasTools.keras_tools(self.sales_df,
                                    features = [1,2], 
                                    index = 0,  ts_n_y_vals = self.y_steps, debug=False)
		self.helper.train_test_split(split_type='sequential')
		
		
		assert self.helper.ts_n_y_vals == self.y_steps

	# @pytest.mark.scale
	def test_scale_str(self):
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = [1,2], 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		# created scaler passed minmax
		
		step = 1
		sample_size = 1
		
		# name of scaler passed
		self.scale_helper.train_test_split(split_type='sample')
		
		return_val = self.scale_helper.reshape_ts(step = step,
					sample_size = sample_size,
					scaler = "standard",
					output_scaler=True)
		
		assert return_val is not None
		# return scaler is true
		
	def test_scale_passed(self):
		# TODO: add scaler handling
		
		# self.scale_helper = KerasTools.keras_tools(self.sales_df, 
  #                                  features = [1,2], 
  #                                  index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		# # created scaler passed minmax
		
		# step = 1
		# sample_size = 1
		
		# # name of scaler passed
		# self.scale_helper.train_test_split(split_type='sample')
		
		# return_val = self.scale_helper.reshape_ts(step = step,
		# 			sample_size = sample_size,
		# 			scaler = "standard",
		# 			output_scaler=True)
		
		# assert return_val is not None
		pass
	
	def test_scale_not_defined(self):
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = [1,2], 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		step = 1
		sample_size = 1
		
		# name of scaler passed
		self.scale_helper.train_test_split(split_type='sample')
		# self.scale_helper.scale(scaler = "minmax")
		
		with pytest.raises(AttributeError) as excinfo:
			self.scale_helper.reshape_ts(step = step,
					sample_size = sample_size,
					scaler = "standad")  #misspelled scaler passed
					
		assert "Invalid Scaler Type Passed" in str(excinfo.value)
		
	def test_seq_split(self):
		"""
		Tests time-series function for creating distinct time-series splits in the data.
		"""
		feature_list = [1,2]
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = feature_list, 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='sequential',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		assert self.scale_helper.train_df.shape == (len(feature_list), (1 - split_pct - val_split_pct) * self.sales_df.shape[0])
		assert self.scale_helper.test_df.shape == (len(feature_list), split_pct * self.sales_df.shape[0])
		assert self.scale_helper.valid_df.shape == (len(feature_list), val_split_pct * self.sales_df.shape[0])
		
		
	def test_sample_split(self):
		"""
		Tests time-series function for sampling features.
		"""
		feature_list = [1,2]
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = feature_list, 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='sample',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
										
		assert self.scale_helper.train_df.shape == (np.round((1 - split_pct - val_split_pct) * len(feature_list)), self.sales_df.shape[0])
		assert self.scale_helper.test_df.shape == (np.round(split_pct * len(feature_list)), self.sales_df.shape[0])
		assert self.scale_helper.valid_df.shape == (np.round(val_split_pct * len(feature_list)), self.sales_df.shape[0])
		
		
	def test_overlap_split(self):
		"""
		Tests time-series function for overlapping time-series chunks.
		"""
		feature_list = [1,2]
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = feature_list, 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		assert self.scale_helper.train_df.shape == (len(feature_list), floor((1 - split_pct - val_split_pct) * (self.sales_df.shape[0] - self.y_steps) + self.y_steps))
		assert self.scale_helper.test_df.shape == (len(feature_list), floor(split_pct * (self.sales_df.shape[0] - self.y_steps) + self.y_steps))
		assert self.scale_helper.valid_df.shape == (len(feature_list), ceil(val_split_pct * (self.sales_df.shape[0] - self.y_steps) + self.y_steps)) #this is rounded up because if there are remaining values they fall in this bucket
		
	
	
	@pytest.mark.parametrize("step", [1, 3, 5])
	@pytest.mark.parametrize("sample_size", [1, 5, 10])
	
	def test_reshape_ts(self, step, sample_size):
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = [1,2], 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		# step = 1
		# sample_size = 1
		
		self.scale_helper.reshape_ts(step = step,
										sample_size = sample_size)
										
		train_len = len(range(0,self.scale_helper.train_df.shape[1] - self.y_steps - sample_size + 1,step))
		test_len = len(range(0,self.scale_helper.test_df.shape[1] - self.y_steps - sample_size + 1,step))
		valid_len = len(range(0,self.scale_helper.valid_df.shape[1] - self.y_steps - sample_size + 1,step))
		
		assert self.scale_helper.X_train.shape == (train_len, sample_size, self.scale_helper.train_df.shape[0])
		assert self.scale_helper.y_train.shape == (train_len, self.scale_helper.train_df.shape[0], self.y_steps)
		
		assert self.scale_helper.X_test.shape == (test_len, sample_size, self.scale_helper.test_df.shape[0])
		assert self.scale_helper.y_test.shape == (test_len, self.scale_helper.test_df.shape[0], self.y_steps)
		
		assert self.scale_helper.X_valid.shape == (valid_len, sample_size, self.scale_helper.valid_df.shape[0])
		assert self.scale_helper.y_valid.shape == (valid_len, self.scale_helper.valid_df.shape[0], self.y_steps)
		

	def test_get_input_shape(self):
		"""
		Tests that input_shape matches expected shape from X_train
		"""
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = [1,2], 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		step = 1
		sample_size = 1
		
		self.scale_helper.reshape_ts(step = step,
										sample_size = sample_size)
										
		input_shape = self.scale_helper.get_input_shape()
		
		np.testing.assert_array_equal(self.scale_helper.X_train.shape[1:3], input_shape)
		
	
	# @pytest.mark.focus
	def test_model_summary(self, capsys):
		""" create and train a NN to get model and history objects for testing model_summary method
		"""
		feature_list = [1,2]
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = feature_list, 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		
		split_pct = 0.3
		val_split_pct = 0.1
		
		self.scale_helper.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		step = 1
		sample_size = 1
		
		self.scale_helper.reshape_ts(step = step,
										sample_size = sample_size)
										
		# create model
		model, history = self.create_model(feature_list)
		
		self.scale_helper.model_summary(model, history, show_charts=True)
		
		captured = capsys.readouterr()
		
		print(captured.out)
		
		assert 'Model: ' in captured.out
		
		
	def create_model(self, feature_list):
		"""Create a keras model to be used in tests"""
		
		input_shape = self.scale_helper.get_input_shape()

		timeseries_input = Input(shape=input_shape, dtype='float32', name='timeseries')
		
		ts_layer = layers.LSTM(units=16, 
								activation='relu')(timeseries_input)
		
		                       
		output = layers.Dense(len(feature_list) * self.y_steps, activation=None)(ts_layer)
		output = layers.Reshape((len(feature_list), self.y_steps))(output)
		
		model = models.Model(timeseries_input, output)
		model.compile(optimizer='adam',
						loss='mse',
						metrics=['mse', 'mae', 'mape'])
		             
		history = model.fit(self.scale_helper.X_train, 
							self.scale_helper.y_train,
							validation_data = (self.scale_helper.X_test, self.scale_helper.y_test),
							steps_per_epoch=5,
							validation_steps = 5,
							epochs=10,
							verbose=0)
		
		return model, history
		
	def test_ts_transform(self):
		"""Compare output of the transform method with the same output of individual components"""
		# standardize the inputs
		split_pct = 0.3
		val_split_pct = 0.1
		step = 1
		sample_size = 1
		feature_list = [1,2]
		
		
		# create instance of standard two step process
		self.scale_helper = KerasTools.keras_tools(self.sales_df, 
                                    features = feature_list, 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		
		
		self.scale_helper.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		
		self.scale_helper.reshape_ts(step = step,
										sample_size = sample_size)
										
		# create instance of ts_transform method
		self.scale_helper2 = KerasTools.keras_tools(self.sales_df, 
                                    features = [1,2], 
                                    index = 0, ts_n_y_vals = self.y_steps, debug=False)
		
		
		self.scale_helper2.ts_transform(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct,
										step = step,
										sample_size = sample_size)
		
		# test array shape
		assert self.scale_helper.X_train.shape == self.scale_helper2.X_train.shape
		assert self.scale_helper.y_train.shape == self.scale_helper2.y_train.shape
		
		assert self.scale_helper.X_test.shape == self.scale_helper2.X_test.shape
		assert self.scale_helper.y_test.shape == self.scale_helper2.y_test.shape
		
		assert self.scale_helper.X_valid.shape == self.scale_helper2.X_valid.shape
		assert self.scale_helper.y_valid.shape == self.scale_helper2.y_valid.shape
		
		# assert array equality
		np.testing.assert_array_equal(self.scale_helper.X_train, self.scale_helper2.X_train)
		np.testing.assert_array_equal(self.scale_helper.y_train, self.scale_helper2.y_train)
		
		np.testing.assert_array_equal(self.scale_helper.X_test, self.scale_helper2.X_test)
		np.testing.assert_array_equal(self.scale_helper.y_test, self.scale_helper2.y_test)
		
		np.testing.assert_array_equal(self.scale_helper.X_valid, self.scale_helper2.X_valid)
		np.testing.assert_array_equal(self.scale_helper.y_valid, self.scale_helper2.y_valid)
		
### Tests
## train_test_split
# split_pct less than 0
# split_pct greater than 1
# val_split_pct less than 0
# val_split_pct greater than 1

## reshape_ts
# input_data added as parameter - train/test
# input_data added as parameter - train/test/valid

## initialization
# ts_n_y_vals
# y_val as string
# y_val as df
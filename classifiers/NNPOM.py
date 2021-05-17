# encoding: utf-8
import numpy as np
import math as math
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from lbfgs import fmin_lbfgs

class NNPOM(BaseEstimator, ClassifierMixin):
	
	"""

	NNPOM Neural Network based on Proportional Odd Model (NNPOM). This
		class implements a neural network model for ordinal regression. The
		model has one hidden layer with hiddenN neurons and one outputlayer
		with only one neuron but as many threshold as the number of classes
		minus one. The standard POM model is applied in this neuron to have
		probabilistic outputs. The learning is based on iRProp+ algorithm and
		the implementation provided by Roberto Calandra in his toolbox Rprop
		Toolbox for {MATLAB}:
		http://www.ias.informatik.tu-darmstadt.de/Research/RpropToolbox
		The model is adjusted by minimizing cross entropy. A regularization
		parameter "lambda" is included based on L2, and the number of
		iterations is specified by the "iterations" parameter.

		NNPOM public methods:
			fit						- Fits a model from training data
			predict					- Performs label prediction
	
		References:
			[1] P. McCullagh, Regression models for ordinal data,  Journal of
				the Royal Statistical Society. Series B (Methodological), vol. 42,
				no. 2, pp. 109–142, 1980.
			[2] M. J. Mathieson, Ordinal models for neural networks, in Proc.
				3rd Int. Conf. Neural Netw. Capital Markets, 1996, pp.
				523-536.
			[3] P.A. Gutiérrez, M. Pérez-Ortiz, J. Sánchez-Monedero,
				F. Fernández-Navarro and C. Hervás-Martínez
				Ordinal regression methods: survey and experimental study
				IEEE Transactions on Knowledge and Data Engineering, Vol. 28.
				Issue 1, 2016
				http://dx.doi.org/10.1109/TKDE.2015.2457911

		This file is part of ORCA: https://github.com/ayrna/orca
		Original authors: Pedro Antonio Gutiérrez, María Pérez Ortiz, Javier Sánchez Monedero
		Citation: If you use this code, please cite the associated paper http://www.uco.es/grupos/ayrna/orreview
		Copyright:
			This software is released under the The GNU General Public License v3.0 licence
			available at http://www.gnu.org/licenses/gpl-3.0.html


		NNPOM properties:
			epsilonInit					- Range for initializing the weights.
			hiddenN						- Number of hidden neurons of the
										model.
			iter						- Number of iterations for iRProp+
										algorithm.
			lambda						- Regularization parameter.
			theta1						- Hidden layer weigths (with bias)
			theta2						- Output layer weigths (without bias, the biases will be the thresholds)
			thresholds					- Class thresholds parameters
			num_labels					- Number of labels in the problem
			m							- Number of samples of X (train patterns array).
		
	"""

	# Constructor of class NNPOM (set parameters values).
	def __init__(self, epsilonInit=0.5, hiddenN=50, iterations=500, lambdaValue=0.01):
		
		self.__epsilonInit = epsilonInit
		self.__hiddenN = hiddenN
		self.__iter = iterations
		self.__lambdaValue = lambdaValue


	#--------Main functions (Public Access)--------


	def fit(self,X,y):

		"""

		Trains the model for the model NNPOM method with TRAIN data.
		Returns the projection of patterns (only valid for threshold models) and the predicted labels.
		
		Parameters
		----------

		X: {array-like, sparse matrix}, shape (n_samples, n_features)
			Training patterns array, where n_samples is the number of samples
			and n_features is the number of features

		y: array-like, shape (n_samples)
			Target vector relative to X

		Returns
		-------

		projectedTrain: {array-like, sparse matrix}, shape (n_samples,)
			Vector array with projected values for each pattern of train patterns.

		predictedTrain: {array-like, sparse matrix}, shape (n_samples,)
			Vector array with predicted values for each pattern of train patterns.

		"""

		# Aux variables
		y = y[:,np.newaxis]
		input_layer_size = X.shape[1]
		num_labels = np.size(np.unique(y))
		m = X.shape[0]
		
		
		# Recode y to Y using nominal coding
		Y = 1 * (np.tile(y, (1,num_labels)) == np.tile(np.arange(1,num_labels+1)[np.newaxis,:], (m,1)))
		# TODO: esta línea devuelve Y=0
		# He probado esta línea y no da cero da la matriz correctamente
		
		# Hidden layer weigths (with bias)
		initial_Theta1 = self.__randInitializeWeights(input_layer_size+1, self.getHiddenN())
		# Output layer weigths (without bias, the biases will be the thresholds)
		initial_Theta2 = self.__randInitializeWeights(self.getHiddenN(), 1)
		# Class thresholds parameters
		initial_thresholds = self.__randInitializeWeights((num_labels-1),1)
		
		# Pack parameters
		initial_nn_params = np.concatenate((initial_Theta1.flatten(order='F'),
		 initial_Theta2.flatten(order='F'), initial_thresholds.flatten(order='F')),
		 axis=0)[:,np.newaxis]
		
		# ---- ARGUMENTOS PENDIENTES DE PRUEBA ----
		nn_params = fmin_lbfgs(f=self.__nnPOMCostFunction, x0=initial_nn_params,args=(input_layer_size, self.__hiddenN,
		 num_labels, X, Y, self.__lambdaValue), max_iterations=self.__iter, line_search='default')
		

		"""
		#Create "short hand" for the cost function to be minimized
		[J,grad] = obj.nnPOMCostFunction(initial_nn_params, ...
				input_layer_size, ...
				hidden_layer_size, ...
				num_labels, X, Y, lambda);
			
		#RProp options
		p.verbosity = 0;					#Increase indent
		p.MaxIter   = parameters.iter;		#Maximum number of iterations
		p.d_Obj     = -1;					#Objective cost
		p.method    = 'IRprop+';			#Use IRprop- algorithm
		p.display   = 0;

		#Running RProp
		[nn_params,cost,exitflag,stats1] = rprop(grad,initial_nn_params,p);

		#options = optimoptions('fminunc','Algorithm','quasi-newton','SpecifyObjectiveGradient',true,'Diagnostics','on','Display','iter-detailed','UseParallel',true,'MaxIter', 1000,'CheckGradients',true);
		#[nn_params, cost, exitflag, output] = fminunc(costFunction, initial_nn_params, options);

		"""
		# Unpack the parameters
		Theta1, Theta2, thresholds_param = self.__unpackParameters(nn_params, input_layer_size,
		 self.getHiddenN(), num_labels)
		self.__theta1 = Theta1
		self.__theta2 = Theta2
		self.__thresholds = self.__convertThresholds(thresholds_param, num_labels)
		self.__num_labels = num_labels
		self.__m = m
		
		projectedTrain, predictedTrain = self.predict(X)
		
		return projectedTrain, predictedTrain
	
	
	def predict (self, test):
		
		"""

		Predicts labels of TEST patterns labels. The object needs to be fitted to the data first.
				
		Parameters
		----------

		test: {array-like, sparse matrix}, shape (n_samples, n_features)
			test patterns array, where n_samples is the number of samples
			and n_features is the number of features

		Returns
		-------

		projected: {array-like, sparse matrix}, shape (n_samples,)
			Vector array with projected values for each pattern of test patterns.

		predicted: {array-like, sparse matrix}, shape (n_samples,)
			Vector array with predicted values for each pattern of test patterns.

		"""

		m = test.shape(0)

		a1 = np.append(np.ones((m, 1)), test, axis=1)
		z2 = np.matmul(a1,self.__theta1.T)
		a2 =  1.0 / (1.0 + np.exp(-z2))
		projected= np.matmul(a2,self.__theta2.T)

		z3 = np.tile(self.__thresholds, (m,1)) - np.tile(projected, (1, self.__num_labels-1))
		a3T =  1.0 / (1.0 + np.exp(-z3))
		a3 = np.append(a3T, np.ones((m,1)), axis=1)
		a3[:,1:] = a3[:,1:] - a3[:,0:-1]
		M,predicted = a3.max(axis=1)[:,np.newaxis],a3.argmax(0)[:,np.newaxis]

		return projected,predicted
	
	
	#--------Getters & Setters (Public Access)--------
	

	# Getter & Setter of "epsilonInit"
	def getEpsilonInit (self):
		
		"""

		This method returns the value of the variable self.__epsilonInit.
		self.__epsilonInit contains the value of epsilon, which is the initialization range of the weights.

		"""

		return self.__epsilonInit

	def setEpsilonInit (self, epsilonInit):
	   
		"""

		This method modify the value of the variable self.__epsilonInit.
		This is replaced by the value contained in the epsilonInit variable passed as an argument.

		"""

		self.__epsilonInit = epsilonInit
	

	# Getter & Setter of "hiddenN"
	def getHiddenN (self):
	   
		"""

		This method returns the value of the variable self.__hiddenN.
		self.__hiddenN contains the number of nodes/neurons in the hidden layer.

		"""

		return self.__hiddenN

	def setHiddenN (self, hiddenN):
	  
		"""

		This method modify the value of the variable self.__hiddenN.
		This is replaced by the value contained in the hiddenN variable passed as an argument.

		"""

		self.__hiddenN = hiddenN
	

	# Getter & Setter of "iter"
	def getIter (self):
		
		"""

		This method returns the value of the variable self.__iter.
		self.__iter contains the number of iterations.

		"""

		return self.__iter
	
	def setIter (self, iterations):
	  
		"""

		This method modify the value of the variable self.__iter.
		This is replaced by the value contained in the iterations variable passed as an argument.

		"""

		self.__iter = iterations
	

	# Getter & Setter of "lambdaValue"
	def getLambdaValue (self):
	   
		"""

		This method returns the value of the variable self.__lambdaValue.
		self.__lambdaValue contains the Lambda parameter used in regularization.

		"""

		return self.__lambdaValue
	
	def setLambdaValue (self, lambdaValue):
	  
		"""

		This method modify the value of the variable self.__lambdaValue.
		This is replaced by the value contained in the lambdaValue variable passed as an argument.

		"""

		self.__lambdaValue = lambdaValue


	# Getter & Setter of "theta1"
	def getTheta1 (self):
		
		"""

		This method returns the value of the variable self.__theta1.
		self.__theta1 contains an array with the weights of the hidden layer (with biases included).

		"""

		return self.__theta1

	def setTheta1 (self, theta1):
	   
		"""

		This method modify the value of the variable self.__theta1.
		This is replaced by the value contained in the theta1 variable passed as an argument.

		"""

		self.__theta1 = theta1
	

	# Getter & Setter of "theta2"
	def getTheta2 (self):
	   
		"""

		This method returns the value of the variable self.__theta2.
		self.__theta2 contains an array with output layer weigths (without bias, the biases will be the thresholds)

		"""

		return self.__theta2
	
	def setTheta2 (self, theta2):
	  
		"""

		This method modify the value of the variable self.__theta2.
		This is replaced by the value contained in the theta2 variable passed as an argument.
		
		"""

		self.__theta2 = theta2


	# Getter & Setter of "thresholds"
	def getThresholds (self):
	   
		"""

		This method returns the value of the variable self.__thresholds.
		self.__thresholds contains an array with the class thresholds parameters.
		
		"""

		return self.__thresholds
	
	def setThresholds (self, thresholds):
	  
		"""

		This method modify the value of the variable self.__thresholds.
		This is replaced by the value contained in the thresholds variable passed as an argument.
		
		"""

		self.__thresholds = thresholds


	# Getter & Setter of "num_labels"
	def getNum_labels (self):
	   
		"""

		This method returns the value of the variable self.__num_labels.
		self.__num_labels contains the number of labels in the problem.
		
		"""

		return self.__num_labels
	
	def setNum_labels (self, num_labels):
	  
		"""

		This method modify the value of the variable self.__num_labels.
		This is replaced by the value contained in the num_labels variable passed as an argument.
		
		"""

		self.__num_labels = num_labels


	# Getter & Setter of "m"
	def getM (self):
	   
		"""

		This method returns the value of the variable self.__m.
		self.__m contains the number of samples of X (train patterns array).
		
		"""

		return self.__m
	
	def setM (self, m):
	  
		"""

		This method modify the value of the variable self.__m.
		This is replaced by the value contained in the m variable passed as an argument.
		
		"""

		self.__m = m


	#--------------Private Access functions------------------


	# Download and save the values ​​of Theta1, Theta2 and thresholds_param
	# from the nn_params array to their corresponding array
	def __unpackParameters(self, nn_params, input_layer_size, hidden_layer_size, num_labels):
		
		"""
		This method gets Theta1, Theta2 and thresholds_param back from the whole array nn_params.

		Parameters
		----------

			nn_params: column array, shape ((imput_layer_size+1)*hidden_layer_size
			+ hidden_layer_size + (num_labels-1))
				Array that is a column vector. It stores the values ​​of Theta1,
				Theta2 and thresholds_param, all of them together in an array in this order.

			input_layer_size: integer
				Number of nodes in the input layer of the neural network model.
		
			hidden_layer_size: integer
				Number of nodes in the hidden layer of the neural network model.
			
			num_labels: integer
				Number of classes.


   		Returns
		-------

			Theta1: The weights between the input layer and the hidden layer (with biases included).

			Theta2: The weights between the hidden layer and the output layer
			 (biases are not included as they are the thresholds).

			thresholds_param: classification thresholds.
		
		"""

		nTheta1 = hidden_layer_size * (input_layer_size + 1)
		Theta1 = np.reshape(nn_params[0:nTheta1],(hidden_layer_size,
		 (input_layer_size + 1)))
		
		nTheta2 = hidden_layer_size
		Theta2 = np.reshape(nn_params[nTheta1:(nTheta1+nTheta2)], 
		 (1, hidden_layer_size))
		
		thresholds_param = np.reshape(nn_params[(nTheta1+nTheta2):],
		 ((num_labels-1), 1))
		
		return Theta1, Theta2, thresholds_param
	

	# Randomly initialize the weights of the neural network layer
	# by entering the number of input and output nodes of that layer
	def __randInitializeWeights(self, L_in, L_out):

		"""
		This method randomly initializes the weights of a layer
		 with L_in incoming connections and L_out outgoing connections

		 Parameters
		----------

			L_in: integer
				Number of inputs of the layer.

			L_out: integer
				Number of outputs of the layer.
		
		 Returns
		-------

			W: Array with the weights of each synaptic relationship between nodes.

		"""
		W = np.ones((L_out,L_in))
		# W = np.random.rand(L_out,L_in)*2*self.getEpsilonInit() - self.getEpsilonInit()

		return W
	

	# Calculate the thresholds
	def __convertThresholds(self, thresholds_param, num_labels):
			
		"""
		This method transforms thresholds to perform unconstrained optimization.

		thresholds(1) = thresholds_param(1)
		thresholds(2) = thresholds_param(1) + thresholds_param(2)^2
		thresholds(3) = thresholds_param(1) + thresholds_param(2)^2
						+ thresholds_param(3)^2

		Parameters
		----------

			thresholds_param: {array-like, column vector}, shape (num_labels-1, 1)
				Contains the original value of the thresholds between classes
			
			num_labels: integer
				Number of classes.

		Returns
		-------

			thresholds: thresholds of the line

		"""
			
		# Threshold ^2 element by element
		thresholds_pquad=thresholds_param**2

		# Gets row-array containing the thresholds
		thresholds = np.reshape(np.multiply(np.tile(np.concatenate((thresholds_param[0:1],
		 thresholds_pquad[1:]), axis=0), (1, num_labels-1)).T, np.tril(np.ones((num_labels-1,
		 num_labels-1)))).sum(axis=1), (num_labels-1,1)).T
		
		return thresholds


	# Implements the cost function and obtains the corresponding derivatives.
	def __nnPOMCostFunction(self, nn_params, grad, input_layer_size, hidden_layer_size,
	num_labels, X, Y, lambdaValue):
			
		"""
			This method implements the cost function and obtains
			the corresponding derivatives.
			
			Parameters
		----------

			nn_params: column array, shape ((imput_layer_size+1)*hidden_layer_size
			+ hidden_layer_size + (num_labels-1))
		
				Array that is a column vector. It stores the values ​​of Theta1,
				Theta2 and thresholds_param, all of them together in an array in this order.
			
			input_layer_size: integer
				Number of nodes in the input layer of the neural network model.
		
			hidden_layer_size: integer
				Number of nodes in the hidden layer of the neural network model.
			
			num_labels: integer
				Number of classes.

			X: {array-like, sparse matrix}, shape (n_samples, n_features)
				Training patterns array, where n_samples is the number of samples
				and n_features is the number of features

			Y: array-like, shape (n_samples)
				Target vector relative to X

			lambdaValue:
				Regularization parameter.

		Returns
		-------

			J: Matrix with cost function (updated weight matrix).
			grad: Array with the error gradient of each weight of each layer.

		"""
		
		# Unroll all the parameters
		Theta1,Theta2,thresholds_param = self.__unpackParameters(nn_params,
		input_layer_size, hidden_layer_size, num_labels)
						
		# Convert thresholds
		thresholds = self.__convertThresholds(thresholds_param, num_labels)
			
		# Setup some useful variables
		m = np.size(X, 0)
			
		# Neural Network model
		a1 = np.append(np.ones((m, 1)), X, axis=1)
		z2 = np.matmul(a1,Theta1.T)
		a2 =  1.0 / (1.0 + np.exp(-z2))

		z3 = np.tile(thresholds,(m,1)) - np.tile(np.matmul(a2,Theta2.T),(1, num_labels-1))
		a3T =  1.0 / (1.0 + np.exp(-z3))
		a3 = np.append(a3T, np.ones((m,1)), axis=1)
		h = np.concatenate((a3[:,0].reshape((a3.shape[0],1)),a3[:,1:] - a3[:,0:-1]), axis = 1)
		
		# Final output
		out = h
		
		
		# Calculate penalty (regularización L2)
		p = np.sum((Theta1[:,1:]**2).sum() + (Theta2[:,0:]**2).sum())
		
		# MSE
		#J = np.sum((out-Y)**2).sum()/(2*m) + lambdaValue*p/(2*m)
		
		# Cross entropy
		J = np.sum(-math.log(out[np.where(Y==1)]), axis=0)/m + lambdaValue*p/(2*m)
		
		
		# if nargout > 1
		
		# Cross entropy
		# out[np.where(out<0.00001)] = 0.00001
		errorDer = np.zeros(Y.shape)
		errorDer[np.where(Y!=0)] = np.divide(-Y[np.where(Y!=0)],out[np.where(Y!=0)])
	
		# MSE
		# errorDer = (out-Y)

		# Calculate sigmas
		fGradients = np.multiply(a3T,(1-a3T))
		gGradients = np.multiply(errorDer, np.concatenate((fGradients[:,0].reshape(-1,1),
		 (fGradients[:,1:] - fGradients[:,:-1]), -fGradients[:,-1].reshape(-1,1)), axis=1))
		sigma3 = -np.sum(gGradients,axis=1)
		sigma2 = np.multiply(np.multiply(np.matmul(sigma3, Theta2), a2), (1-a2))
		
		# Accumulate gradients
		delta_1 = np.matmul(sigma2.T, a1)
		delta_2 = np.matmul(sigma3.T, a2)
		
		# Calculate regularized gradient
		p1 = (lambdaValue/m) * np.concatenate((np.zeros((np.size(Theta1, axis=0), 1)), Theta1[:,1:]), axis=1)
		p2 = (lambdaValue/m) * Theta2[:,0:]
		Theta1_grad = delta_1 / m + p1
		Theta2_grad = delta_2 / m + p2
		
		
		# Treshold gradients
		ThreshGradMatrix = np.multiply(np.concatenate((np.triu(np.ones((num_labels-1, num_labels-1))),
		 np.ones((num_labels-1, 1))), axis=1), np.tile(gGradients.sum(axis=0), (num_labels-1, 1)))
		
		originalShape = ThreshGradMatrix.shape
		ThreshGradMatrix = ThreshGradMatrix.flatten(order='F')
		
		ThreshGradMatrix[(num_labels)::num_labels] = ThreshGradMatrix.flatten(order='F')[(num_labels)::num_labels] + np.multiply(errorDer[:,1:(num_labels-1)],
		 fGradients[:,0:(num_labels-2)]).sum(axis=0)
		
		ThreshGradMatrix = np.reshape(ThreshGradMatrix[:,np.newaxis],originalShape, order ='F')
		
		Threshold_grad = ThreshGradMatrix.sum(axis=1)[:,np.newaxis]
		Threshold_grad[1:] = 2 * np.multiply(Threshold_grad[1:], thresholds_param[1:])
		
		# Unroll gradients
		grad = np.concatenate((Theta1_grad.flatten(order='F'),
		 Theta2_grad.flatten(order='F'), thresholds_param.flatten(order='F')),
		 axis=0)[:,np.newaxis]
		
		return J
	

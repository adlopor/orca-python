# encoding: utf-8
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels

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
        iterations is specified by the "iter" parameter.
        
        NNPOM methods:
            fitpredict               - runs the corresponding algorithm,
                                        fitting the model and testing it
                                        in a dataset. (No es necesario, creo)
            fit                        - Fits a model from training data
            predict                    - Performs label prediction
         
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
            epsilonInit                - Range for initializing the weights.
            parameters.hiddenN         - Number of hidden neurons of the
                                        model.
            parameters.iter            - Number of iterations for iRProp+
                                        algorithm.
            parameters.lambda          - Regularization parameter.
        
    """

	#Set parameters values
    def __init__(self, epsilonInit=0.5, hiddenN=50, iter=500, lambdaValue=0.01):
        
		self.__epsilonInit = epsilonInit
        self.__hiddenN = hiddenN
		self.__iter = iter
		self.__lambdaValue = lambdaValue
    
    def fit(self,X,y)

        """
        Trains the model with TRAIN data and vector of parameters PARAMETERS.
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

		self: object
		"""
	
        pass

    def predict (self):
        pass

    def fitpredict(self):
        pass





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

        self.__epsilonInit=epsilonInit
    

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

        self.__hiddenN=hiddenN
    

    # Getter & Setter of "iter"
    def getIter (self):
       
        """
        This method returns the value of the variable self.__iter.
        self.__iter contains the number of iterations.
        """

        return self.__iter
    
    def setIter (self, iter):
      
        """
        This method modify the value of the variable self.__iter.
        This is replaced by the value contained in the iter variable passed as an argument.
        """

        self.__iter=iter
    

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

        self.__lambdaValue=lambdaValue
    
    
    
    
        

    
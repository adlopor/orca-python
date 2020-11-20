#include "Python.h"

#include "svorex_module_functions.h"

/*Python module init*/
#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

static PyMethodDef svorexMethods[] = {
	{ "fit", fit, METH_VARARGS, "Fits a model" },
    { "predict", predict, METH_VARARGS, "Predict labels" },
	{ NULL, NULL, 0, NULL }
};

#ifndef IS_PY3K /*For Python 2*/
	#ifdef __cplusplus
		extern "C" {
	#endif
			DL_EXPORT(void) initsvorex(void)
			{
			  Py_InitModule("svorex", svorexMethods);
			}
	#ifdef __cplusplus
		}
	#endif
#else /*For Python 3*/
	static struct PyModuleDef svorexmodule = {
	    PyModuleDef_HEAD_INIT,
	    "svorex",   /* name of module */
	    NULL, 		 /* module documentation, may be NULL */
	    -1,       	 /* size of per-interpreter state of the module,
	                 or -1 if the module keeps state in global variables. */
	    svorexMethods
	};

	#ifdef __cplusplus
		extern "C" {
	#endif
			PyMODINIT_FUNC
			PyInit_svorex(void){
			    return PyModule_Create(&svorexmodule);
			}
	#ifdef __cplusplus
		}
	#endif
#endif

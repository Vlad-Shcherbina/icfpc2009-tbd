static double div(double a, double b)
{
	if (b == 0.0) return 0.0;
	return a / b;
}

__declspec(dllexport) int run(int steps, double i2, double i3, double i16000, double * memory, double * output)
{ 
	int cnt = 0;
	#include "compiled_vm_declarations.inc"
	
	for (cnt = 0; cnt < steps; cnt++)
	{
		if (output[0] != 0.0)
			break;
			
		#include "compiled_vm_statements.inc"
	}
	return cnt;
}


int initcompiled_vm()
{
	return -1;
}
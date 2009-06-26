// Vorber_VM_C.cpp : Defines the entry point for the console application.
//

#include "common.h"
#include "VM.h"

int _tmain(int argc, _TCHAR* argv[])
{
	VorberVirtualMachine::Instance().LoadProgram(argv[1]);
	VorberVirtualMachine::Instance().LoadInputText(argv[2]);
	VorberVirtualMachine::Instance().Run();
	VorberVirtualMachine::Instance().WriteOutput(argv[3]);
	return 0;
}


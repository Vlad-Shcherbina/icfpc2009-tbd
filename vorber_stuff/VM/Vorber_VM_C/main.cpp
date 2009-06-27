// Vorber_VM_C.cpp : Defines the entry point for the console application.
//

#include "common.h"
#include "VM.h"

int _tmain(int argc, _TCHAR* argv[])
{
	VorberVirtualMachine* vm = new VorberVirtualMachine();
	vm->LoadProgram(argv[1]);
	vm->LoadInputText(argv[2]);
	vm->Run();
	vm->WriteOutput(argv[3]);
	delete vm;
	return 0;
}


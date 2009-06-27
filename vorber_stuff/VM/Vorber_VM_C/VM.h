#ifndef __VORBER_VM_C_VM_H_INCLUDED__
#define __VORBER_VM_C_VM_H_INCLUDED__
#include "common.h"
#include "types.h"
#include <map>

#define LOGGING

#ifdef LOGGING
#include <string>
#define LOGFILE (VorberVirtualMachine::Instance().logfile)
#endif


struct VorberVirtualMachine
{
	struct InputElement //12 byte input fragment, containing one instruction (4 bytes) and 1 data value (8 bytes)
	{
		uint* words; //we are going for performance anyway :P
	};

	struct MemCell //decoded pair
	{
		friend class VorberVirtualMachine;
		uint InstructionEncoded;
		double Data;
		MemCell(VorberVirtualMachine* _owner = NULL) : InstructionEncoded(0), Data(0.0), owner(_owner) {} ;
		MemCell(VorberVirtualMachine* owner, InputElement input, bool even);
		void Construct(InputElement input, bool even);
	private:
		VorberVirtualMachine* owner; 

	};

	struct Instruction
	{
		enum INSTRUCTION_TYPE
		{
			S = 0, D
		};
		enum S_INSTRUCTIONS
		{
			Noop = 0,
			Cmpz = 1,
			Sqrt = 2,
			Copy = 3,
			Input = 4,
			INVALID_S_INSTRUCTION = NIL
		};
		enum D_INSTRUCTIONS
		{
			Add = 1,
			Sub,
			Mult,
			Div,
			Output,
			Phi,
			INVALID_D_INSTRUCTION = NIL
		};
		enum CMPZ_IMM
		{
			LTZ = 0,
			LEZ,
			EQZ,
			GEZ,
			GTZ,
			INVALID_IMM = NIL
		};

		uint Addr1;
		uint Addr2;
		INSTRUCTION_TYPE type;
		S_INSTRUCTIONS Sop;
		D_INSTRUCTIONS Dop;
		CMPZ_IMM imm;

		Instruction(VorberVirtualMachine* machine, uint input);

		void Execute();
#ifdef LOGGING
		std::string ToString();
#endif
	private:
		VorberVirtualMachine* owner; 

	};
	
	std::map<uint, double> InputPorts;
	std::map<uint, double> OutputPorts;

	MemCell Memory[ADDRTOP];
	uint ActualCellCount;

	uint CurrentInstruction;
	bool status;

	struct Port
	{
		uint index;
		double value;
	};

	//////////////////////////////////////////////////////////////////////////
	void LoadProgram(const char* filename);
	void LoadInput(const char* filename);
	void LoadInputText(const char* filename);
	void WriteOutput(const char* filename, bool clear = false);
	//////////////////////////////////////////////////////////////////////////

	void Reset();
	void Process();

	void Run();

	//////////////////////////////////////////////////////////////////////////
	FILE* logfile;
	void MemoryDump(const char* filename);

	//////////////////////////////////////////////////////////////////////////
	VorberVirtualMachine();
	~VorberVirtualMachine();

private:
};
#endif

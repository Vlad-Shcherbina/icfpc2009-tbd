#include "types.h"
#include "VM.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <map>
#include <string>
#define TYPEMASK 0xf0000000
#define SOPMASK 0x0f000000
#define IMMMASK 0x00ffc000
#define SDATAMASK 0x00003fff
#define DOPMASK 0xf0000000
#define DD1MASK 0x0fffc000
#define DD2MASK 0x00003fff

VorberVirtualMachine::Instruction::Instruction( uint input )
{
	//type:
	//S instructions have bits 28..31 as zero
	const uint typemask = 0xf0000000;
	type = (input & TYPEMASK) > 0 ? D : S;
	switch (type)
	{
	case S:
		{
			Sop = (S_INSTRUCTIONS)((input&SOPMASK)>>28);
			imm = (CMPZ_IMM)((input&IMMMASK)>>14);
			Addr1 = (input&SDATAMASK);
			Addr2 = NIL;
			Dop = INVALID_D_INSTRUCTION;
		}
		break;
	case D:
		{
			Addr1 = (input&DD1MASK)>>14;
			Addr2 = (input&DD2MASK);
			Sop = INVALID_S_INSTRUCTION;
			Dop = (D_INSTRUCTIONS)((input&DOPMASK)>>28);
			imm = INVALID_IMM;
		}
		break;
	}
}

void VorberVirtualMachine::Instruction::Execute()
{
	std::string logstring = "";
	MemCell* Memory = VorberVirtualMachine::Instance().Memory;
	uint CurrentAddress = VorberVirtualMachine::Instance().CurrentInstruction;
	switch (type)
	{
	case S:
		{
			switch (Sop)
			{
			case Noop:
				{
					Memory[CurrentAddress].Data = Memory[CurrentAddress].Data;
				};
				break;
			case Cmpz:
				{
					switch (imm)
					{
					case LTZ:
						{
							VorberVirtualMachine::Instance().status = Memory[Addr1].Data < 0.0f;
						}
						break;
					case LEZ:
						{
							VorberVirtualMachine::Instance().status = Memory[Addr1].Data <= 0.0f;
						}
						break;
					case EQZ:
						{
							VorberVirtualMachine::Instance().status = Memory[Addr1].Data == 0.0f;
						}
						break;
					case GEZ:
						{
							VorberVirtualMachine::Instance().status = Memory[Addr1].Data >= 0.0f;
						}
						break;
					case GTZ:
						{
							VorberVirtualMachine::Instance().status = Memory[Addr1].Data > 0.0f;
						}
						break;
					}
				};
				break;
			case Sqrt:
				{
					Memory[CurrentAddress].Data = sqrt(Memory[Addr1].Data);
				};
				break;
			case Copy:
				{
					Memory[CurrentAddress].Data = Memory[Addr1].Data;
				};
				break;
			case Input:
				{
					Memory[CurrentAddress].Data = VorberVirtualMachine::Instance().InputPorts[Addr1];
				};
				break;
			}
		}
		break;

	case D:
		{
			switch (Dop)
			{
			case Add :
				{
					Memory[CurrentAddress].Data = Memory[Addr1].Data + Memory[Addr2].Data;
				};
				break;
			case Sub:
				{
					Memory[CurrentAddress].Data = Memory[Addr1].Data - Memory[Addr2].Data;
				};
				break;
			case Mult:
				{
					Memory[CurrentAddress].Data = Memory[Addr1].Data * Memory[Addr2].Data;
				};
				break;
			case Div:
				{
					if (Memory[Addr2].Data = 0.0) Memory[CurrentAddress].Data = 0.0;
					else Memory[CurrentAddress].Data = Memory[Addr1].Data / Memory[Addr2].Data;
				};
				break;
			case Output:
				{
					VorberVirtualMachine::Instance().OutputPorts[Addr1] = Memory[Addr2].Data;
				};
				break;
			case Phi:
				{
					if (VorberVirtualMachine::Instance().status) Memory[CurrentAddress].Data = Memory[Addr1].Data;
					else Memory[CurrentAddress].Data = Memory[Addr2].Data;
				};
				break;
			}
		}
		break;
	}
}
#ifdef LOGGING
std::string VorberVirtualMachine::Instruction::ToString()
{
	std::string result = "";
	char tmp[512];
	switch (type)
	{
	case S: result = "S: ";
			{
				switch (Sop)
				{
				case Noop:
					result +="Noop ";
					break;
				case Cmpz:
					result +="Cmpz ";
					switch (imm)
					{
					case LTZ:
						result +="LTZ ";
						break;
					case LEZ:
						result +="LEZ ";
						break;
					case EQZ:
						result +="EQZ ";
						break;
					case GEZ:
						result +="GEZ ";
						break;
					case GTZ:
						result +="GTZ ";
						break;
					case INVALID_IMM:
					default:
						result +="INVALID_IMM ";
						break;
					}
					break;
				case Sqrt:
					result +="Sqrt ";
					break;
				case Copy:
					result +="Copy ";
					break;
				case Input:
					result +="Input ";
					break;
				case INVALID_S_INSTRUCTION:
				default:
					result +="INVALID_S_INSTRUCTION ";
					break;
				}
				sprintf(tmp, "%d", Addr1);
				result += tmp;
			}
		break;
	case D: result = "D: ";
			{
				switch (Dop)
				{
				case Add:
					result +="Add ";
					break;
				case Sub:
					result +="Sub ";
					break;
				case Mult:
					result +="Mult ";
					break;
				case Div:
					result +="Div ";
					break;
				case Output:
					result +="Output ";
					break;
				case Phi:
					result +="Phi ";
					result += VorberVirtualMachine::Instance().status ? "status: 1 ": "status 0 ";
					break;
				case INVALID_D_INSTRUCTION:
				default:
					result +="INVALID_D_INSTRUCTION";
					break;
				}
				sprintf(tmp, "%d %d", Addr1, Addr2);
				result += tmp;

			}
		break;
	};
	return result;
}
#endif
VorberVirtualMachine& VorberVirtualMachine::Instance()
{
	static VorberVirtualMachine instance;
	return instance;
}

VorberVirtualMachine::VorberVirtualMachine()
{
	for (uint i = 0; i < ADDRTOP; i++)
	{
		Memory[i].InstructionEncoded = 0;
		Memory[i].Data = 0.0;
	}
	CurrentInstruction = 0;
	status = false;
	ActualCellCount = 0;
	logfile = fopen("VM.log", "w+");
}

void VorberVirtualMachine::LoadProgram( const char* filename )
{
	FILE* f = fopen(filename, "rb");
	uint size = ADDRTOP*3;
	uint buffer[ADDRTOP*3];
	ActualCellCount = fread(buffer, 4, ADDRTOP*3, f);
	ActualCellCount /=3;
	InputElement input;
	for (uint i = 0; i < ActualCellCount; i++)
	{
		input.words = buffer + 3*i;
		Memory[i].Construct(input, i%2 == 0);
	}
	fclose(f);
}

void VorberVirtualMachine::LoadInputText( const char* filename )
{
	InputPorts.clear();
	FILE* F = fopen(filename, "r");
	char buff[512];
	while (NULL != fgets(buff, 512, F))
	{
		uint i;
		double d;
		sscanf(buff, "%i %f\n", &i, &d);
		InputPorts[i] = d;
	}
	fclose(F);
}

void VorberVirtualMachine::WriteOutput( const char* filename, bool clear )
{
	FILE* F = fopen(filename, "w+");
	char* buff[512];
	for (std::map<uint, double>::iterator i = OutputPorts.begin(); i != OutputPorts.end(); i++)
	{
		fprintf(F, "%04x %f\n", i->first, i->second);
	}
	fclose(F);
	if (clear)
		OutputPorts.clear();
}

void VorberVirtualMachine::Reset()
{
	CurrentInstruction = 0;
	status = false;
	OutputPorts.clear();
}

void VorberVirtualMachine::Process()
{
	Instruction ins(Memory[CurrentInstruction].InstructionEncoded);
	fprintf(logfile, "%04x: %s\n", CurrentInstruction, ins.ToString().c_str());
	ins.Execute();
	CurrentInstruction++;
}

void VorberVirtualMachine::Run()
{
	while (CurrentInstruction < ADDRTOP)
	{
		Process();
	}
	MemoryDump("dump");
}

VorberVirtualMachine::~VorberVirtualMachine()
{
	fclose(logfile);
}

void VorberVirtualMachine::MemoryDump( const char* filename )
{
	FILE* F = fopen(filename, "w+");
	char* buff[512];
	for (uint i = 0; i < ADDRTOP; i++)
	{
		fprintf(F, "%04x %f\n", i, Memory[i].Data);
	}
	fclose(F);
}
VorberVirtualMachine::MemCell::MemCell( InputElement input, bool even )
{
	Construct(input, even);
}

void VorberVirtualMachine::MemCell::Construct( InputElement input, bool even )
{
	if (even)
	{
		memmove(&Data, input.words, 8);
		InstructionEncoded = input.words[2];
	}
	else
	{
		InstructionEncoded = input.words[0];
		memmove(&Data, input.words+1, 8);
	}
}
#ifndef CAPN_CONVERSIONS_HPP
#define CAPN_CONVERSIONS_HPP


#include "..\PacketStructs\LiveDataPacket.hpp"
#include "..\PacketStructs\PacketStructs.hpp"
#include "..\ErrorCodes\ErrorCodes.hpp"
#include <kj\windows-sanity.h>
#undef VOID
#include "game_data.capnp.h"
#include <capnp\serialize.h>
#include <capnp\message.h>

typedef void* CompiledGameTickPacket;
typedef void* CompiledControllerState;
typedef void* CompiledDesiredGameState;

namespace CapnConversions {

	struct ByteBuffer
	{
		void* ptr;
		int size;
	};

	// Convert 
	ByteBuffer liveDataPacketToBuffer(LiveDataPacket* pLiveData);
	IndexedPlayerInput* bufferToPlayerInput(ByteBuffer buf);
}

#endif  // !CAPN_CONVERSIONS_HPP
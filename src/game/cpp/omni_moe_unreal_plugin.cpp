#include "omni_moe_unreal_plugin.h"
#include "Misc/MessageDialog.h"
#include "Modules/ModuleManager.h"
#include "Interfaces/IPluginManager.h"

#define LOCTEXT_NAMESPACE "FOmniMoEPluginModule"

void FOmniMoEPluginModule::StartupModule()
{
	// This code will execute after your module is loaded into memory.
	UE_LOG(LogTemp, Log, TEXT("OMNI C++ (Unreal): Starting MoE Integration Plugin."));
	
	// Default to local gateway
	OmniGatewayURL = TEXT("http://127.0.0.1:8080/v1/generate");
}

void FOmniMoEPluginModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.
	UE_LOG(LogTemp, Log, TEXT("OMNI C++ (Unreal): Shutting down MoE Integration Plugin."));
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FOmniMoEPluginModule, OmniMoEPlugin)

// Note: Usage in an Actor would involve FHttpModule to make POST requests 
// to OmniGatewayURL passing the game context as prompt.

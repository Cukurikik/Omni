#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * OMNI Framework - Unreal Engine Plugin Module
 * Acts as the bridge linking Unreal Engine 5 actors with the local or remote
 * OMNI MoE Inference Gateway for generating dynamic gameplay narratives.
 */
class FOmniMoEPluginModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	// Global endpoint for the OMNI Router
	FString OmniGatewayURL;
};

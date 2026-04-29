#include "OmniMetaHumanController.h"

// Omni Unreal C++ MetaHuman Controller.
// Deterministic skeletal animation bridge.

bool UOmniMetaHumanController::ApplyFacialWeights(const TArray<float>& BlendWeights)
{
    if (BlendWeights.Num() == 0)
    {
        return false; // Monadic-style early return
    }

    if (!FacialMeshComponent)
    {
        return false;
    }

    // Deterministic blending application
    for (int32 i = 0; i < BlendWeights.Num(); ++i)
    {
        FName MorphName = FName(*FString::Printf(TEXT("Morph_%d"), i));
        FacialMeshComponent->SetMorphTarget(MorphName, BlendWeights[i]);
    }

    return true;
}

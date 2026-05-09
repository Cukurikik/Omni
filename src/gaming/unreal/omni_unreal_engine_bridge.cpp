// Omni Unreal Engine 5 Bridge (C++)
// Gaming & Simulation Layer
// Binds the Omni Universal Binary to UE5 Blueprints, allowing 
// NPC conversational AI to run locally without network calls.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "OmniUEBridge.generated.h"

// Forward declaration of the Omni C-ABI
extern "C" {
    typedef void* OmniModelHandle;
    OmniModelHandle omni_load_model(const char* path);
    int omni_generate(OmniModelHandle handle, const char* prompt, char* output_buffer, int max_len);
    void omni_free_model(OmniModelHandle handle);
}

UCLASS()
class OMNI_API UOmniBlueprintLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

private:
    static OmniModelHandle GlobalModelHandle;

public:
    UFUNCTION(BlueprintCallable, Category = "Omni AI")
    static bool InitializeOmniCore(const FString& ModelPath)
    {
        if (GlobalModelHandle != nullptr) {
            return true;
        }
        
        GlobalModelHandle = omni_load_model(TCHAR_TO_UTF8(*ModelPath));
        return GlobalModelHandle != nullptr;
    }

    UFUNCTION(BlueprintCallable, Category = "Omni AI")
    static FString GenerateNPCDialogue(const FString& Prompt, int32 MaxLength = 256)
    {
        if (GlobalModelHandle == nullptr) {
            return TEXT("Error: Omni Core not initialized.");
        }

        char* Buffer = (char*)malloc(MaxLength);
        if (Buffer == nullptr) return TEXT("");

        int status = omni_generate(GlobalModelHandle, TCHAR_TO_UTF8(*Prompt), Buffer, MaxLength);
        
        FString Result(UTF8_TO_TCHAR(Buffer));
        free(Buffer);

        if (status != 0) {
            return TEXT("Error: Inference failed.");
        }

        return Result;
    }
};

// Initialize static member
OmniModelHandle UOmniBlueprintLibrary::GlobalModelHandle = nullptr;

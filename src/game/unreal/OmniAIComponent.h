// OMNI Framework - Unreal Engine AI Component
// Exposes LLM API interactions to Unreal Blueprints via C++

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Http.h"
#include "OmniAIComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnOmniResponseReceived, const FString&, ResponseText);

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class OMNI_API UOmniAIComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	UOmniAIComponent();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="OMNI AI")
	FString ApiEndpoint;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="OMNI AI")
	FString SystemPrompt;

	UPROPERTY(BlueprintAssignable, Category="OMNI AI")
	FOnOmniResponseReceived OnResponseReceived;

	UFUNCTION(BlueprintCallable, Category="OMNI AI")
	void GenerateResponse(const FString& PlayerInput);

protected:
	virtual void BeginPlay() override;

private:
	void OnHttpResponseComplete(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
};

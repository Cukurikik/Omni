// @omni-layer Game | @omni-lang Unreal C++ | @omni-batch 17
// @omni-description Unreal RL agent header with observation, action, reward.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OmniRLAgent.generated.h"

USTRUCT(BlueprintType)
struct FOmniObs {
    GENERATED_BODY()
    UPROPERTY() TArray<float> Features;
    UPROPERTY() float Reward;
    UPROPERTY() bool bDone;
    UPROPERTY() int32 Step;
};

UCLASS()
class AOmniRLAgent : public AActor {
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere) int32 ObsDim = 24;
    UPROPERTY(EditAnywhere) int32 MaxSteps = 1000;
    UPROPERTY(EditAnywhere) AActor* Goal;
    UFUNCTION(BlueprintCallable) FOmniObs Reset();
    UFUNCTION(BlueprintCallable) FOmniObs Step(const TArray<float>& Act);
private:
    int32 CurStep = 0; float EpReward = 0; bool Done = false;
};

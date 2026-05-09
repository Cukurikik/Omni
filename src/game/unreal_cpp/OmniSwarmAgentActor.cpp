// OMNI Framework - Unreal Engine 5 Actor for AthenaOS Agent Visualization
#include "OmniSwarmAgentActor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"

AOmniSwarmAgentActor::AOmniSwarmAgentActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SphereCollider = CreateDefaultSubobject<USphereComponent>(TEXT("SphereCollider"));
    RootComponent = SphereCollider;
    SphereCollider->InitSphereRadius(50.0f);

    AgentMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AgentMesh"));
    AgentMesh->SetupAttachment(RootComponent);
    
    CurrentState = ESwarmAgentState::IDLE;
}

void AOmniSwarmAgentActor::BeginPlay()
{
    Super::BeginPlay();
}

void AOmniSwarmAgentActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // Simulate swarm movement based on OMNI Network signals
    if (CurrentState == ESwarmAgentState::COMPUTING)
    {
        FVector NewLocation = GetActorLocation() + (GetActorForwardVector() * Speed * DeltaTime);
        SetActorLocation(NewLocation);
    }
}

void AOmniSwarmAgentActor::UpdateStateFromOmniNetwork(FString NewStateStr)
{
    if (NewStateStr == "COMPUTING") {
        CurrentState = ESwarmAgentState::COMPUTING;
    } else {
        CurrentState = ESwarmAgentState::IDLE;
    }
}

// OMNI Game Layer — Unreal C++ AI Subsystem
// Transformer-powered NPC AI for Unreal Engine 5.
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Http.h"
#include "Json.h"
#include "OmniAISubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnInferenceComplete, FString, RequestId, FString, Response);

USTRUCT(BlueprintType)
struct FOmniInferenceRequest {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Prompt;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MaxTokens = 128;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float Temperature = 0.8f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString RequestId;
};

UCLASS()
class OMNIGAME_API UOmniAISubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UPROPERTY(BlueprintAssignable) FOnInferenceComplete OnInferenceComplete;

    UFUNCTION(BlueprintCallable, Category="OmniAI")
    void SendInference(const FOmniInferenceRequest& Request);

    UFUNCTION(BlueprintCallable, Category="OmniAI")
    void SetEndpoint(const FString& Url) { ApiEndpoint = Url; }

    UFUNCTION(BlueprintPure, Category="OmniAI")
    int32 GetTotalRequests() const { return TotalRequests; }

private:
    void OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
    FString ApiEndpoint = TEXT("http://localhost:8080/api/v1/infer");
    int32 TotalRequests = 0;
    float TotalLatencyMs = 0.f;
};

// Implementation
void UOmniAISubsystem::Initialize(FSubsystemCollectionBase& Collection) {
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("OmniAI Subsystem initialized"));
}

void UOmniAISubsystem::SendInference(const FOmniInferenceRequest& Request) {
    TotalRequests++;
    auto HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetURL(ApiEndpoint);
    HttpRequest->SetVerb(TEXT("POST"));
    HttpRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));

    TSharedPtr<FJsonObject> JsonObj = MakeShareable(new FJsonObject);
    JsonObj->SetStringField(TEXT("prompt"), Request.Prompt);
    JsonObj->SetNumberField(TEXT("max_tokens"), Request.MaxTokens);
    JsonObj->SetNumberField(TEXT("temperature"), Request.Temperature);

    FString Body;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Body);
    FJsonSerializer::Serialize(JsonObj.ToSharedRef(), Writer);
    HttpRequest->SetContentAsString(Body);
    HttpRequest->OnProcessRequestComplete().BindUObject(this, &UOmniAISubsystem::OnResponseReceived);
    HttpRequest->ProcessRequest();
}

void UOmniAISubsystem::OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess) {
    FString Result = TEXT("No response");
    if (bSuccess && Response.IsValid()) {
        TSharedPtr<FJsonObject> JsonResponse;
        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());
        if (FJsonSerializer::Deserialize(Reader, JsonResponse)) {
            Result = JsonResponse->GetStringField(TEXT("generated_text"));
        }
    }
    OnInferenceComplete.Broadcast(TEXT(""), Result);
}

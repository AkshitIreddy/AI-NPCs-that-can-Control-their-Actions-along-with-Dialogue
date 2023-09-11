#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyBlueprintFunctionLibrary.generated.h"

/**
 * 
 */
UCLASS()
class PROJECT_API UMyBlueprintFunctionLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
	
public:
	UFUNCTION(BlueprintPure, Category = "File Operations", meta = (Keywords = "Load Text File"))
		static bool LoadTxt(FString FileNameA, FString& SaveTextA);

	UFUNCTION(BlueprintCallable, Category = "File Operations", meta = (Keywords = "Save Text File"))
		static bool SaveTxt(FString SaveTextB, FString FileNameB);

	UFUNCTION(BlueprintCallable, Category = "Flowers", meta = (Keywords = "Spawn Flowers around Object"))
		static void SpawnFlowersAroundObject(AActor* SpawnAroundObject, TSubclassOf<AActor> FlowerClass, int32 NumFlowers);
};

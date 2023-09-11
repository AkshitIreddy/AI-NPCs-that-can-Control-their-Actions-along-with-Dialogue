// Fill out your copyright notice in the Description page of Project Settings.


#include "MyBlueprintFunctionLibrary.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Engine/World.h"

bool UMyBlueprintFunctionLibrary::LoadTxt(FString FileNameA, FString& SaveTextA)
{
    return FFileHelper::LoadFileToString(SaveTextA, *(FPaths::ProjectDir() + FileNameA));
}

bool UMyBlueprintFunctionLibrary::SaveTxt(FString SaveTextB, FString FileNameB)
{
    return FFileHelper::SaveStringToFile(SaveTextB, *(FPaths::ProjectDir() + FileNameB));
}

void UMyBlueprintFunctionLibrary::SpawnFlowersAroundObject(AActor* SpawnAroundObject, TSubclassOf<AActor> FlowerClass, int32 NumFlowers)
{
    if (!SpawnAroundObject || !FlowerClass)
    {
        // Check if the input parameters are valid
        return;
    }

    UWorld* World = SpawnAroundObject->GetWorld();
    if (!World)
    {
        // Ensure we have a valid world
        return;
    }

    FVector SpawnLocation = SpawnAroundObject->GetActorLocation();
    FRotator SpawnRotation = FRotator::ZeroRotator;

    for (int32 i = 0; i < NumFlowers; ++i)
    {
        FVector Offset = FVector(FMath::FRandRange(-200.0f, 200.0f), FMath::FRandRange(-200.0f, 200.0f), 0.0f);
        FVector FlowerSpawnLocation = SpawnLocation + Offset;

        // Spawn the flower
        AActor* SpawnedFlower = World->SpawnActor(FlowerClass, &FlowerSpawnLocation, &SpawnRotation);

        if (SpawnedFlower)
        {
            // You can customize the spawned flower's properties here if needed.
        }
    }
}

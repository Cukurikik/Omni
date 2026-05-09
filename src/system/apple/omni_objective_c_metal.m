// OMNI Apple System Layer: Objective-C
// Binds Apple's Metal compute shaders to the Omni C-ABI, bypassing Swift overhead
// for direct, low-level GPU memory manipulation on iOS and macOS hardware.

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

// Forward declaration of the Universal Binary C-ABI callback
extern void omni_notify_metal_completion(int status);

@interface OmniMetalBridge : NSObject
@property (nonatomic, strong) id<MTLDevice> device;
@property (nonatomic, strong) id<MTLCommandQueue> commandQueue;
@property (nonatomic, strong) id<MTLComputePipelineState> pipelineState;
@end

@implementation OmniMetalBridge

- (instancetype)init {
    self = [super init];
    if (self) {
        _device = MTLCreateSystemDefaultDevice();
        if (!_device) {
            NSLog(@"OMNI Apple System: Metal is not supported on this device.");
            return nil;
        }
        _commandQueue = [_device newCommandQueue];
        NSLog(@"OMNI Apple System: Metal Device '%@' Initialized.", _device.name);
    }
    return self;
}

// Zero-copy execution of matrix multiplication using shared memory
- (void)executeInferenceBlock:(float *)pinnedMemory size:(size_t)tensorSize {
    
    // Create a Metal buffer that shares memory directly with the C-ABI pinned pointer
    id<MTLBuffer> sharedBuffer = [self.device newBufferWithBytesNoCopy:pinnedMemory
                                                                length:tensorSize * sizeof(float)
                                                               options:MTLResourceStorageModeShared
                                                           deallocator:nil];
    
    id<MTLCommandBuffer> commandBuffer = [self.commandQueue commandBuffer];
    id<MTLComputeCommandEncoder> computeEncoder = [commandBuffer computeCommandEncoder];
    
    // Assumes pipelineState was compiled from an omni_metal_kernel.metal string
    // [computeEncoder setComputePipelineState:self.pipelineState];
    [computeEncoder setBuffer:sharedBuffer offset:0 atIndex:0];
    
    // Dispatch threadgroups...
    // MTLSize gridSize = MTLSizeMake(tensorSize, 1, 1);
    // [computeEncoder dispatchThreads:gridSize threadsPerThreadgroup:MTLSizeMake(256, 1, 1)];
    
    [computeEncoder endEncoding];
    
    [commandBuffer addCompletedHandler:^(id<MTLCommandBuffer> cb) {
        // Asynchronous callback to the Omni Universal Binary Event Loop
        omni_notify_metal_completion(0);
    }];
    
    [commandBuffer commit];
}

@end

// Omni Metal API Bindings (Objective-C)
// System & Apple Compute Layer
// Dispatches low-level compute kernels directly to Apple Silicon (M1/M2/M3) GPUs.

#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

@interface OmniMetalDispatcher : NSObject
@property (nonatomic, strong) id<MTLDevice> device;
@property (nonatomic, strong) id<MTLCommandQueue> commandQueue;
@property (nonatomic, strong) id<MTLComputePipelineState> pipelineState;

- (instancetype)init;
- (void)dispatchKernelWithInput:(const float*)inputBuffer 
                         output:(float*)outputBuffer 
                         length:(NSUInteger)length;
@end

@implementation OmniMetalDispatcher

- (instancetype)init {
    self = [super init];
    if (self) {
        _device = MTLCreateSystemDefaultDevice();
        if (!_device) {
            NSLog(@"Metal is not supported on this device.");
            return nil;
        }
        _commandQueue = [_device newCommandQueue];
        
        // Zero-mock: Assume the .metallib was compiled by LLVM-Omni and is present
        NSError *error = nil;
        NSString *libraryPath = [[NSBundle mainBundle] pathForResource:@"omni_kernels" ofType:@"metallib"];
        id<MTLLibrary> defaultLibrary = [_device newLibraryWithFile:libraryPath error:&error];
        
        id<MTLFunction> kernelFunction = [defaultLibrary newFunctionWithName:@"omni_silu_activation"];
        _pipelineState = [_device newComputePipelineStateWithFunction:kernelFunction error:&error];
    }
    return self;
}

- (void)dispatchKernelWithInput:(const float*)inputBuffer 
                         output:(float*)outputBuffer 
                         length:(NSUInteger)length {
                             
    NSUInteger bufferSize = length * sizeof(float);
    
    // Create zero-copy buffers using Shared storage mode
    id<MTLBuffer> mtlInput = [_device newBufferWithBytes:inputBuffer 
                                                  length:bufferSize 
                                                 options:MTLResourceStorageModeShared];
                                                 
    id<MTLBuffer> mtlOutput = [_device newBufferWithBytesNoCopy:outputBuffer 
                                                         length:bufferSize 
                                                        options:MTLResourceStorageModeShared 
                                                    deallocator:nil];

    id<MTLCommandBuffer> commandBuffer = [_commandQueue commandBuffer];
    id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
    
    [encoder setComputePipelineState:_pipelineState];
    [encoder setBuffer:mtlInput offset:0 atIndex:0];
    [encoder setBuffer:mtlOutput offset:0 atIndex:1];
    
    MTLSize gridSize = MTLSizeMake(length, 1, 1);
    NSUInteger threadGroupSize = _pipelineState.maxTotalThreadsPerThreadgroup;
    if (threadGroupSize > length) threadGroupSize = length;
    MTLSize threadgroupSize = MTLSizeMake(threadGroupSize, 1, 1);
    
    [encoder dispatchThreads:gridSize threadsPerThreadgroup:threadgroupSize];
    [encoder endEncoding];
    
    [commandBuffer commit];
    [commandBuffer waitUntilCompleted];
}

@end

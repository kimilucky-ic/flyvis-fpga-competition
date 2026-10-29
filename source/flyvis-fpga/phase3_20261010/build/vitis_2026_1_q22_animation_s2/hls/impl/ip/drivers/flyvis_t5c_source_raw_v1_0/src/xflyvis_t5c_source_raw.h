// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
// Tool Version Limit: 2026.06
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
#ifndef XFLYVIS_T5C_SOURCE_RAW_H
#define XFLYVIS_T5C_SOURCE_RAW_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xflyvis_t5c_source_raw_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
#ifdef SDT
    char *Name;
#else
    u16 DeviceId;
#endif
    u64 Control_BaseAddress;
} XFlyvis_t5c_source_raw_Config;
#endif

typedef struct {
    u64 Control_BaseAddress;
    u32 IsReady;
} XFlyvis_t5c_source_raw;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XFlyvis_t5c_source_raw_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XFlyvis_t5c_source_raw_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XFlyvis_t5c_source_raw_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XFlyvis_t5c_source_raw_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
#ifdef SDT
int XFlyvis_t5c_source_raw_Initialize(XFlyvis_t5c_source_raw *InstancePtr, UINTPTR BaseAddress);
XFlyvis_t5c_source_raw_Config* XFlyvis_t5c_source_raw_LookupConfig(UINTPTR BaseAddress);
#else
int XFlyvis_t5c_source_raw_Initialize(XFlyvis_t5c_source_raw *InstancePtr, u16 DeviceId);
XFlyvis_t5c_source_raw_Config* XFlyvis_t5c_source_raw_LookupConfig(u16 DeviceId);
#endif
int XFlyvis_t5c_source_raw_CfgInitialize(XFlyvis_t5c_source_raw *InstancePtr, XFlyvis_t5c_source_raw_Config *ConfigPtr);
#else
int XFlyvis_t5c_source_raw_Initialize(XFlyvis_t5c_source_raw *InstancePtr, const char* InstanceName);
int XFlyvis_t5c_source_raw_Release(XFlyvis_t5c_source_raw *InstancePtr);
#endif

void XFlyvis_t5c_source_raw_Start(XFlyvis_t5c_source_raw *InstancePtr);
u32 XFlyvis_t5c_source_raw_IsDone(XFlyvis_t5c_source_raw *InstancePtr);
u32 XFlyvis_t5c_source_raw_IsIdle(XFlyvis_t5c_source_raw *InstancePtr);
u32 XFlyvis_t5c_source_raw_IsReady(XFlyvis_t5c_source_raw *InstancePtr);
void XFlyvis_t5c_source_raw_EnableAutoRestart(XFlyvis_t5c_source_raw *InstancePtr);
void XFlyvis_t5c_source_raw_DisableAutoRestart(XFlyvis_t5c_source_raw *InstancePtr);
u32 XFlyvis_t5c_source_raw_Get_return(XFlyvis_t5c_source_raw *InstancePtr);

void XFlyvis_t5c_source_raw_Set_request(XFlyvis_t5c_source_raw *InstancePtr, u64 Data);
u64 XFlyvis_t5c_source_raw_Get_request(XFlyvis_t5c_source_raw *InstancePtr);
void XFlyvis_t5c_source_raw_Set_result(XFlyvis_t5c_source_raw *InstancePtr, u64 Data);
u64 XFlyvis_t5c_source_raw_Get_result(XFlyvis_t5c_source_raw *InstancePtr);

void XFlyvis_t5c_source_raw_InterruptGlobalEnable(XFlyvis_t5c_source_raw *InstancePtr);
void XFlyvis_t5c_source_raw_InterruptGlobalDisable(XFlyvis_t5c_source_raw *InstancePtr);
void XFlyvis_t5c_source_raw_InterruptEnable(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask);
void XFlyvis_t5c_source_raw_InterruptDisable(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask);
void XFlyvis_t5c_source_raw_InterruptClear(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask);
u32 XFlyvis_t5c_source_raw_InterruptGetEnabled(XFlyvis_t5c_source_raw *InstancePtr);
u32 XFlyvis_t5c_source_raw_InterruptGetStatus(XFlyvis_t5c_source_raw *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif

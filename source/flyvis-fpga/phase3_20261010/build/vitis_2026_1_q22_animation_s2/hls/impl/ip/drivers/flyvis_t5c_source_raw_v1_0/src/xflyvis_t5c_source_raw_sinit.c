// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
// Tool Version Limit: 2026.06
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
#ifndef __linux__

#include "xstatus.h"
#ifdef SDT
#include "xparameters.h"
#endif
#include "xflyvis_t5c_source_raw.h"

extern XFlyvis_t5c_source_raw_Config XFlyvis_t5c_source_raw_ConfigTable[];

#ifdef SDT
XFlyvis_t5c_source_raw_Config *XFlyvis_t5c_source_raw_LookupConfig(UINTPTR BaseAddress) {
	XFlyvis_t5c_source_raw_Config *ConfigPtr = NULL;

	int Index;

	for (Index = (u32)0x0; XFlyvis_t5c_source_raw_ConfigTable[Index].Name != NULL; Index++) {
		if (!BaseAddress || XFlyvis_t5c_source_raw_ConfigTable[Index].Control_BaseAddress == BaseAddress) {
			ConfigPtr = &XFlyvis_t5c_source_raw_ConfigTable[Index];
			break;
		}
	}

	return ConfigPtr;
}

int XFlyvis_t5c_source_raw_Initialize(XFlyvis_t5c_source_raw *InstancePtr, UINTPTR BaseAddress) {
	XFlyvis_t5c_source_raw_Config *ConfigPtr;

	Xil_AssertNonvoid(InstancePtr != NULL);

	ConfigPtr = XFlyvis_t5c_source_raw_LookupConfig(BaseAddress);
	if (ConfigPtr == NULL) {
		InstancePtr->IsReady = 0;
		return (XST_DEVICE_NOT_FOUND);
	}

	return XFlyvis_t5c_source_raw_CfgInitialize(InstancePtr, ConfigPtr);
}
#else
XFlyvis_t5c_source_raw_Config *XFlyvis_t5c_source_raw_LookupConfig(u16 DeviceId) {
	XFlyvis_t5c_source_raw_Config *ConfigPtr = NULL;

	int Index;

	for (Index = 0; Index < XPAR_XFLYVIS_T5C_SOURCE_RAW_NUM_INSTANCES; Index++) {
		if (XFlyvis_t5c_source_raw_ConfigTable[Index].DeviceId == DeviceId) {
			ConfigPtr = &XFlyvis_t5c_source_raw_ConfigTable[Index];
			break;
		}
	}

	return ConfigPtr;
}

int XFlyvis_t5c_source_raw_Initialize(XFlyvis_t5c_source_raw *InstancePtr, u16 DeviceId) {
	XFlyvis_t5c_source_raw_Config *ConfigPtr;

	Xil_AssertNonvoid(InstancePtr != NULL);

	ConfigPtr = XFlyvis_t5c_source_raw_LookupConfig(DeviceId);
	if (ConfigPtr == NULL) {
		InstancePtr->IsReady = 0;
		return (XST_DEVICE_NOT_FOUND);
	}

	return XFlyvis_t5c_source_raw_CfgInitialize(InstancePtr, ConfigPtr);
}
#endif

#endif


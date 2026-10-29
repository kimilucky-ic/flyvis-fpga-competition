// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
// Tool Version Limit: 2026.06
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
/***************************** Include Files *********************************/
#include "xflyvis_t5c_source_raw.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XFlyvis_t5c_source_raw_CfgInitialize(XFlyvis_t5c_source_raw *InstancePtr, XFlyvis_t5c_source_raw_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Control_BaseAddress = ConfigPtr->Control_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XFlyvis_t5c_source_raw_Start(XFlyvis_t5c_source_raw *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL) & 0x80;
    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XFlyvis_t5c_source_raw_IsDone(XFlyvis_t5c_source_raw *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XFlyvis_t5c_source_raw_IsIdle(XFlyvis_t5c_source_raw *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XFlyvis_t5c_source_raw_IsReady(XFlyvis_t5c_source_raw *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XFlyvis_t5c_source_raw_EnableAutoRestart(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL, 0x80);
}

void XFlyvis_t5c_source_raw_DisableAutoRestart(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_CTRL, 0);
}

u32 XFlyvis_t5c_source_raw_Get_return(XFlyvis_t5c_source_raw *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_AP_RETURN);
    return Data;
}
void XFlyvis_t5c_source_raw_Set_request(XFlyvis_t5c_source_raw *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_REQUEST_DATA, (u32)(Data));
    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_REQUEST_DATA + 4, (u32)(Data >> 32));
}

u64 XFlyvis_t5c_source_raw_Get_request(XFlyvis_t5c_source_raw *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_REQUEST_DATA);
    Data += (u64)XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_REQUEST_DATA + 4) << 32;
    return Data;
}

void XFlyvis_t5c_source_raw_Set_result(XFlyvis_t5c_source_raw *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_RESULT_DATA, (u32)(Data));
    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_RESULT_DATA + 4, (u32)(Data >> 32));
}

u64 XFlyvis_t5c_source_raw_Get_result(XFlyvis_t5c_source_raw *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_RESULT_DATA);
    Data += (u64)XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_RESULT_DATA + 4) << 32;
    return Data;
}

void XFlyvis_t5c_source_raw_InterruptGlobalEnable(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_GIE, 1);
}

void XFlyvis_t5c_source_raw_InterruptGlobalDisable(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_GIE, 0);
}

void XFlyvis_t5c_source_raw_InterruptEnable(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_IER);
    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_IER, Register | Mask);
}

void XFlyvis_t5c_source_raw_InterruptDisable(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_IER);
    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_IER, Register & (~Mask));
}

void XFlyvis_t5c_source_raw_InterruptClear(XFlyvis_t5c_source_raw *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFlyvis_t5c_source_raw_WriteReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_ISR, Mask);
}

u32 XFlyvis_t5c_source_raw_InterruptGetEnabled(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_IER);
}

u32 XFlyvis_t5c_source_raw_InterruptGetStatus(XFlyvis_t5c_source_raw *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XFlyvis_t5c_source_raw_ReadReg(InstancePtr->Control_BaseAddress, XFLYVIS_T5C_SOURCE_RAW_CONTROL_ADDR_ISR);
}


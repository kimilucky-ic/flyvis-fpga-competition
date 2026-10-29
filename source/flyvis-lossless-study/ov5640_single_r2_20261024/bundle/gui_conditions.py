"""Explicit conditional functional test, never electrical signoff."""
PROFILE='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1'

def check_conditions(c):
    if c.get('board_family')!='Leader ZYNQ-7020' or c.get('part')!='xc7z020clg400-2' or c.get('baseboard_revision')!='V3.9':
        raise ValueError('Only confirmed Leader7020 V3.9 scope')
    if c.get('transport_revision')!='IIC21_R2' or c.get('delivery_revision')!='LINE11_SINGLE_R2':raise ValueError('Wrong isolated candidate revision')
    if c.get('test_profile')!=PROFILE:raise ValueError('Explicit conditional profile required; old generic flags not sufficient')
    if c.get('manufacturer_compatibility')!='USER_REPORTED_MANUFACTURER_CONFIRMED':raise ValueError('Manufacturer confirmation absent')
    for k in ('camera_io_3v3_verified','pinmap_and_orientation_verified','exclusive_board_ownership',
              'module_nominal_24MHz_documented','PS_nominal_reference_documented','unmeasured_timing_accepted'):
        if c.get(k) is not True:raise ValueError('Required admission absent: '+k)
    if c.get('operator_confirmation')!='同意单帧测试':raise ValueError('Human conditional-test confirmation absent')
    for k in ('physical_clock_measured','SCCB_rise_time_measured','DVP_external_timing_measured'):
        if c.get(k) is not False:raise ValueError('This profile cannot claim measured external timing: '+k)
    if c.get('SCCB_pullups_voltage_and_rise_time_checked') is not False:
        raise ValueError('Preserve combined SCCB measurement flag as false; circuit pullups documented separately')
    if c.get('channel_order') not in ('RGB','BGR','GBR'):raise ValueError('Explicit channel order required')

def current_hp(mmio,boot_id):
    from gui_ps_readonly import inspect
    pages={}
    def read(address):
        base=address&~0xfff
        if base not in pages:pages[base]=mmio(base,4096)
        return int(pages[base].read(address-base))
    result=inspect(read);result['boot_id']=boot_id
    if not result['HP0_HP1_64bit_verified']:raise RuntimeError('Current HP admission failed: '+str(result))
    return result

def check_hp_evidence(hp,boot_id):
    if hp.get('boot_id')!=boot_id or hp.get('status')!='PASS_CURRENT_HP_WIDTH_ONLY':raise ValueError('HP boot/status mismatch')
    raw=hp['raw_registers']
    if raw.get('0xf8000240')!=0:raise ValueError('HP reset admission absent')
    for a in ('0xf8008000','0xf8008014','0xf8009000','0xf8009014'):
        v=raw.get(a)
        if not isinstance(v,int) or not 0<=v<=0xffffffff or v&1:raise ValueError('HP not64bit: '+a)
    if hp.get('register_writes')!=0 or hp.get('HP0_HP1_64bit_verified') is not True:raise ValueError('Not readonly64bit evidence')

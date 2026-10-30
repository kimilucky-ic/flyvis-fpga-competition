"""Explicit wall/model time mapping; never changes the 5ms Euler update."""
import math
from live_protocol import require

DT=.005

def clock_spec(rate):
    require(type(rate) is int and rate in (50,100,200),'STREAM_CLOCK_RATE')
    return dict(schema='flyvis-stream-clock/v1',target_steps_per_s=rate,model_dt_s=DT,
                model_seconds_per_wall_second=rate*DT,
                mode='ORIGINAL_TIME_SCALE' if rate==200 else 'SLOW_MODEL_DEMO',
                source_time_policy='MODEL_TIME_EQUALS_CAPTURE_RELATIVE_SECONDS_TIMES_SCALE',
                lag_limit_clock='WALL_SECONDS_BEHIND_SELECTED_RATE')

def control_clock(control):
    # Pre-clock saved records and protocol fixtures retain their original rate.
    spec=control.get('clock',clock_spec(200))
    require(spec==clock_spec(spec['target_steps_per_s']),'STREAM_CLOCK_IDENTITY')
    if 'clock' in control:require(control['binding']['clock']==spec,'STREAM_CLOCK_BINDING')
    return spec

def model_source_time(source,spec):
    wall=source['relative_s'];require(math.isfinite(wall) and wall>=0,'SOURCE_WALL_TIME')
    model=wall*spec['model_seconds_per_wall_second']
    require(source.get('model_relative_s',model)==model,'SOURCE_MODEL_TIME_MAPPING')
    return model

def schedule(step,elapsed,spec):
    due=step/spec['target_steps_per_s']
    return max(0,due-elapsed),max(0,elapsed-due)

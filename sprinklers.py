from homeassistant.const import EVENT_STATE_CHANGED

zone_max= 5 #Max number of zones

def bypass_valve(action=None):
    """ Turn on/off bypass valve switch"""
    if action == "turn_on":
        switch.turn_on(entity_id=f"switch.bypass_grid_valve")
    elif action == "turn_off":
        switch.turn_off(entity_id=f"switch.bypass_grid_valve")
        
        
def auto_pump(action=None):
    """ Turn on/off auto pump"""
    if action == "turn_on":
        switch.turn_on(entity_id=f"switch.pump_auto")
        switch.turn_on(entity_id=f"switch.pump_trigger")
    elif action == "turn_off":
        switch.turn_off(entity_id=f"switch.pump_auto")
        switch.turn_off(entity_id=f"switch.pump_trigger") 


def cycle_zone(zone_number=None, action=None, enable_auto_pump= False, enable_bypass=False):
    """Function to execute actions on a sprinker zone with bypass valve and pump if enabled"""
    
    task.unique("cycle_zone", True)
    
    if action == "turn_on":
        switch.turn_on(entity_id=f"switch.sprinklers_channel_{zone_number}")
        if enable_auto_pump:
            auto_pump(action=action)
        if enable_bypass:
            bypass_valve(action=action)
        
    elif action == "turn_off":
        switch.turn_off(entity_id=f"switch.sprinklers_channel_{zone_number}")
        if enable_auto_pump:
            auto_pump(action=action)
        if enable_bypass:
            bypass_valve(action=action)
        
    log.debug(f"Zone {zone_number}: {action}")  
    
def master_off(reset_counter=False):
    """Switches off the whole system"""
    switch.turn_off(entity_id="switch.bypass_grid_valve")
    switch.turn_off(entity_id="switch.pump_auto")
    switch.turn_off(entity_id="switch.pump_trigger")
    for i in range (1,6):
        switch.turn_off(entity_id=f"switch.sprinklers_channel_{i}")
    log.debug(f"All outputs switched off") 
    
    if reset_counter:
        counter.reset(entity_id=f"counter.zone")
        
# Controller mode event
@event_trigger(EVENT_STATE_CHANGED, "entity_id=='input_select.controller_mode'")
def monitor_state_change(entity_id=None, new_state=None, old_state=None):
    
    log.debug(f"Sprinklers changed from {old_state.state} to {new_state.state}")
    
    z_index = int(counter.zone)
    enable_automation = bool(input_boolean.master_enable_sprinklers == 'on')
    enable_auto_pump = bool(input_boolean.enable_auto_pump == 'on')
    enable_bypass = bool(input_boolean.enable_bypass == 'on')
    
    if enable_automation: # Do logic only if automation enabled

        # [off->on]
        if old_state.state == 'off' and new_state.state == 'on':

            if z_index ==  0:
                counter.increment(entity_id=f"counter.zone")
            else:
                counter.reset(entity_id=f"counter.zone") 
                timer.cancel(entity_id=f"timer.zone") 
                counter.increment(entity_id=f"counter.zone")
                
        # [*->off]
        if new_state.state == 'off':
            master_off()
            counter.reset(entity_id=f"counter.zone") 
            timer.cancel(entity_id=f"timer.zone") 

        # [on->pause]
        if old_state.state == 'on' and new_state.state == 'pause':
            timer.pause(entity_id=f"timer.zone") 
        
        # [pause->on]
        if old_state.state == 'pause' and new_state.state == 'on':
            timer.start(entity_id=f"timer.zone") 

        
    else:
        counter.reset(entity_id=f"counter.zone")
        timer.cancel(entity_id=f"timer.zone") 
        input_select.select_option(entity_id=f"input_select.controller_mode", option='off')   
        

# Increased counter
@event_trigger(EVENT_STATE_CHANGED, "entity_id=='counter.zone'")
def zone_counter_state_change(entity_id=None, new_state=None, old_state=None):
    log.debug(f"Counter changed to {new_state.state}")
    z_index = int(counter.zone)
    
    if z_index == 0:
        master_off()
        return
    
    if z_index > zone_max:
        input_select.select_option(entity_id=f"input_select.controller_mode", option='off') 
        counter.reset(entity_id=f"counter.zone")
        return
        
    z_enabled = bool(state.get(f"input_boolean.enable_zone_{z_index}") == 'on')
    enable_auto_pump = bool(input_boolean.enable_auto_pump == 'on')
    enable_bypass = bool(input_boolean.enable_bypass == 'on')

    
    if z_enabled and state.get(f"input_datetime.zone_{z_index}") != "00:00:00":
        cycle_zone(zone_number=z_index, action='turn_on',
                   enable_auto_pump= enable_auto_pump, enable_bypass=enable_bypass)
        timer.start(entity_id=f"timer.zone", duration=state.get(f"input_datetime.zone_{z_index}"))
    else:
        counter.increment(entity_id=f"counter.zone")

        

# Finish timmer
@event_trigger("timer.finished", "entity_id=='timer.zone'")
def zone_timer_finished(entity_id=None):
    log.debug(f"Timer finished")
    
    z_index = int(counter.zone)
    enable_auto_pump = bool(input_boolean.enable_auto_pump == 'on')
    enable_bypass = bool(input_boolean.enable_bypass == 'on')
    
    cycle_zone(zone_number=z_index, action='turn_off',
               enable_auto_pump= False, enable_bypass=False)
        
    counter.increment(entity_id=f"counter.zone")

# Cancel timmer
@event_trigger("timer.cancelled", "entity_id=='timer.zone'")
def zone_timer_cancelled(entity_id=None):
    log.debug(f"Timer cancelled")
    master_off()
    input_select.select_option(entity_id=f"input_select.controller_mode", option='off') 
    counter.reset(entity_id=f"counter.zone")   
    

# Pause timmer
@event_trigger(EVENT_STATE_CHANGED, "entity_id=='timer.zone'")
def zone_timer_state_change(entity_id=None, new_state=None, old_state=None):
    log.debug(f"Timer changed from {old_state.state} to {new_state.state}")
    if old_state.state == 'active' and new_state.state == 'paused':
        master_off()
        input_select.select_option(entity_id=f"input_select.controller_mode", option='pause') 
        
    z_index = int(counter.zone)
    enable_auto_pump = bool(input_boolean.enable_auto_pump == 'on')
    enable_bypass = bool(input_boolean.enable_bypass == 'on')
    
    if old_state.state == 'paused' and new_state.state == 'active':
        input_select.select_option(entity_id=f"input_select.controller_mode", option='on') 
        cycle_zone(zone_number=z_index, action='turn_on', 
                enable_auto_pump= enable_auto_pump, enable_bypass=enable_bypass)
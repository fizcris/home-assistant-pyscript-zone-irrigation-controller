# home-assistant-pyscript-zone-irrigation-controller
---
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/fizcris)


This integration writen in pyscript for [Home Assistant](https://home-assistant.io/) and aims to automate a zone irrigation controller with special requirements as pauses and pump/bypass valve switches. 

The base automation from wich this pyscript automation can be found in [this topic](https://community.home-assistant.io/t/complex-automations-state-machine/335368/7).

---

<table>
    <tr>
        <td>
            <p style="text-align: center;">Original image</p>
            <img src="resources/ui.gif" alt="cal_images" width="300" />
        </td>
    </tr>
</table>

## Automation Requirements
 + A master switch need to be enabled for the automation to start.

 + When the system is enabled, it begins stepping through each one of the 5 zones.

+ If a zone’s associated input_boolean is enabled, its corresponding switch is turned on for the duration specified by the zone’s associated input_number. A timer performs the countdown.

+ If the enable switch is turned on for the bypass valve the correspondent switch would be active as long as one zone is active.

+ If the enable switch is turned on for the pump valve the correspondent switch and pump trigger switch will be active as long as one zone is active.

+ If the zone is disabled, the system simply skips to the next zone.
When the timer finishes, the zone’s switch is turned off, and the system proceeds to process the next zone.

+ After all enabled zones are processed, the system is set to off.

+ At any time during its processing, the system may be paused. The current zone’s switch is turned off (also the bypass switch and pump switches if enabled) and the timer is paused. Re-enabling the system causes it to pick up from where it paused (i.e. switch is turned back on and timer continues to countdown the balance of its duration).

+ At any time during its processing, the system may be disabled. This causes it to cancel the timer and turn off all switches.
---

## External libraries required
- [pyscript](https://github.com/custom-components/pyscript)
- [button-card](https://github.com/custom-cards/button-card)
---

## Installation
***

### Create Entities
Copy the contents of `entities_zone.yaml` into your `configuration.yaml` or link it using one of the advanced linking methods. I personally use `packages: !include_dir_named integrations` in my `configuration.yaml` file and then place the file into `integrations/entities_zone.yaml`.

**Entities summary**:
+ One **timer** to countdown a zone’s duration.
+ One **counter** to keep track of which zone to process.
+ One **input_select** to control overall operation (on/off/pause).
+ Five **input_booleans**, one per zone to indicate its enabled/disabled status.
+ Five **input_datetimes**, one per zone to indicate its duration (in hours and minutes).
+ One **input_boolean** to enable/disable bypass valve
+ Two **input_booleans** to enable/disable and trigguer pump
***
### Lovelace UI
Copy the contents of `lovelace.yaml` into an empty `vertical-stack` card on your lovelace UI.

Be aware thah the library [button-card](https://github.com/custom-cards/button-card) is required beforehand.
***
### Pyscript automation
Copy the `sprinklers.py` file into `pyscript/apps/sprinklers.py` and add 

```
allow_all_imports: true
hass_is_global: true
apps:
  sprinklers:
```
to your pyscript config.yaml file. Be aware to follow the [instructions](https://hacs-pyscript.readthedocs.io/en/latest/configuration.html) to avoid missconfigurations as apps are not possible to be add from the pyscript integration UI.

### Extra comments

I personally use the [scheduler-component](https://github.com/nielsfaber/scheduler-component) to create scheduled triggers for the zone controller.

It is also desirable to modify the logger output in your `configuration.yaml` file while developing the automation:
```
logger:
  default: info
  logs:
    homeassistant.components.pyscript: debug
```


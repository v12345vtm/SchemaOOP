from OOPschema import *

mod = DomoModule("0.0", 4, "relay")
mod.channels[0] = "Just a string"
mod.channels[1] = 123
mod.channels[2] = DomoRelay(channelid=2)
mod.channels[3] = {"custom": "dict"}

print(mod.as_dict())

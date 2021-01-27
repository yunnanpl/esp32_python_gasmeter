#-### config for offsets

# measurement start date, in struct_time type
voffdate = ( 2021, 1, 15, 0, 0, 0, 0, 0, 0 )
# following line works with time module, used later
#vofftime = int(time.mktime(voffdate))
offset = 999.52

# gas counter resolution
# in case of resolution of 0.1, the counter sends one signal up and one down
# to make counting nicer, it counts each signal as half of the resolution
resolution = 0.05

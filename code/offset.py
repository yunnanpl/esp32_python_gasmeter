#-### config for offsets

#-###
#-### start date for measurement, in struct_time type
#-### should start at midnight
voffdate = ( 2021, 1, 15, 0, 0, 0, 0, 0, 0 )

#-###
#-###
#-### value on meter, to calculate current value
offset = 999.62

#-### gas counter resolution
#-### in case of resolution of 0.1, the counter sends one signal up and one down
#-### to make counting nicer, it counts each signal as half of the resolution
vresolution = 0.05

#-###
#-### gas energy, assumed 10 kWh per 1 m^2
#-### can vary usually from 9 to 11
venergy = 10

#-### Done here
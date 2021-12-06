# select all 
# copy paste into the R console
# use as described in examples
#
# Assumptions 
# -----------
# 			Assumes you start your sessions sitting, however,
# 			you can just do the opposite, or any activity for 
# 			that matter!
#
# Limitations 
# -----------
# 			 1. need to keep R up and running
# 			 2. cannot easily kill process (use task manager)
# 
# Example Run 1
# -------------
# to sit for 45 mins and stand for 10 mins, 3 times
# simply write:
#
# > run()
#
# that uses the default values (you can change them)
#
# Example Run 2
# -------------
# to sit for 15 mins and stand for 5 mins, 1 time
# write:
#
# > run(15, 5, 1)
#
# You can change the type of beeps (see comments)

rm(list=ls())
library('beepr')

# DEFAULTS VALUES ---------- change as desired!
num_times_beeps_repeat = 4
secs_between_beeps = 1.5 
default_sit_mins = 45
default_stand_mins = 10
default_times = 3

make_sound <- function(sound) {
	# BEEP SOUNDS
	# -----------
	# helper fuction to choose a sound 
	# options are: 
	# "ping", "coin", "sword", "fanfare", "facebook",
	# "complete", "treasure", "ready", "shotgun",
	# "mario", "wilhelm"
	# for a random sound issue: 
	# beep(0)
	for (i in 1:num_times_beeps_repeat) {
		beep(sound) 
		Sys.sleep(secs_between_beeps)
	}
}

run <- function(sit_mins = default_sit_mins, 
				stand_mins = default_stand_mins, 
				num = default_times) {
	
	# convert from minutes to seconds
	sit_secs <- 60*sit_mins
	stand_secs <- 60*stand_mins
	
	# iterate num times
	for (i in 1:num) {
		# long wait 
		Sys.sleep(sit_secs)
		# standup sound 
		make_sound("ping") # <-------- CHANGE STANDUP BEEP 
		# short wait 
		Sys.sleep(stand_secs)
		# sitdown sound
		make_sound("coin") # <---------- CHANGE SITDOWN BEEP 
	}
}
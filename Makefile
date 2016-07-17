#!/usr/bin/env make

# proof-of-concept GNU Make equivalent of SConstruct file.
# expands combinatoric parameter space into nested directory steructure

SANTAJAR := santa-sim/target/santa-sim-0.0.1-SNAPSHOT.jar
SANTACONFIG := santa-sim/examples/small-indel.xml
SEED:=1465407525161

population := 1000 2000 3000 4000 5000 10000 50000 100000
generations := 500 700 1000 10000

# use nested $(foreach) loops to expand combinations of parameters
dirs:=$(foreach p1,$(population),$(foreach p2,$(generations),output/pop$(p1)/gen$(p2)))

%.out : population=$(subst pop,,$(wordlist 2,2,$(subst /, ,$@)))
%.out : generation=$(subst gen,,$(wordlist 3,3,$(subst /, ,$@)))

%.config : $(SANTACONFIG)
	mkdir -p $(dir $@) && cp $(SANTACONFIG) $@

%.out : %.config
	java -mx512m -Djava.util.logging.config.file="logging.properties" -jar ${SANTAJAR} -population=${population} -samplesize=10 -generations=${generation} -seed=${SEED} $^ >$@ 2>&1'

# build all things!
all: $(foreach dir,$(dirs),$(dir)/santa.out)

.PHONY: all
.PRECIOUS: %.config




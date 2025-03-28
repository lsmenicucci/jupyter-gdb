BUILD_DIR=./build

build_dir:
	mkdir -p $(BUILD_DIR)


$(BUILD_DIR)/%: samples/%.f90 build_dir
	gfortran -g -O0 $< -o $@

shell:
	docker exec -it jupyter bash

.PHONY: shell

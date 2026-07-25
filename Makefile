# K(5,5) geodesic labeling — handoff entry points
J ?= 12

.PHONY: test cnf cubes run-cubes cpsat clean

test:
	python3 generate_cnf.py --selftest

cnf:
	python3 generate_cnf.py --n 5 -o k55.cnf

cubes:
	python3 generate_cnf.py --n 5 -o k55.cnf --cubes

# solve all 100 cubes, $(J) in parallel; logs in cubes-out/
run-cubes: cubes
	mkdir -p cubes-out
	i=0; \
	head -1 k55.cnf > /dev/null; \
	vars=$$(sed -n '2s/p cnf \([0-9]*\) .*/\1/p' k55.cnf); \
	cls=$$(sed -n '2s/p cnf [0-9]* \([0-9]*\)/\1/p' k55.cnf); \
	while read lit; do \
	  i=$$((i+1)); \
	  ( printf 'p cnf %s %s\n' "$$vars" "$$((cls+1))"; \
	    tail -n +3 k55.cnf; \
	    printf '%s 0\n' "$$lit" ) > cubes-out/cube_$$i.cnf; \
	done < cubes.txt; \
	ls cubes-out/cube_*.cnf | xargs -P $(J) -I{} sh -c \
	  'kissat -q {} > {}.log; echo "{}: $$(grep -o "^s .*" {}.log)"' \
	  | tee cubes-out/summary.txt; \
	echo "---"; \
	grep -c "s UNSATISFIABLE" cubes-out/summary.txt || true; \
	grep "s SATISFIABLE" cubes-out/summary.txt || echo "no SAT cube yet"

cpsat:
	python3 cpsat_run.py --workers $(J)

clean:
	rm -rf k55.cnf k22.cnf cubes.txt cubes-out solution.txt *.log *.drat

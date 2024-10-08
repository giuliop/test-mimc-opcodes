.PHONY: all compile test

# Default action if no specific target is provided
all: compile test

# Output files
MIMC = contract/mimc.approval.teal

# Compile the mimc contract if mimc.py has changed
$(MIMC): contract/mimc.py
	@echo "Compiling contract/mimc.py"
	algokit compile py contract/mimc.py

	# substitute (pragma) 'version 10' with 'version 11' in teal files
	perl -i -pe 's/version 10/version 11/g' contract/mimc.approval.teal
	perl -i -pe 's/version 10/version 11/g' contract/mimc.clear.teal

	@echo ""
	# substitute 'sha256' with 'mimc BN254g1' in mimc.approval.teal
	perl -i -pe 's/sha256/mimc BN254_MP_110/g' contract/mimc.approval.teal

	@echo ""
	# substitute 'keccak256' with 'mimc BLS12_381g1' in mimc.approval.teal
	perl -i -pe 's/keccak256/mimc BLS12_381_MP_111/g' contract/mimc.approval.teal

compile: $(MIMC)

test:
	@echo "\nRunning main.py"
	pipenv run python main.py

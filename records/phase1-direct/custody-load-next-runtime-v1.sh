set -e
source /home/sicarii/opt/gnat/env.sh
export GPR_PROJECT_PATH="$PWD/scratch/phase1-direct/private-sparklib/lib/gnat:$GPR_PROJECT_PATH"
export WORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True PYTHONPATH=runtime:tests
python refresh_contract_pins.py --check
python tests/generate_custody_load_fixtures.py
gprbuild -p -j2 -P tests/custody_load_contracts.gpr -XWORLDLINE_BUILD=checks -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True -cargs:Ada -fPIC
./bin/custody-load-contracts/custody_load_extras_tests tests/custody_load_extras.json tests/custody_load_extras_digest.json
./bin/custody-load-contracts/custody_load_decode_tests tests/custody_load_empty.json 0 maximum
./bin/custody-load-contracts/custody_load_decode_tests tests/custody_load_populated.json 1 maximum

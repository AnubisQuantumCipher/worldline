set -e
source /home/sicarii/opt/gnat/env.sh
export GPR_PROJECT_PATH="$PWD/scratch/phase1-direct/private-sparklib/lib/gnat:$GPR_PROJECT_PATH"
export WORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True WORLDLINE_CORE_LIB="$PWD/lib/libworldline_core.so" PYTHONPATH=runtime:tests
python refresh_contract_pins.py --check
for project in worldline.gpr tests/custody_load_contracts.gpr; do
 gprbuild -p -j2 -P "$project" -XWORLDLINE_BUILD=checks -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True -cargs:Ada -fPIC
done
python tests/generate_custody_load_fixtures.py
./bin/custody-load-contracts/custody_load_extras_tests tests/custody_load_extras.json tests/custody_load_extras_digest.json
./bin/worldline_core_tests
./bin/worldline_core_fuzz
python -m unittest -v test_custody_native_guard test_custody_prepared_abi test_custody_v2_explicit_provision test_custody_provision_kernel test_custody_v2_sql_capture test_custody_foreign_key_capture test_root_worker_codec_lossless

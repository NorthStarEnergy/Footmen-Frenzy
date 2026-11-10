# Test maps

Each family folder holds verified, versioned Warcraft III test maps in Git LFS. The shared build publishes the installed map to this folder on the origin remote's main branch. For each new test, the same Git push commits the packed editable source under projects/<project>/src on the branch named in project.json. The adjacent .source.json file records that commit and the map SHA-256. Use -LocalOnly for a build without publication. Use Git LFS when cloning to obtain the playable binaries.

If the upload fails after local installation, retry with the same build report and output using `python tools/publish_test_map.py 799x "FF799X_example_v99_TEST.w3x"`. Use the project and filename from your build. A different map with the same filename requires a new version.

# History

## 0.6.0 (2024-10-28)
- Add forging of algorithm templates.
- Split CLI commands into 'pack' for challenge packs and 'algorithm' for algorithm templates.

## 0.5.0 (2024-10-10)
- Fixed interoperability issues when running challenge pack scripts on macOS.
- Fixed several Docker deprecation warnings.
- Added examples for file inputs.
- Reworked multithreading in example evaluation methods:
  - Used concurrent.futures.ProcessPoolExecutor.
  - Dynamically limited the number of workers in evaluation methods (via multiprocessing.cpu_count()).
  - Introduced a controller thread.
- Silenced Docker volume shell calls.
- Mounted a dummy /tmp to test scripts, preventing final containers that users might build.
- Challenge packs now include a proper .gitignore.
- Added a save.sh script to Docker-based examples to demonstrate how to export a Docker image.
- Ensured Docker file-mounted inputs are read-only.
- Dist challenge packs under the Apache License 2.0.

## 0.4.0 (2023-01-22)
* Stop using '/tmp' in example Dockerfiles to contain non-transient files.

## 0.3.0 (2023-01-08)
* Replace "input"/"output" in the context JSON input with "algorithm_input"/"algorithm_output".

## 0.2.2 (2023-01-02)
* Various improvements to spelling and wording in the challenge packs
* Report grand-challenge-forge version in generated pack README
* Use challenge-level archives instead of phase-level archives for the pack README
* Add support for reading and writing TIFF files
* Disable network in test runs

## 0.2.1 (2023-12-15)
* Various improvements to spelling and comments in the challenge packs
* Fixed passing `'is_image'`, `'is_json'` to the prediction.json example of the evaluation method
* Added a generic `read_file()` / `write_file()` to the evaluation.py and inference.py of the algorithm and evaluation examples, respectively

## 0.2.0 (2023-12-14)

* Adds challenge packs, consisting of:
  * example upload algorithm
  * example submission algorithm
  * example evaluation method

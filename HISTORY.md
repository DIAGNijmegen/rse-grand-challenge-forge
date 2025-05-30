# History


# 0.7.4 (2025-05-30)
- Reduce the length of some paths found in rendered templates directory structures.

# 0.7.3 (2025-04-25)
- Fix CLI assuming zpath was returned.


## 0.7.2 (2025-04-24)
- Fix CLI construct causing errors in release: the zipfile wrapper is not in a module that is release accessible.

## 0.7.1 (2025-04-18)
- Fix DEBUG construct causing errors in release

## 0.7.0 (2025-04-18)
 - Improve error reporting for evaluation methods
 - Upgrade Python version and minor fixes
 - Evaluation ground truth and algorithm models tar balls
 - Add a now what section to the pack README
 - Remove redundant permission docker run
 - Fix escaping string example values
 - Remove quality assurance tests that run post-generation
 - [Breaking] Internally generate to ZipFile-handle
 - [Breaking] Templates now handle algorithm interfaces

## 0.6.1 (2024-10-31)

- Fix not using algorithm URL correctly in README
- Use valid examples for JSON-like inputs/outputs
- Fix permissions not always being restored correctly when running on latest Ubuntu LTS
- Ensure .tif are correctly parsed by example scripts

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

- Stop using '/tmp' in example Dockerfiles to contain non-transient files.

## 0.3.0 (2023-01-08)

- Replace "input"/"output" in the context JSON input with "algorithm_input"/"algorithm_output".

## 0.2.2 (2023-01-02)

- Various improvements to spelling and wording in the challenge packs

- Report grand-challenge-forge version in generated pack README
- Use challenge-level archives instead of phase-level archives for the pack README
- Add support for reading and writing TIFF files
- Disable network in test runs

## 0.2.1 (2023-12-15)

- Various improvements to spelling and comments in the challenge packs

- Fixed passing `'is_image'`, `'is_json'` to the prediction.json example of the evaluation method
- Added a generic `read_file()` / `write_file()` to the evaluation.py and inference.py of the algorithm and evaluation examples, respectively

## 0.2.0 (2023-12-14)

- Adds challenge packs, consisting of:
- example upload algorithm
- example submission algorithm
- example evaluation method
